from time import sleep, time
from typing import Optional

from qcelemental.models import AtomicInput as AtomicInput  # noqa
from qcelemental.models import AtomicResult as AtomicResult  # noqa
from qcelemental.models import Molecule as Molecule  # noqa
from qcelemental.models.common_models import Model  # noqa

from .exceptions import ComputeError, TimeoutError

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
READY_STATES = frozenset({SUCCESS, FAILURE, REVOKED})
# Set of states meaning the task result is not ready (hasn't been executed).
UNREADY_STATES = frozenset({PENDING, RECEIVED, STARTED, REJECTED, RETRY})


class FutureResult:
    def __init__(self, task_id: str, client):
        """client is http_client._Requests client. Must avoid circular import"""
        self.task_id = task_id
        self.result: Optional[AtomicResult] = None
        self._client = client
        self._status: str = PENDING

    def __repr__(self) -> str:
        return f"{type(self).__name__}(task_id={self.task_id}, result={self.result})"

    def get(
        self, timeout: Optional[float] = None, interval: float = 1.0
    ) -> AtomicResult:
        """Block and return AtomicResult."""
        if self.result:
            return self.result

        start_time = time()
        status, result = self._client.result(self.task_id)
        while status not in READY_STATES:
            sleep(interval)
            status, result = self._client.result(self.task_id)
            if timeout:
                if (time() - start_time) > timeout:
                    raise TimeoutError(
                        f"Your timeout limit of {timeout} seconds was exceeded"
                    )

        if status == SUCCESS:
            self.result = result
            return self.result
        else:
            raise ComputeError(
                f"An error occured in your computation. \n"
                f"Status: {status}. \n"
                f"Additional information: {result}"
            )

    @property
    def status(self) -> str:
        """Check status of compute job"""
        if self._status in READY_STATES:
            return self._status
        self._status, result = self._client.result(self.task_id)
        if result:
            self.result = result
        return self._status
