class BaseError(Exception):
    """Exception Base for client."""

    pass


class ComputeError(BaseError):
    """Some exception was raised with a computation"""

    pass


class TimeoutError(BaseError):
    """A timeout parameter was exceeded"""

    pass
