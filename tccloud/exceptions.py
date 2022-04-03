class BaseError(Exception):
    """Exception Base for client."""


class TimeoutError(BaseError):
    """A timeout parameter was exceeded"""
