import asyncio
import json
import logging
import traceback
from collections.abc import AsyncGenerator, Generator
from enum import Enum
from pathlib import Path
from time import sleep, time
from typing import TYPE_CHECKING, Any, Optional, Union, cast
from uuid import uuid4

from httpx import HTTPError
from pydantic import BaseModel, field_validator, model_validator
from qcio import Files, Inputs, ProgramOutput
from typing_extensions import Self

from .exceptions import TimeoutError

# Option 1: Use TYPE_CHECKING for static type hints.
if TYPE_CHECKING:
    from .client import CCClient

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Tasks status for a submitted compute job"""

    # States from https://github.com/celery/celery/blob/master/celery/states.py

    #: Task state is unknown (assumed pending since you know the id).
    PENDING = "PENDING"
    #: Task was received by a worker (only used in events).
    RECEIVED = "RECEIVED"
    #: Task was started by a worker (:setting:`task_track_started`).
    STARTED = "STARTED"
    #: Task succeeded
    SUCCESS = "SUCCESS"
    #: Task failed
    FAILURE = "FAILURE"
    #: Task was revoked.
    REVOKED = "REVOKED"
    #: Task was rejected (only used in events).
    REJECTED = "REJECTED"
    #: Task is waiting for retry.
    RETRY = "RETRY"
    IGNORED = "IGNORED"


READY_STATES = {TaskStatus.SUCCESS, TaskStatus.FAILURE, TaskStatus.REVOKED}


class FutureOutput(BaseModel):
    """
    Represents one or more asynchronous compute tasks.

    Developer Note:
        Rather than refactoring into a `BaseFutureOutput` with `FutureOutput` and
        `FutureOutputs` subclass, we use the `return_single_output` flag to determine
        when the `.get()` method should return a `ProgramOutput` or
        `list[ProgramOutput]` and when to enable the `.task_id` attribute. This
        simplifies the API, reduces code complexity, removes the need for `isinstance`
        checks, and still gives the same end user experience. We can rethink this design
        if it becomes an issue.


    Attributes:
        task_ids: A list of task IDs from a compute submission.
        input_data: A list of input data objects for each task.
        program: The program used for the computation.
        client: A `CCClient` instance that can perform HTTP requests to check task status.
        return_single_output (bool): If True, indicates that the `.get()` method will
            return a single ProgramOutput rather than a list. Also enables the
            `.task_id` property.
        outputs: A list of ProgramOutputs once tasks are completed (order
            corresponds to task_ids). Generally not passed by the user, but used
            internally to track task outputs.

        statuses: A list of TaskStatus enums corresponding to the status of each task.
            Generally not passed by the user, but used internally to track task status.
    """

    task_ids: list[str]
    inputs: list[Inputs]
    program: str
    client: Any
    outputs: list[Optional[ProgramOutput]] = []
    return_single_output: bool = False
    statuses: list[TaskStatus] = []

    model_config = {
        # Raises an error if extra fields are passed to model.
        "extra": "forbid",
        # For client
        # https://docs.pydantic.dev/latest/usage/types/#arbitrary-types-allowed
        "arbitrary_types_allowed": True,
    }

    @field_validator("client", mode="before")
    def _instantiate_client(cls, v: Union["CCClient", dict[str, Any]]) -> "CCClient":
        """
        If 'client' is provided as a dict, assume it is the serialized configuration
        and instantiate a CCClient from it. This enables .open() to work correctly.
        """
        if isinstance(v, dict):
            from chemcloud import CCClient

            try:
                return CCClient(**v)
            except Exception as exc:
                raise ValueError(
                    f"Error instantiating client from serialized data: {v}."
                ) from exc
        return v

    @model_validator(mode="after")
    def _initialize_outputs_and_statuses(self) -> Self:
        """Initialize program_outputs and statuses based on task_ids length."""
        if not self.outputs:
            self.outputs = [None] * len(self.task_ids)
        if not self.statuses:
            self.statuses = [TaskStatus.PENDING] * len(self.task_ids)
        return self

    @model_validator(mode="after")
    def _ensure_single_input(self) -> Self:
        """Ensure that return_single_output is only set for a single task submission."""
        if self.return_single_output and len(self.task_ids) != 1:
            raise ValueError(
                "return_single_output=True is only valid for a single task submission."
            )
        return self

    @property
    def task_id(self) -> str:
        """Return the task id if only a single computation was submitted."""
        if not self.return_single_output:
            raise AttributeError("Tasks submitted as a list. Use `task_ids` instead.")
        return self.task_ids[0]

    async def refresh_async(self) -> None:
        """Refresh the status and output for uncollected tasks."""
        logger.debug("Refreshing task statuses and outputs.")

        # Identify unfinished tasks
        assert self.statuses is not None  # For mypy
        unfinished_indices = [
            i for i, status in enumerate(self.statuses) if status not in READY_STATES
        ]
        if not unfinished_indices:
            logger.debug("No unfinished tasks to refresh.")
            return  # Nothing to refresh

        # Build coroutines to refresh unfinished tasks
        coroutines = [
            self.client.fetch_output_async(self.task_ids[i]) for i in unfinished_indices
        ]
        # Run the coroutines in parallel; collect statues and results.
        logger.info(f"Refreshing {len(unfinished_indices)} unfinished task(s).")
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # Update statuses and outputs based on results
        for i, result in zip(unfinished_indices, results):
            # Insulate users against all HTTP errors
            if isinstance(result, HTTPError):
                logger.error(
                    f"Error collecting task {self.task_ids[i]}: {result}", exc_info=True
                )
                self.statuses[i] = TaskStatus.FAILURE
                self.outputs[i] = self._output_from_exception(result, self.inputs[i])
            else:
                assert (
                    isinstance(result, tuple) and len(result) == 2
                ), "Invalid result returned."
                logger.debug(f"Task {self.task_ids[i]} collected: status {result[0]}")
                self.statuses[i], self.outputs[i] = result

    def refresh(self):
        """Sync wrapper around `refresh_async`."""
        return self.client.run(self.refresh_async())

    async def get_async(
        self, timeout: Optional[float] = None, initial_interval: float = 1.0
    ) -> Union[ProgramOutput, list[ProgramOutput]]:
        """
        Block until all tasks complete and return their ProgramOutputs.

        If only one task was submitted, returns the single result;
        otherwise, returns a list of program_outputs.

        Parameters:
            timeout: The maximum time to wait for all tasks to complete.
            initial_interval: The initial interval between status checks.

        Returns:
            The ProgramOutput objects for all tasks once they are complete.

        Raises:
            TimeoutError: If the timeout is exceeded before all tasks complete.
        """
        start = time()
        interval = initial_interval
        completed = 0
        while not await self.is_ready_async():
            # Check for timeout
            elapsed = time() - start
            logger.debug(
                f"Waiting for tasks to complete... elapsed time: {elapsed:.2f}s"
            )
            if timeout is not None and elapsed > timeout:
                raise TimeoutError(
                    f"Timeout of {timeout} seconds exceeded while waiting for tasks."
                )
            # Refresh statuses and outputs
            await self.refresh_async()
            # Check for new completions
            new_completed = sum(status in READY_STATES for status in self.statuses)
            if new_completed > completed:
                completed = new_completed
                interval = initial_interval  # Reset interval if new completions found
            else:
                # Increase interval gradually (up to a max value)
                interval = min(interval * 1.5, 30.0)
            logger.debug(f"Sleeping for {interval:.2f} seconds before next poll.")
            await asyncio.sleep(interval)

        logger.info("All tasks are ready. Returning results.")
        assert all(
            output is not None for output in self.outputs
        ), "All outputs should be collected at this point."
        if self.return_single_output:
            return cast(ProgramOutput, self.outputs[0])
        return cast(list[ProgramOutput], self.outputs)

    def get(self, *args, **kwargs) -> Union[ProgramOutput, list[ProgramOutput]]:
        """Sync wrapper around `get_async`."""
        return self.client.run(self.get_async(*args, **kwargs))

    async def is_ready_async(self) -> bool:
        """
        Asynchronously refreshes the statuses and checks if all tasks are complete.
        """
        await self.refresh_async()
        return all(status in READY_STATES for status in self.statuses)

    @property
    def is_ready(self) -> bool:
        """Synch wrapper around `is_ready_async`."""
        return self.client.run(self.is_ready_async())

    async def as_completed_async(
        self, initial_interval: float = 1.0
    ) -> AsyncGenerator[ProgramOutput, None]:
        """
        Yields ProgramOutput objects as tasks become ready (SUCCESS, FAILURE, or REVOKED).
        Blocks until all tasks have finished or the generator is exhausted.

        This uses the same refresh logic as `.get_async()`, so it will automatically
        handle errors and generate ProgramOutput objects (including error placeholders)
        in the same way. The order in which results are yielded is not guaranteed
        to match the exact order tasks finish on the server.

        Parameters:
            initial_interval: The initial interval (in seconds) between refresh calls.
            This interval is increased by a factor of 1.5 on every poll cycle that
            finds no newly completed tasks, up to a maximum of 30 seconds.

        Yields:
            ProgramOutput objects for each task as they become ready.
            If a task fails, the yielded ProgramOutput will contain
            error/traceback information (just like `.get_async()`).
        """
        done_indices: set[int] = set()
        interval = initial_interval
        while len(done_indices) < len(self.task_ids):
            logger.debug("Polling for task completions...")
            await self.refresh_async()
            any_new = False
            for i, status in enumerate(self.statuses):
                if i not in done_indices and status in READY_STATES:
                    logger.info(
                        f"Task {self.task_ids[i]} is complete with status {status}."
                    )
                    done_indices.add(i)
                    any_new = True
                    if self.outputs[i] is not None:
                        yield cast(ProgramOutput, self.outputs[i])
                        self.outputs[i] = None  # Optional: clear to free memory

            if any_new:
                # Reset interval if new completions were found.
                interval = initial_interval

            else:
                interval = min(interval * 1.5, 30.0)
                logger.debug(f"No new completions; sleeping {interval:.2f} seconds.")
                await asyncio.sleep(interval)

    def as_completed(
        self, initial_interval: float = 1.0
    ) -> Generator[ProgramOutput, None, None]:
        """
        Synchronous implementation of `as_completed_async`.

        Cannot directly wrap async version due to it containing an AsyncGenerator, and
        asyncio.sleep() so we must reimplement the logic here.
        """
        done_indices: set[int] = set()
        interval = initial_interval

        # Keep polling until all tasks are completed
        while len(done_indices) < len(self.task_ids):
            logger.debug("Polling for task completions...")
            self.refresh()
            any_new = False
            for i, status in enumerate(self.statuses):
                if i not in done_indices and status in READY_STATES:
                    logger.info(
                        f"Task {self.task_ids[i]} is complete with status {status}."
                    )
                    done_indices.add(i)
                    any_new = True
                    assert self.outputs[i] is not None
                    yield cast(ProgramOutput, self.outputs[i])
                    self.outputs[i] = None  # Clear the output to save memory

            if any_new:
                # Reset interval if new completions were found.
                interval = initial_interval
            else:
                # Increase interval if nothing new was found.
                interval = min(interval * 1.5, 30.0)
                logger.debug(f"No new completions; sleeping {interval:.2f} seconds.")
                sleep(interval)

    def _output_from_exception(
        self, exc: Exception, input_data: Inputs
    ) -> ProgramOutput:
        """Create a ProgramOutput object from an exception."""
        tb_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        stdout_str = (
            "The ChemCloud server was unable to return this result. "
            "Please open an issue at https://github.com/mtzgroup/chemcloud-client/issues "
            "and include this entire ProgramOutput object in the issue description. "
            "You can dump this object to a JSON file using `output.save('output.json')`."
        )
        return ProgramOutput(
            input_data=input_data,
            success=False,
            results=Files(),  # Empty results
            stdout=stdout_str,
            traceback=tb_str,
            provenance={"program": self.program},
        )

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """
        Custom dump method that replaces the `client` field with a minimal configuration
        dictionary.
        """
        data = super().model_dump(**kwargs)
        data["client"] = {
            "chemcloud_domain": self.client._http_client._chemcloud_domain,
            "profile": self.client._http_client._profile,
        }
        return data

    def save(self, path: Optional[Union[str, Path]] = None) -> None:
        """Save the FutureOutput to a JSON file."""
        path = (
            Path(path)
            if path is not None
            else Path.cwd() / f"future-{uuid4().hex}.json"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.model_dump()))

    @classmethod
    def open(self, path: Union[str, Path]) -> "FutureOutput":
        """Load a FutureOutput from a JSON file."""
        data = json.loads(Path(path).read_text())
        return FutureOutput(**data)
