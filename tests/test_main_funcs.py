# Import the function and global default client from your package's __init__.py.
from qcio import ProgramOutput

import chemcloud
from chemcloud import FutureOutput, compute, configure_client
from chemcloud.client import CCClient


def test_configure_client():
    """
    Test that configure_client sets the default client (_default_client) with the correct queue
    and chemcloud_domain values.
    """
    # Reset global default client
    chemcloud._default_client = None

    # Call configure_client with custom values.
    configure_client(chemcloud_domain="https://example.com", queue="testqueue")
    # _default_client should now be an instance of CCClient.

    assert isinstance(
        chemcloud._default_client, CCClient
    ), "Default client not instantiated properly."
    # The client's queue should be set to the provided value.
    assert (
        chemcloud._default_client.queue == "testqueue"
    ), "Client queue is not set correctly."
    # The underlying HTTP client's chemcloud_domain should match our value.
    assert (
        chemcloud._default_client._http_client._chemcloud_domain
        == "https://example.com"
    ), "chemcloud_domain was not set correctly."


def test_compute(
    patch_openapi_endpoint,
    patch_compute_endpoints,
    prog_input,
    jwt,
):
    # Reset global default client
    chemcloud._default_client = None
    configure_client()

    # Set JWT so that the client can make requests
    from chemcloud import _default_client

    _default_client._http_client._access_token = jwt

    # Single input
    output = compute("psi4", prog_input)
    assert isinstance(output, ProgramOutput), "Output is not a ProgramOutput."

    # Input list
    outputs = compute("psi4", [prog_input] * 2)
    assert isinstance(outputs, list), "Outputs is not a list."
    assert all(
        [isinstance(output, ProgramOutput) for output in outputs]
    ), "Not all outputs are ProgramOutput instances."


def test_compute_future(
    patch_openapi_endpoint,
    patch_compute_endpoints,
    prog_input,
    jwt,
):
    # Reset global default client
    chemcloud._default_client = None
    configure_client()

    # Set JWT so that the client can make requests
    from chemcloud import _default_client

    _default_client._http_client._access_token = jwt

    # Single input
    future = compute("psi4", prog_input, return_future=True)
    assert isinstance(future, FutureOutput), "Future is not a FutureOutput instance."
    output = future.get()
    assert isinstance(output, ProgramOutput), "Output is not a ProgramOutput."

    # Input list
    futures = compute("psi4", [prog_input] * 2, return_future=True)
    assert isinstance(futures, FutureOutput), "Futures is not a FutureOutput instance."
    assert len(futures.task_ids) == 2, "Incorrect number of task IDs."
    outputs = futures.get()
    assert isinstance(outputs, list), "Outputs is not a list."
    assert all(
        [isinstance(output, ProgramOutput) for output in outputs]
    ), "Not all outputs are ProgramOutput instances."
