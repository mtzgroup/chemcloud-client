"""ChemCloud python client. Scalable compute, easy to learn, fast to code."""

# https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
from importlib import metadata
from typing import Optional

__version__ = metadata.version(__name__)

from .client import CCClient
from .models import FutureOutput  # noqa

_default_client: Optional[CCClient] = None


def compute(*args, **kwargs):
    """Submit a compute job using the default client.

    See [CCClient.compute][chemcloud.client.CCClient.compute] for more information.
    """
    global _default_client
    if _default_client is None:
        _default_client = CCClient()
    return _default_client.compute(*args, **kwargs)


def hello_world(name: Optional[str] = None) -> str:
    """Return a greeting message from the ChemCloud server.

    See [CCClient.hello_world][chemcloud.client.CCClient.hello_world] for more information.
    """
    global _default_client
    if _default_client is None:
        _default_client = CCClient()
    return _default_client.hello_world(name)


def setup_profile(profile: Optional[str] = None) -> None:
    """Setup a profile for the ChemCloud client.

    See [CCClient.setup_profile][chemcloud.client.CCClient.setup_profile] for more information.
    """
    client = CCClient()
    client.setup_profile(profile)


def configure_client(**kwargs) -> None:
    """Configure the default ChemCloud client.

    Passes keyword arguments to CCClient constructor.
    See [CCClient][chemcloud.client.CCClient] for more information.
    """
    global _default_client
    _default_client = CCClient(**kwargs)


def fetch_output(*args, **kwargs):
    """Fetch the status and output of a compute job using the default client.

    Only needed if you want on manually check the status of a compute job.

    See [CCClient.fetch_output][chemcloud.client.CCClient.fetch_output] for more information.
    """
    global _default_client
    if _default_client is None:
        _default_client = CCClient()
    return _default_client.fetch_output(*args, **kwargs)
