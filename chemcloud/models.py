from abc import ABC
from enum import Enum
from pathlib import Path
from time import sleep, time
from typing import Any, List, Optional, Type, Union

from pydantic import field_validator
from pydantic.main import BaseModel
from qcio import DualProgramInput, FileInput, ProgramInput, ProgramOutput
from typing_extensions import TypeAlias

from .exceptions import TimeoutError

GROUP_ID_PREFIX = "group-"

# Convenience types
QCIOInputs: TypeAlias = Union[ProgramInput, FileInput, DualProgramInput]
QCIOInputsOrList: TypeAlias = Union[QCIOInputs, List[QCIOInputs]]
QCIOOutputs: TypeAlias = ProgramOutput
QCIOOutputsOrList: TypeAlias = Union[QCIOOutputs, List[QCIOOutputs]]


class TaskStatus(str, Enum):
    """Tasks status for a submitted compute job."""

    #: Task state is unknown (assumed pending since you know the id).
    PENDING = "PENDING"
    COMPLETE = "COMPLETE"
    FAILURE = "FAILURE"


class FutureOutputBase(BaseModel, ABC):
    """Base class for FutureOutputs

    Attributes:
        task_id: The task_id for primary task submitted to ChemCloud. May correspond to
            a single task or group of tasks.
        client: The _RequestsClient to use for http requests to ChemCloud.
        result: Primary return value resulting from computation.

    Caution:
        A FutureOutput should never be instantiated directly.
        `CCClient.compute(...)` will return one when you submit a computation.
    """

    task_id: str
    result: Optional[QCIOOutputsOrList] = None
    client: Any
    _state: TaskStatus = TaskStatus.PENDING

    model_config = {"validate_assignment": True}

    def get(
        self,
        timeout: Optional[float] = None,  # in seconds
        interval: float = 1.0,
    ) -> Optional[QCIOOutputsOrList]:
        """Block until a calculation is complete and return the result.

        Parameters:
            timeout: The number of seconds to wait for a computation before raising a
                TimeOutError.
            interval: The amount of time to wait between calls to ChemCloud to
                check a computation's status.

        Returns:
            Resultant values from a computation.

        Exceptions:
            TimeoutError: Raised if timeout interval exceeded.
        """
        if self.result:
            return self.result

        start_time = time()

        # self._state check prevents 401 errors from ChemCloud when the job completed
        # but the server failed to return a result (e.g., due to .program_output not)
        # being set correctly by qcio/BigChem.
        # TODO: Make a clearer contract between Server and Client re: states. This got
        # a bit messy as I switched mimicking celery states to the more simplified setup
        # I have now. This can be simplified further.
        while not self.result and self._state not in {"COMPLETE", "FAILURE"}:
            # Calling self.status returns status and sets self.result if task complete
            self.status
            if timeout:
                if (time() - start_time) > timeout:
                    raise TimeoutError(
                        f"Your timeout limit of {timeout} seconds was exceeded"
                    )
            sleep(interval)

        return self.result

    def _output(self):
        """Return output from server"""
        return self.client.output(self.task_id)

    @property
    def status(self) -> str:
        """Check status of compute task.

        Returns:
            Status of computation.

        Note:
            Sets self.result if task is complete.
        """
        if self.result:
            return self._state
        self._state, self.result = self._output()
        return self._state


class FutureOutput(FutureOutputBase):
    """Single computation result"""

    result: Optional[QCIOOutputs] = None


class FutureOutputGroup(FutureOutputBase):
    """Group computation result"""

    result: Optional[List[QCIOOutputs]] = None

    def _output(self):
        """Return result from server. Remove GROUP_ID_PREFIX from id."""
        return self.client.output(self.task_id.replace(GROUP_ID_PREFIX, ""))

    @field_validator("task_id")
    @classmethod
    def validate_id(cls, val):
        """Prepend id with GROUP_ID_PREFIX.

        NOTE:
            This makes instantiating FutureOutputGroups from saved ids easier because
            they are differentiated from FutureOutput ids.
        """
        if not val.startswith(GROUP_ID_PREFIX):
            val = GROUP_ID_PREFIX + val
        return val


def to_file(
    future_results: Union[FutureOutputBase, List[FutureOutputBase]],
    path: Union[str, Path],
    *,
    append: bool = False,
) -> None:
    """Write FutureOutputs to disk for later retrieval

    Params:
        future_results: List of or single FutureOutput or FutureOutputGroup
        path: File path to results file
        append: Append results to an existing file if True, else create new file
    """
    if not isinstance(future_results, list):
        future_results = [future_results]

    with open(path, f"{'a' if append else 'w'}") as f:
        f.writelines([f"{fr.task_id}\n" for fr in future_results])


def from_file(
    path: Union[str, Path],
    client: Any,
) -> List[Union[FutureOutput, FutureOutputGroup]]:
    """Instantiate FutureOutputs or FutureOutputGroups from file of result ids

    Params:
        path: Path to file containing the ids
        client: Instantiated CCClient object
    """
    frs: List[Union[FutureOutput, FutureOutputGroup]] = []
    with open(path) as f:
        for id in f.readlines():
            id = id.strip()
            model: Union[Type[FutureOutput], Type[FutureOutputGroup]]
            if id.startswith(GROUP_ID_PREFIX):
                model = FutureOutputGroup
            else:
                model = FutureOutput
            frs.append(model(task_id=id, client=client._client))

    assert len(frs) > 0, "No ids found in file!"
    return frs
