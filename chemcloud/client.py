import logging
from typing import Any, Optional, Union

from qcio import InputType, ProgramOutput
from typing_extensions import TypeAlias

from . import __version__
from .config import Settings, settings
from .exceptions import UnsupportedProgramError
from .http_client import _HttpClient
from .models import FutureOutput, TaskStatus

logger = logging.getLogger(__name__)

QCIOInputsOrList: TypeAlias = Union[InputType, list[InputType]]


class CCClient:
    """
    Main client object to perform computations using ChemCloud.

    Parameters:
        chemcloud_username: Your ChemCloud username (full email address).
        chemcloud_password: Your ChemCloud password.
        profile: A named profile for authentication with ChemCloud. No value needs to be
            passed and most users will only have one login with ChemCloud. CCClient will
            access the profile by default without a specific name being passed. Pass a
            value if you have multiple logins to ChemCloud.
        chemcloud_domain: The domain for the ChemCloud server. Defaults to
            https://chemcloud.mtzlab.com.
        settings: An instance of the Settings class. Defaults to the global settings
            object.
        queue: The name of a desired compute queue. If None, default queue is used from
            settings.

    Responsibilities:
      - Expose domain-specific methods (e.g., compute, output) that operate with Python objects.
      - Translate raw JSON responses into domain objects (e.g., FutureOutput).
      - Handle OpenAPI specification caching, parameter validation, etc.
    """

    def __init__(
        self,
        *,
        chemcloud_username: Optional[str] = None,
        chemcloud_password: Optional[str] = None,
        profile: Optional[str] = None,
        chemcloud_domain: Optional[str] = None,
        settings: Settings = settings,
        queue: Optional[str] = None,
    ):
        self._http_client = _HttpClient(
            chemcloud_username=chemcloud_username,
            chemcloud_password=chemcloud_password,
            profile=profile,
            chemcloud_domain=chemcloud_domain,
            settings=settings,  # Assume settings is injected here
        )
        self.queue = queue
        self._settings = settings
        self._openapi_spec: Optional[dict[str, Any]] = None

    @property
    def profile(self) -> str:
        return self._http_client._profile

    @property
    def version(self) -> str:
        """Returns chemcloud client version"""
        return __version__

    @property
    def supported_programs(self) -> list[str]:
        """Compute programs currently supported by ChemCloud.

        Returns:
            List of programs currently supported by ChemCloud."""
        try:
            programs = self.openapi_spec["components"]["schemas"]["SupportedPrograms"][
                "enum"
            ]
        except (KeyError, IndexError):
            logger.warning("Cannot locate currently supported programs.")
            programs = [""]
        return programs

    @property
    def openapi_spec(self) -> dict[str, Any]:
        """Gets OpenAPI specification from ChemCloud Server"""
        if self._openapi_spec is None:
            self._openapi_spec = self._http_client.run_parallel_requests(
                [
                    self._http_client._request_async(
                        "get", "/openapi.json", api_call=False
                    )
                ]
            )[0]
        return self._openapi_spec

    def compute(
        self,
        program: str,
        inp_obj: QCIOInputsOrList,
        *,
        collect_stdout: bool = True,
        collect_files: bool = False,
        collect_wfn: bool = False,
        rm_scratch_dir: bool = True,
        propagate_wfn: bool = False,
        queue: Optional[str] = None,
        return_future: bool = False,
    ) -> Union[ProgramOutput, list[ProgramOutput], "FutureOutput"]:
        """Submit a computation to ChemCloud.

        Parameters:
            program: A program name matching one of the self.supported_programs
            inp_obj: The input object to be used for the computation. This can be a
                single input object or a list of input objects.
            collect_stdout: Whether to collect stdout/stderr from the program as output.
                Failed computations will always collect stdout/stderr.
            collect_files: Collect all files generated by the QC program as output.
            collect_wfn: Collect the wavefunction file(s) from the calculation.
                Not every program will support this. Use collect_files to collect
                all files including the wavefunction.
            rm_scratch_dir: Delete the scratch directory after the program exits. Should
                only be set to False for debugging purposes.
            propagate_wfn: For any adapter performing a sequential task, such
                as a geometry optimization, propagate the wavefunction from the previous
                step to the next step. This is useful for accelerating convergence by
                using a previously computed wavefunction as a starting guess. This will
                be ignored if the adapter for a given qc program does not support it.
            queue: The name of a private compute queue. If None, default queue is used
                from settings.
            return_future: If True, return a FutureOutput object. If False, block and
                return the ProgramOutput object(s) directly.


        Returns:
            Object providing access to a computation's eventual result. You can check a
            computation's status by running .status on the FutureOutput object or
            .get() to block and retrieve the computation's final result.
        """
        if not inp_obj:
            raise ValueError("Please provide input objects for the computation.")

        logger.info(
            f"Submitting compute job for program {program} with inputs {inp_obj}."
        )

        if program not in self.supported_programs:
            raise UnsupportedProgramError(
                f"Please use one of the following programs: {self.supported_programs}"
            )

        url_params = dict(
            program=program,
            collect_stdout=collect_stdout,
            collect_files=collect_files,
            collect_wfn=collect_wfn,
            rm_scratch_dir=rm_scratch_dir,
            propagate_wfn=propagate_wfn,
            queue=queue or self.queue or self._settings.chemcloud_queue,
        )

        if not isinstance(inp_obj, list):
            inp_objs = [inp_obj]
        else:
            inp_objs = inp_obj

        # Create a list of coroutines to submit each compute request.
        coroutines = [
            self._http_client._authenticated_request_async(
                "post", "/compute", data=inp, params=url_params
            )
            for inp in inp_objs
        ]

        # Use the HTTP client's parallel runner with the desired concurrency.
        task_ids = self._http_client.run_parallel_requests(coroutines)
        future = FutureOutput(
            task_ids=task_ids,
            inputs=inp_objs,
            single_input=not isinstance(inp_obj, list),
            program=program,
            client=self,
        )
        if return_future:
            return future
        return future.get()

    def fetch_output(
        self, task_id: str
    ) -> tuple[TaskStatus, Optional[Union[ProgramOutput, list[ProgramOutput]]]]:
        """
        Synchronously fetch the output for a single task.
        """
        # Run the asynchronous authenticated request synchronously.
        return self._http_client.run_parallel_requests(
            [self.fetch_output_async(task_id)]
        )[0]

    async def fetch_output_async(
        self, task_id: str
    ) -> tuple[TaskStatus, Optional[ProgramOutput]]:
        """
        Perform an authenticated request to check the status and output for a single task.

        Parameters:
            task_id: The ID of the task to check.

        Returns:
            A tuple of the task status and the output object if available.
        """
        response = await self._http_client._authenticated_request_async(
            "get", f"/compute/output/{task_id}"
        )
        status = TaskStatus(response.get("status", TaskStatus.PENDING))
        output = response.get("program_output")
        if output is not None:
            output = ProgramOutput(**output)
        return status, output

    def hello_world(self, name: Optional[str] = None) -> str:
        """A simple endpoint to check connectivity to ChemCloud.

        Parameters:
            name: Your name

        Returns:
            A message from ChemCloud if the client was able to successfully
            connect.
        """
        logger.info(f"Sending hello_world request with name: {name}")

        # Run a single asynchronous request synchronously via run_parallel_requests.
        return self._http_client.run_parallel_requests(
            [
                self._http_client._request_async(
                    "get", "/hello-world", params={"name": name}, api_call=False
                )
            ]
        )[0]

    def setup_profile(self, profile: Optional[str] = None) -> None:
        """Setup profiles for authentication with ChemCloud.

        Parameters:
            profile: Optional value to create a named profile for use with QC
                Cloud. No value needs to be passed and most users will only have one
                login with ChemCloud. CCClient will access the profile by
                default without a specific name being passed. Pass a value if you have
                multiple logins to ChemCloud.
        Note:
            Configures `chemcloud` to use the passed credentials automatically in the
            future. You only need to run this method once per profile. Credentials will
            be loaded automatically from the credentials file in the future.
        """
        profile = profile or self._settings.chemcloud_credentials_profile
        print(
            f"✅ If you don't have an account, please signup at: {self._http_client._chemcloud_domain}/signup"
        )
        # Use the async _set_tokens_from_user_input wrapped via run_parallel_requests
        access_token, refresh_token = self._http_client.run_parallel_requests(
            [self._http_client._set_tokens_from_user_input()]
        )[0]
        self._http_client.write_tokens_to_credentials_file(
            access_token, refresh_token, profile=profile
        )
        print(
            f"'{profile}' profile configured! Username/password not required for future use."
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._http_client._chemcloud_domain}, profile={self.profile})"
