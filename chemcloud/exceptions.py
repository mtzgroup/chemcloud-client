class BaseError(Exception):
    """Exception Base for client."""


class TimeoutError(BaseError):
    """A timeout parameter was exceeded"""


class UnsupportedProgramError(BaseError):
    """A program is not supported by ChemCloud"""


class AuthenticationError(BaseError):
    """An error occurred during authentication."""
