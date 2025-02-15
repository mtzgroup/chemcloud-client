from qcio import Model, ProgramInput, ProgramOutput

from chemcloud import CCClient, FutureOutput


def test_version():
    client = CCClient()
    assert isinstance(client.version, str)


def test_compute(settings, patch_openapi_endpoint, patch_compute_endpoints, water, jwt):
    client = CCClient(settings=settings)
    client._http_client._access_token = jwt

    Model(method="B3LYP", basis="6-31g")
    atomic_input = ProgramInput(
        structure=water, model={"method": "b3lyp", "basis": "6-31g"}, calctype="energy"
    )

    result = client.compute("psi4", atomic_input)
    assert isinstance(result, ProgramOutput)


def test_compute_future(
    settings, patch_openapi_endpoint, patch_compute_endpoints, water, jwt
):
    client = CCClient(settings=settings)
    client._http_client._access_token = jwt

    Model(method="B3LYP", basis="6-31g")
    atomic_input = ProgramInput(
        structure=water, model={"method": "b3lyp", "basis": "6-31g"}, calctype="energy"
    )

    future = client.compute("psi4", atomic_input, return_future=True)
    assert isinstance(future, FutureOutput)
    assert future.task_ids[0] == patch_compute_endpoints
    assert future.client is client


def test_compute_batch_future(
    settings, patch_openapi_endpoint, patch_compute_endpoints, water, jwt
):
    client = CCClient(settings=settings)
    client._http_client._access_token = jwt

    model = Model(method="B3LYP", basis="6-31g")
    atomic_input = ProgramInput(structure=water, model=model, calctype="energy")

    future = client.compute("psi4", [atomic_input, atomic_input], return_future=True)

    assert isinstance(future, FutureOutput)
    assert future.task_ids[0] == f"{patch_compute_endpoints}"
    assert future.client is client
