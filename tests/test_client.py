from qcio import ProgramOutput

from chemcloud import CCClient, FutureOutput


def test_version():
    client = CCClient()
    assert isinstance(client.version, str)


def test_compute(
    settings, patch_openapi_endpoint, patch_compute_endpoints, prog_input, jwt
):
    client = CCClient(settings=settings)
    client._http_client._access_token = jwt

    result = client.compute("psi4", prog_input)
    assert isinstance(result, ProgramOutput)


def test_compute_future(
    settings, patch_openapi_endpoint, patch_compute_endpoints, prog_input, jwt
):
    client = CCClient(settings=settings)
    client._http_client._access_token = jwt

    future = client.compute("psi4", prog_input, return_future=True)
    assert isinstance(future, FutureOutput)
    assert future.task_ids[0] == patch_compute_endpoints
    assert future.client is client


def test_compute_batch_future(
    settings, patch_openapi_endpoint, patch_compute_endpoints, prog_input, jwt
):
    client = CCClient(settings=settings)
    client._http_client._access_token = jwt

    future = client.compute("psi4", [prog_input] * 2, return_future=True)

    assert isinstance(future, FutureOutput)
    assert future.task_ids[0] == f"{patch_compute_endpoints}"
    assert future.client is client


def test_compute_queue_explicit(
    settings,
    patch_openapi_endpoint,
    patch_compute_endpoints,
    water,
    jwt,
    mocker,
    prog_input,
):
    """
    If a queue is explicitly passed to compute(), then that value should be used.
    """
    client = CCClient(settings=settings)
    client._http_client._access_token = jwt

    # Spy on the method that sends the HTTP request
    spy = mocker.spy(client._http_client, "_authenticated_request_async")

    explicit_queue = "explicit_queue"
    # Call compute() with an explicit queue
    client.compute("psi4", prog_input, queue=explicit_queue)

    # Verify that _authenticated_request_async was called at least once with the correct queue.
    assert (
        spy.call_count == 2
    ), "Should be called once to submit the task, once to get the result."
    # Get the keyword arguments from the first call.
    call_kwargs = spy.call_args_list[0].kwargs
    # Get the URL parameters from the first call.
    params = call_kwargs.get("params")
    assert params is not None, "No URL parameters were passed."
    assert params.get("queue") == explicit_queue, "Explicit queue was not used."


def test_compute_queue_from_client(
    settings,
    patch_openapi_endpoint,
    patch_compute_endpoints,
    water,
    jwt,
    mocker,
    prog_input,
):
    """
    If no queue is passed to compute() but CCClient was configured with a queue,
    then that value should be used.
    """
    client_queue = "client_queue"
    client = CCClient(settings=settings, queue=client_queue)
    client._http_client._access_token = jwt

    # Spy on the method that sends the HTTP request.
    spy = mocker.spy(client._http_client, "_authenticated_request_async")

    # Call compute() without an explicit queue.
    client.compute("psi4", prog_input)

    # Verify that _authenticated_request_async was called twice.
    assert (
        spy.call_count == 2
    ), "Should be called once to submit the task, once to get the result."
    # Get the keyword arguments from the first call.
    call_kwargs = spy.call_args_list[0].kwargs
    # Get the URL parameters from the first call.
    params = call_kwargs.get("params")
    assert params is not None, "No URL parameters were passed."
    assert params.get("queue") == client_queue, "Client queue was not used."


def test_compute_queue_from_settings(
    settings, patch_openapi_endpoint, patch_compute_endpoints, jwt, mocker, prog_input
):
    """
    If neither compute() nor CCClient specify a queue, then the queue from settings should be used.
    """
    env_queue = "env_queue"
    original_queue = settings.chemcloud_queue
    settings.chemcloud_queue = env_queue
    client = CCClient(settings=settings)  # No explicit queue passed
    client._http_client._access_token = jwt

    spy = mocker.spy(client._http_client, "_authenticated_request_async")

    # Call compute() without providing a queue.
    client.compute("psi4", prog_input)

    # Verify that _authenticated_request_async was called twice.
    assert (
        spy.call_count == 2
    ), "Should be called once to submit the task, once to get the result."
    call_kwargs = spy.call_args_list[0].kwargs
    params = call_kwargs.get("params")
    assert params is not None, "No URL parameters were passed."
    assert params.get("queue") == env_queue, "Default queue from settings was not used."

    # Restore the original queue value.
    settings.chemcloud_queue = original_queue
