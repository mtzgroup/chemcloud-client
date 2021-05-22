from enum import Enum
from time import sleep, time
from typing import Optional, Union

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

PossibleResults = Union[AtomicResult, OptimizationResult, FailedOperation]


class FutureResult:
    def __init__(self, task_id: str, client):
        """client is http_client._Requests client. Must avoid circular import

        Caution:
            A FutureResult should never be instantiated directly.
            `TCClient.compute(...)` will return one when you submit a computation.
        """
        self.task_id = task_id
        self.result: Optional[PossibleResults] = None
        self._client = client
        self._status: TaskStatus = TaskStatus.PENDING

    def __repr__(self) -> str:
        return f"{type(self).__name__}(task_id={self.task_id}, result={self.result})"

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
        """
        if self._status in _READY_STATES:
            return self._status
        self._status, result = self._client.result(self.task_id)
        if result:
            self.result = result
        return self._status.value
