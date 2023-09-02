from abc import ABC
from enum import Enum
from pathlib import Path
from time import sleep, time
from typing import Any, List, Optional, Type, Union

from pydantic import field_validator
from pydantic.main import BaseModel
from qcio import (
    DualProgramInput,
    FileInput,
    FileOutput,
    OptimizationOutput,
    ProgramFailure,
    ProgramInput,
    SinglePointOutput,
)

from .exceptions import TimeoutError

GROUP_ID_PREFIX = "group-"

# Convenience types
QCIOInputs = Union[ProgramInput, FileInput, DualProgramInput]
QCIOInputsOrList = Union[QCIOInputs, List[QCIOInputs]]
QCIOOutputs = Union[FileOutput, SinglePointOutput, OptimizationOutput, ProgramFailure]
QCIOOutputsOrList = Union[QCIOOutputs, List[QCIOOutputs]]


class TaskStatus(str, Enum):
    """Tasks status for a submitted compute job."""

    #: Task state is unknown (assumed pending since you know the id).
    PENDING = "PENDING"
    COMPLETE = "COMPLETE"


class FutureResultBase(BaseModel, ABC):
    """Base class for FutureResults

    Parameters:
        id: The id for primary task submitted to ChemCloud. May correspond to a
            single task or group of tasks
        client: The _RequestsClient to use for http requests to ChemCloud
        result: Primary return value resulting from computation

    Caution:
        A FutureResult should never be instantiated directly.
        `CCClient.compute(...)` will return one when you submit a computation.
    """

    id: str
    result: Optional[QCIOOutputsOrList] = None
    client: Any
    _state: TaskStatus = TaskStatus.PENDING

    model_config = {"validate_assignment": True}

    def get(
        self,
        timeout: Optional[float] = None,  # in seconds
        interval: float = 1.0,
    ) -> QCIOOutputsOrList:
        """Block and return result.

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

        while not self.result:
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
        return self.client.output(self.id)

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


class FutureResult(FutureResultBase):
    """Single computation result"""

    result: Optional[QCIOOutputs] = None


class FutureResultGroup(FutureResultBase):
    """Group computation result"""

    result: Optional[List[QCIOOutputs]] = None

    def _output(self):
        """Return result from server. Remove GROUP_ID_PREFIX from id."""
        return self.client.output(self.id.replace(GROUP_ID_PREFIX, ""))

    @field_validator("id")
    @classmethod
    def validate_id(cls, val):
        """Prepend id with GROUP_ID_PREFIX.

        NOTE:
            This makes instantiating FutureResultGroups from saved ids easier because
            they are differentiated from FutureResult ids.
        """
        if not val.startswith(GROUP_ID_PREFIX):
            val = GROUP_ID_PREFIX + val
        return val


def to_file(
    future_results: Union[FutureResultBase, List[FutureResultBase]],
    path: Union[str, Path],
    *,
    append: bool = False,
) -> None:
    """Write FutureResults to disk for later retrieval

    Params:
        future_results: List of or single FutureResult or FutureResultGroup
        path: File path to results file
        append: Append results to an existing file if True, else create new file
    """
    if not isinstance(future_results, list):
        future_results = [future_results]

    with open(path, f"{'a' if append else 'w'}") as f:
        f.writelines([f"{fr.id}\n" for fr in future_results])


def from_file(
    path: Union[str, Path],
    client: Any,
) -> List[Union[FutureResult, FutureResultGroup]]:
    """Instantiate FutureResults or FutureResultGroups from file of result ids

    Params:
        path: Path to file containing the ids
        client: Instantiated CCClient object
    """
    frs: List[Union[FutureResult, FutureResultGroup]] = []
    with open(path) as f:
        for id in f.readlines():
            id = id.strip()
            model: Union[Type[FutureResult], Type[FutureResultGroup]]
            if id.startswith(GROUP_ID_PREFIX):
                model = FutureResultGroup
            else:
                model = FutureResult
            frs.append(model(id=id, client=client._client))

    assert len(frs) > 0, "No ids found in file!"
    return frs
