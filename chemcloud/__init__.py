"""ChemCloud python client. Scalable compute, easy to learn, fast to code."""

# https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
from importlib import metadata
from typing import Optional, Union

__version__ = metadata.version(__name__)

from qcio import ProgramOutput

from .client import CCClient
from .models import FutureOutput  # noqa

_default_client: Optional[CCClient] = None


def compute(*args, **kwargs) -> Union[ProgramOutput, list[ProgramOutput], FutureOutput]:
    """Submit a compute job using the default client.

    See [CCClient.compute][chemcloud.client.CCClient.compute] for more information.

    Usage:
        ```python
        from qcio import ProgramInput, Structure
        from chemcloud import compute

        struct = Structure.open("structure.xyz")
        prog_input = ProgramInput(
            calctype="energy",
            structure=struct,
            model={"method": "b3lyp", "basis": "6-31g"},
            keywords={},  # Optional keywords for the program
            )

        # Submit a single job
        output = compute("psi4", prog_input)

        # Submit multiple jobs
        prog_inputs = [prog_input] * 100  # List of ProgramInput objects
        outputs = compute("psi4", prog_inputs)
        ```

        Results may be collected asynchronously if desired:

        ```python
        future = compute("psi4", prog_inputs, return_future=True)
        future.is_ready  # Checks if all tasks are complete (not required)
        outputs = future.get()  # Collects results
        ```

        Or stream results from the server as they complete:

        ```python
        future = compute("psi4", prog_inputs, return_future=True)
        for output in future.as_completed():  # Will return results as the complete
            # Process outputs
        ```
    """
    global _default_client
    if _default_client is None:
        _default_client = CCClient()
    return _default_client.compute(*args, **kwargs)


def configure_client(**kwargs) -> None:
    """Configure the default ChemCloud client.

    Passes keyword arguments to CCClient constructor.
    See [CCClient][chemcloud.client.CCClient] for more information.

    Usage:
        Pass any of the following keyword arguments before calling
        [compute][chemcloud.compute] to configure the client.

        ```python
        from chemcloud import configure_client

        configure_client(
            chemcloud_username="testuser",  # Not recommended
            chemcloud_password="testpassword",  # Not recommended  # pragma: allowlist secret
            chemcloud_domain="https://example.com",
            profile="testprofile",
            queue="myqueue",
            )
        ```
    """
    global _default_client
    _default_client = CCClient(**kwargs)


def setup_profile(profile: Optional[str] = None) -> None:
    """Setup a profile for the ChemCloud client.

    See [CCClient.setup_profile][chemcloud.client.CCClient.setup_profile] for more information.
    """
    client = CCClient()
    client.setup_profile(profile)


def fetch_output(*args, **kwargs):
    """Fetch the status and output of a compute job using the default client.

    Only needed if you want on manually check the status of a compute job. This function
    is usually not used by end users.

    See [CCClient.fetch_output][chemcloud.client.CCClient.fetch_output] for more information.
    """
    global _default_client
    if _default_client is None:
        _default_client = CCClient()
    return _default_client.fetch_output(*args, **kwargs)


def hello_world(name: Optional[str] = None) -> str:
    """Return a greeting message from the ChemCloud server.

    See [CCClient.hello_world][chemcloud.client.CCClient.hello_world] for more information.
    """
    global _default_client
    if _default_client is None:
        _default_client = CCClient()
    return _default_client.hello_world(name)
