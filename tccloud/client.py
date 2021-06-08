from typing import Dict, List, Optional, Union

from . import __version__
from .config import settings
from .http_client import _RequestsClient
from .models import (
    AtomicInputOrList,
    FutureResult,
    FutureResultGroup,
    OptimizationInputOrList,
)


class TCClient:
    """Main client object to perform computations using TeraChem Cloud."""

    def __init__(
        self,
        *,
        tccloud_username: Optional[str] = None,
        tccloud_password: Optional[str] = None,
        profile: Optional[str] = None,
        tccloud_domain: Optional[str] = None,
    ):
        """
        Initialize a TCClient object.

        Parameters:
            tccloud_username: TeraChem Cloud username
            tccloud_password: TeraChem Cloud password
            profile: Authentication profile name
            tccloud_domain: Domain of TeraChem Cloud instance to connect to

        !!! Danger
            It is not recommended to pass your TeraChem Cloud username and password
            directly to a `TCClient`. Instead instantiate a client with no credentials
            `client = TCClient()` and then run `client.configure()` to securely set up
            your authentication credentials for TeraChem Cloud.
        """
        self._client = _RequestsClient(
            tccloud_username=tccloud_username,
            tccloud_password=tccloud_password,
            profile=profile,
            tccloud_domain=tccloud_domain,
        )
        self._openapi_spec: Optional[Dict] = None

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._client._tccloud_domain}, profile={self.profile})"

    def _set_openapi_specification(self):
        """Gets OpenAPI specification from TeraChem Cloud Server"""
        self._openapi_spec = self._client._request(
            "get", "/openapi.json", api_call=False
        )

    @property
    def version(self) -> str:
        """Return tccloud version"""
        return __version__

    @property
    def profile(self) -> str:
        """Profile being used for authentication with TeraChem Cloud.

        Returns:
            The name of the name of the credentials profile being used with
            the current client.

        NOTE: This is a note!
        """
        return self._client._profile

    @property
    def supported_engines(self) -> List[str]:
        """Compute engines currently supported by TeraChem Cloud.

        Returns:
            List of engines currently supported by TeraChem Cloud."""
        if not self._openapi_spec:
            self._set_openapi_specification()
        try:
            assert self._openapi_spec is not None
            engines = self._openapi_spec["components"]["schemas"]["SupportedEngines"][
                "enum"
            ]
        except IndexError:
            print("Cannot locate currently supported engines.")
            engines = [""]
        return engines

    @property
    def supported_procedures(self) -> List[str]:
        """Compute procedures currently supported by TeraChem Cloud.

        Returns:
            List of procedures currently supported by TeraChem Cloud."""
        if not self._openapi_spec:
            self._set_openapi_specification()
        try:
            assert self._openapi_spec is not None
            procedures = self._openapi_spec["components"]["schemas"][
                "SupportedProcedures"
            ]["enum"]
        except IndexError:
            print("Cannot locate currently supported procedures.")
            procedures = [""]
        return procedures

    def hello_world(self, name: Optional[str] = None) -> str:
        """A simple endpoint to check connectivity to TeraChem Cloud.

        Parameters:
            name: Your name

        Returns:
            A message from TeraChem Cloud if the client was able to successfully
            connect.
        """
        return self._client.hello_world(name)

    def compute(
        self, input_data: AtomicInputOrList, engine: str, queue: Optional[str] = None
    ) -> Union[FutureResult, FutureResultGroup]:
        """Submit a computation to TeraChem Cloud.

        Parameters:
            input_data: Defines the structure of the desired computation.
            engine: A string matching one of the `self.supported_engines`
            queue: The name of a private compute queue. If None, default queue is used

        Returns:
            Object providing access to a computation's eventual result. You can check a
            computation's status by runing `.status` on the `FutureResult` object or
            `.get()` to block and retrieve the computation's final result.
        """
        if self.supported_engines is not None:
            assert (
                engine in self.supported_engines
            ), f"Please use one of the following engines: {self.supported_engines}"

        return self._client.compute(input_data, engine, queue)

    def compute_procedure(
        self,
        input_data: OptimizationInputOrList,
        procedure: str,
        queue: Optional[str] = None,
    ) -> Union[FutureResult, FutureResultGroup]:
        """Submit a procedure computation to TeraChem Cloud

        Parameters:
            input_data: Defines the inputs for an optimization computation
            procedure: The name of the procedure, e.g., 'berny'
            queue: The name of a private compute queue. If None, default queue is used

        Returns:
            Object providing access to a computation's eventual result. You can check a
            computation's status by runing `.status` on the `FutureResult` object or
            `.get()` to block and retrieve the computation's final result.
        """
        if self.supported_procedures is not None:
            assert (
                procedure in self.supported_procedures
            ), f"Please use one of the following procedures: {self.supported_procedures}"
        return self._client.compute_procedure(input_data, procedure, queue)

    def configure(
        self, profile: str = settings.tccloud_default_credentials_profile
    ) -> None:
        """Configure profiles for authentication with TeraChem Cloud.

        Parameters:
            profile: Optional value to create a named profile for use with TeraChem
                Cloud. No value needs to be passed and most users will only have one
                login with TeraChem Cloud. TCClient will access the profile by
                default without a specific name being passed. Pass a value if you have
                multiple logins to TeraChem Cloud.
        Note:
            Configures `tccloud` to use the passed credentials automatically in the
            future. You will not need to run `.configure()` the next time you use the
            `tccloud`.

        """
        print(
            f"✅ If you don't get have an account please signup at: {settings.tccloud_domain}/signup"
        )
        access_token, refresh_token = self._client._set_tokens_from_user_input()
        self._client.write_tokens_to_credentials_file(
            access_token, refresh_token, profile=profile
        )
        print(
            f"'{profile}' profile configured! Username/password not required for future use of TCClient"
        )
