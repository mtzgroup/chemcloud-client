class BaseError(Exception):
    """Exception Base for client."""


class ComputeError(BaseError):
    """Some exception was raised with a computation"""


class TimeoutError(BaseError):
    """A timeout parameter was exceeded"""
