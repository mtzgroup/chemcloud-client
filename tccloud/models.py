from abc import ABC
from enum import Enum
from pathlib import Path
from time import sleep, time
from typing import Any, List, Optional, Type, Union

from pydantic import validator
from pydantic.main import BaseModel
from qcelemental.models import AtomicInput as AtomicInput  # noqa: F401
from qcelemental.models import AtomicResult as AtomicResult  # noqa: F401
from qcelemental.models import Molecule as Molecule  # noqa: F401
from qcelemental.models import OptimizationInput as OptimizationInput  # noqa: F401
from qcelemental.models import OptimizationResult as OptimizationResult  # noqa: F401
from qcelemental.models.common_models import FailedOperation
from qcelemental.models.common_models import Model as Model  # noqa: F401
from qcelemental.models.procedures import (  # noqa: F401
    QCInputSpecification as QCInputSpecification,
)

from .exceptions import TimeoutError

GROUP_ID_PREFIX = "group-"

# Convenience types
AtomicInputOrList = Union[AtomicInput, List[AtomicInput]]
OptimizationInputOrList = Union[OptimizationInput, List[OptimizationInput]]
PossibleResults = Union[AtomicResult, OptimizationResult, FailedOperation]
PossibleResultsOrList = Union[PossibleResults, List[PossibleResults]]


class TaskStatus(str, Enum):
    """Tasks status for a submitted compute job."""

    #: Task state is unknown (assumed pending since you know the id).
    PENDING = "PENDING"
    COMPLETE = "COMPLETE"


class FutureResultBase(BaseModel, ABC):
    """Base class for FutureResults

    Parameters:
        id: The id for primary task submitted to TeraChem Cloud. May correspond to a
            single task or group of tasks
        client: The _RequestsClient to use for http requests to TeraChem Cloud
        result: Primary return value resulting from computation

    Caution:
        A FutureResult should never be instantiated directly.
        `TCClient.compute(...)` will return one when you submit a computation.
    """

    id: str
    result: Optional[Any] = None
    client: Any
    _state: TaskStatus = TaskStatus.PENDING

    class Config:
        underscore_attrs_are_private = True
        validate_assignment = True

    def get(
        self,
        timeout: Optional[float] = None,  # in seconds
        interval: float = 1.0,
    ) -> PossibleResultsOrList:
        """Block and return result.

        Parameters:
            timeout: The number of seconds to wait for a computation before raising a
                TimeOutError.
            interval: The amount of time to wait between calls to TeraChem Cloud to
                check a computation's status.

        Returns:
            Resultant values from a computation.

        Exceptions:
            TimeoutError: Raised if timout interval exceeded.
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

    def _result(self):
        """Return result from server"""
        return self.client.result(self.id)

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
        self._state, self.result = self._result()
        return self._state


class FutureResult(FutureResultBase):
    """Single computation result"""

    result: Optional[PossibleResults] = None


class FutureResultGroup(FutureResultBase):
    """Group computation result"""

    result: Optional[List[PossibleResults]] = None

    def _result(self):
        """Return result from server. Remove GROUP_ID_PREFIX from id."""
        return self.client.result(self.id.replace(GROUP_ID_PREFIX, ""))

    @validator("id")
    def validate_id(cls, v):
        """Prepend id with GROUP_ID_PREFIX.

        NOTE:
            This makes instiating FutureResultGroups from saved ids easier because
            they are differentiated from FutureResult ids.
        """
        if not v.startswith(GROUP_ID_PREFIX):
            v = GROUP_ID_PREFIX + v
        return v


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
        client: Instantiated TCClient object
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
