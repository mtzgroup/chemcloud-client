from abc import ABC, abstractmethod
from enum import Enum
from time import sleep, time
from typing import Any, Dict, List, Optional, Union

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

from .exceptions import ComputeError, TimeoutError

# Convenience types
AtomicInputOrList = Union[AtomicInput, List[AtomicInput]]
OptimizationInputOrList = Union[OptimizationInput, List[OptimizationInput]]
PossibleResults = Union[AtomicResult, OptimizationResult, FailedOperation]
PossibleResultsOrList = Union[PossibleResults, List[PossibleResults]]


class TaskStatus(str, Enum):
    """Tasks status for a submitted compute job."""

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


# Set of states meaning the task result is ready (has been executed).
_READY_STATES = frozenset({TaskStatus.SUCCESS, TaskStatus.FAILURE, TaskStatus.REVOKED})
# Set of states meaning the task result is not ready (hasn't been executed).
_UNREADY_STATES = frozenset(
    {
        TaskStatus.PENDING,
        TaskStatus.RECEIVED,
        TaskStatus.STARTED,
        TaskStatus.REJECTED,
        TaskStatus.RETRY,
    }
)


class FutureResultBase(BaseModel, ABC):
    """Base class for FutureResults

    Parameters:
        task_id: The task_id for primary task submitted to TeraChem Cloud. May
            correspond to a single task for group of tasks
        client: The _RequestsClient to use for http requests to TeraChem Cloud
        result: Primary return value resulting from computation

    Caution:
        A FutureResult should never be instantiated directly.
        `TCClient.compute(...)` will return one when you submit a computation.
    """

    task_id: str
    result: Optional[Any] = None
    client: Any
    compute_status: TaskStatus = TaskStatus.PENDING

    class Config:
        # underscore_attrs_are_private = False
        validate_assignment = True

    @abstractmethod
    def to_task(self):
        """Convert to task dictionary for TeraChem Cloud /result endpoint"""
        raise NotImplementedError

    def get(
        self,
        timeout: Optional[float] = None,  # in seconds
        interval: float = 1.0,
        raise_error: bool = False,
    ) -> PossibleResults:
        """Block and return result.

        Parameters:
            timeout: The number of seconds to wait for a computation before raising a
                TimeOutError.
            interval: The amount of time to wait between calls to TeraChem Cloud to
                check a computation's status.
            raise_error: If set to True `.get()` will raise a ComputeError if the
                computation was unsuccessful.

        Returns:
            `AtomicResult` if computation succeeded or `FailedOperation` if computation failed.

        Exceptions:
            ComputeError: Raised if `raise_error=True`
        """
        if self.result:
            return self.result

        start_time = time()
        # Calling self.status returns status and sets self.result if task complete
        while self.status not in _READY_STATES:
            sleep(interval)
            if timeout:
                if (time() - start_time) > timeout:
                    raise TimeoutError(
                        f"Your timeout limit of {timeout} seconds was exceeded"
                    )

        if self.status != TaskStatus.SUCCESS and raise_error is True:
            raise ComputeError(
                f"An error occurred in your computation. \n"
                f"Status: {self.status}. \n"
                f"Additional information: {self.result}"
            )

        return self.result

    @property
    def status(self) -> str:
        """Check status of compute task.

        Returns:
            Status of computation.

        Note:
            Sets self.result if task is complete.

        NOTE: Do I want to return TaskStatus.FAILURE if FailedOperation is returned?
        """
        if self.compute_status in _READY_STATES:
            return self.compute_status
        self.compute_status, self.result = self.client.result(self.to_task())
        return self.compute_status


class FutureResult(FutureResultBase):
    """Single computation FutureResult"""

    result: Optional[PossibleResults] = None

    @classmethod
    def from_task(cls, task: Dict[str, str], client) -> "FutureResult":
        """Instantiate FutureResult from TeraChem Cloud Task"""
        return cls(task_id=task["task_id"], client=client)

    def to_task(self) -> Dict[str, str]:
        """To TeraChem Cloud task defintion"""
        return {"task_id": self.task_id}


class FutureResultGroup(FutureResultBase):
    """Group computation FutureResult

    Parameters:
        subtask_ids: Array of task_ids for children tasks. Children tasks exist when
            multiple computation were submitted as a group.
    """

    subtask_ids: List[str]
    result: Optional[List[PossibleResults]] = None

    @classmethod
    def from_task(cls, task: Dict[str, Any], client) -> "FutureResultGroup":
        """Instantiate FutureResult from TeraChem Cloud Task"""
        subtask_ids = [st["task_id"] for st in task["subtasks"]]
        return cls(task_id=task["task_id"], client=client, subtask_ids=subtask_ids)

    def to_task(self) -> Dict[str, Any]:
        """To TeraChem Cloud task defintion"""
        subtasks = [{"task_id": st_id} for st_id in self.subtask_ids]
        return {"task_id": self.task_id, "subtasks": subtasks}
