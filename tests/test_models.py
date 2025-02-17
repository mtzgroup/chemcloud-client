import json
import re
from pathlib import Path

from pytest_httpx import HTTPXMock
from qcio import FileInput, ProgramOutput

from chemcloud import CCClient, FutureOutput
from chemcloud.models import TaskStatus


def test_result_pending(
    settings,
    jwt,
    httpx_mock: HTTPXMock,
):
    client = CCClient(settings=settings)
    client._http_client._access_token = jwt

    httpx_mock.add_response(json={"status": "PENDING", "program_output": None})

    future = FutureOutput(
        task_ids=["fake_task_id"],
        client=client,
        inputs=[FileInput()],
        program="fake_program",
    )
    status, output = future.client.fetch_output(future.task_id)

    assert status == TaskStatus.PENDING
    assert output is None


def test_result_success(
    settings,
    jwt,
    httpx_mock: HTTPXMock,
):
    client = CCClient(settings=settings)
    client._http_client._access_token = jwt

    output: ProgramOutput = ProgramOutput.model_validate_json(
        (Path(__file__).parent / "water.b3lyp.6-31g.energy.json").read_text()
    )
    url = re.compile(".*/compute/output")
    httpx_mock.add_response(
        url=url,
        json={
            "status": "SUCCESS",
            "program_output": json.loads(output.model_dump_json()),
        },
    )

    future = FutureOutput(
        task_ids=["fake_task_id"],
        inputs=[FileInput()],
        program="fake_program",
        client=client,
    )
    status, output = future.client.fetch_output("fake_task_id")

    assert status == "SUCCESS"
    assert isinstance(output, ProgramOutput)  # type: ignore


def test_as_completed(httpx_mock, settings, jwt):
    # Instantiate the client and set a valid token.
    client = CCClient(settings=settings)
    client._http_client._access_token = jwt

    # Load a valid ProgramOutput from a JSON file.
    output: ProgramOutput = ProgramOutput.model_validate_json(
        (Path(__file__).parent / "water.b3lyp.6-31g.energy.json").read_text()
    )

    # Create a regex for matching compute output endpoints.
    url = re.compile(".*/compute/output")

    # First response: task is still pending (no program_output).
    httpx_mock.add_response(
        url=url,
        json={"status": "PENDING", "program_output": None},
    )

    # Second response: task is complete with a successful output.
    httpx_mock.add_response(
        url=url,
        json={
            "status": "SUCCESS",
            "program_output": json.loads(output.model_dump_json()),
        },
    )

    # Create a FutureOutput instance with a single task.
    future = FutureOutput(
        task_ids=["fake_task_id"],
        inputs=[{}],  # Using an empty dict as a stand-in for an Inputs instance.
        program="fake_program",
        client=client,
    )

    # Call as_completed with a short initial_interval so the test runs fast.
    outputs = list(future.as_completed(initial_interval=0.1))

    # We expect one completed output to be yielded.
    assert len(outputs) == 1
    result = outputs[0]
    assert isinstance(result, ProgramOutput)
    assert all([output is None for output in future.outputs])


def test_model_dump_returns_client_config(prog_input):
    """
    Test that model_dump() replaces the `client` field with a minimal configuration
    dictionary containing the chemcloud_domain and profile.
    """
    # Create a client with a custom domain and profile.
    client = CCClient(chemcloud_domain="https://example.com", profile="testprofile")
    # Create a FutureOutput instance.
    future = FutureOutput(
        task_ids=["task1"],
        inputs=[prog_input],
        program="dummy",
        client=client,
    )
    dumped = future.model_dump()  # Using our overridden model_dump method.

    # Check that the dumped data contains a "client" field with our minimal config.
    assert "client" in dumped, "Dumped data should have a 'client' field."
    client_config = dumped["client"]
    assert client_config["chemcloud_domain"] == "https://example.com"
    assert client_config["profile"] == "testprofile"


def test_ensure_client_validator(prog_input):
    """
    Test that if the client field is provided as a dict (serialized configuration),
    the field validator instantiates a proper CCClient.
    """
    # Create a minimal client configuration dict.
    client_config = {
        "chemcloud_domain": "https://example.com",
        "profile": "testprofile",
    }
    # Create a FutureOutput with the client field as a dict.
    future = FutureOutput(
        task_ids=["task1"],
        inputs=[prog_input],
        program="dummy",
        client=client_config,
    )
    # The validator should have converted the dict into a CCClient.
    assert isinstance(
        future.client, CCClient
    ), "Client field should be an instance of CCClient."
    # Check that the instantiated client has the expected configuration.
    assert future.client._http_client._chemcloud_domain == "https://example.com"
    assert future.client._http_client._profile == "testprofile"


def test_save_with_provided_path(tmp_path, prog_input):
    """
    Test that save() writes a JSON file containing the dumped data,
    with the client field replaced by its minimal configuration.
    """
    # Create a FutureOutput with known dummy data.
    future = FutureOutput(
        task_ids=["task_ids"],
        inputs=[prog_input],
        program="program",
        client=CCClient(chemcloud_domain="https://example.com", profile="testprofile"),
    )
    # Save to a specific file path.
    file_path = tmp_path / "future_test.json"
    future.save(file_path)

    # Verify the file was created.
    assert file_path.exists(), "File was not created by save()"

    # Read the file content.
    saved_data = json.loads(file_path.read_text())
    # The saved data should match what model_dump() returns.
    assert (
        saved_data == future.model_dump()
    ), "Saved JSON does not match expected dump data."


def test_open(tmp_path, prog_input):
    """
    Test that a FutureOutput saved to disk can be reloaded correctly.
    The client field should be re-instantiated as a CCClient.
    """
    # Create a FutureOutput with known dummy data.
    future = FutureOutput(
        task_ids=["task_ids"],
        inputs=[prog_input],
        program="program",
        client=CCClient(chemcloud_domain="https://example.com", profile="testprofile"),
    )
    # Save to a specific file path.
    file_path = tmp_path / "future_test.json"
    future.save(file_path)

    # Load the FutureOutput from the saved file.
    loaded_future = FutureOutput.open(file_path)

    # Verify basic fields.
    assert loaded_future.task_ids == future.task_ids
    assert loaded_future.inputs == future.inputs
    assert loaded_future.program == future.program

    # Verify that the client was re-instantiated as a CCClient with the proper configuration.
    assert isinstance(
        loaded_future.client, CCClient
    ), "Client was not re-instantiated as CCClient"
    assert loaded_future.client._http_client._chemcloud_domain == "https://example.com"
    assert loaded_future.client._http_client._profile == "testprofile"
