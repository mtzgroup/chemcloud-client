import json
import re
from pathlib import Path

import toml
from pytest_httpx import HTTPXMock
from qcelemental.models.common_models import Model

from tccloud.config import Settings
from tccloud.http_client import _RequestsClient
from tccloud.models import (
    AtomicInput,
    AtomicResult,
    FutureResult,
    FutureResultGroup,
    OptimizationInput,
    QCInputSpecification,
    TaskStatus,
)


def test_passing_username_password_are_prioritized_for_auth(
    mocker, monkeypatch, settings, credentials_file, patch_token_endpoint, jwt
):
    # Set environment variables
    monkeypatch.setenv("TCCLOUD_USERNAME", "env_username", prepend=False)
    monkeypatch.setenv("TCCLOUD_PASSWORD", "env_password", prepend=False)

    # Create Credentials file
    refresh_token = "credentials_file_refresh_token"
    credentials_file(jwt, refresh_token)

    spy = mocker.spy(_RequestsClient, "_tokens_from_username_password")

    # Instantiate client
    passed_username = "passed_username"
    passed_password = "passed_password"  # pragma: allowlist secret
    client = _RequestsClient(
        tccloud_username=passed_username,
        tccloud_password=passed_password,
        settings=settings,
    )
    client._set_tokens()

    spy.assert_called_once_with(client, passed_username, passed_password)
    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]


def test_environment_variables_used_for_auth_if_no_passed_values(
    monkeypatch, credentials_file, settings, mocker, patch_token_endpoint, jwt
):
    # Set environment variables
    env_username = "env_username"
    env_password = "env_password"  # pragma: allowlist secret
    monkeypatch.setenv("TCCLOUD_USERNAME", env_username, prepend=False)
    monkeypatch.setenv("TCCLOUD_PASSWORD", env_password, prepend=False)

    # Create Credentials file
    refresh_token = "credentials_file_refresh_token"
    credentials_file(jwt, refresh_token)

    spy = mocker.spy(_RequestsClient, "_tokens_from_username_password")

    settings_with_patched_envars = Settings(
        tccloud_base_directory=settings.tccloud_base_directory
    )

    # Instantiate client
    client = _RequestsClient(
        settings=settings_with_patched_envars,
    )

    client._set_tokens()

    spy.assert_called_once_with(client, env_username, env_password)
    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]


def test_credentials_file_used_for_auth_if_no_passed_values_or_envvars(
    settings, credentials_file, jwt
):
    # Create Credentials file
    refresh_token = "credentials_file_refresh_token"

    credentials_file(jwt, refresh_token)

    # Instantiate client
    client = _RequestsClient(settings=settings)
    client._set_tokens()

    assert client._access_token == jwt
    assert client._refresh_token == refresh_token


def test_username_password_requested_if_no_credentials_available_to_create_credentials_file(
    settings, monkeypatch, patch_token_endpoint, mocker
):
    # Hack using "no" for username since this will also return "no" for configuring
    # crednetials file
    username = "user_input_username"
    password = "user_input_password"  # pragma: allowlist secret

    monkeypatch.setattr("builtins.input", lambda _: username)
    monkeypatch.setattr("tccloud.http_client.getpass", lambda x: password)

    spy = mocker.spy(_RequestsClient, "_tokens_from_username_password")

    client = _RequestsClient(settings=settings)
    client._set_tokens()

    spy.assert_called_once_with(client, username, password)
    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]

    credentials_file = (
        Path(settings.tccloud_base_directory) / settings.tccloud_credentials_file
    )

    # Credentials file does not yet exist
    assert not credentials_file.is_file()


def test_write_tokens_to_credentials_file(settings):
    client = _RequestsClient(settings=settings)
    credentials_file = (
        Path(settings.tccloud_base_directory) / settings.tccloud_credentials_file
    )

    # Credentials file does not yet exist
    assert not credentials_file.is_file()

    test_access_token = "test_access_token"
    test_refresh_token = "test_refresh_token"

    client.write_tokens_to_credentials_file(test_access_token, test_refresh_token)

    assert credentials_file.is_file()

    with open(credentials_file) as f:
        data = toml.load(f)

    assert (
        data[settings.tccloud_default_credentials_profile]["access_token"]
        == test_access_token
    )
    assert (
        data[settings.tccloud_default_credentials_profile]["refresh_token"]
        == test_refresh_token
    )


def test_write_tokens_to_credentials_file_adds_new_profiles_to_credentials_file(
    settings,
):
    client = _RequestsClient(settings=settings)
    credentials_file = (
        Path(settings.tccloud_base_directory) / settings.tccloud_credentials_file
    )

    # Credentials file does not yet exist
    assert not credentials_file.is_file()

    default_access_token = "default_access_token"
    default_refresh_token = "default_refresh_token"

    client.write_tokens_to_credentials_file(default_access_token, default_refresh_token)

    assert credentials_file.is_file()

    with open(credentials_file) as f:
        data = toml.load(f)

    assert (
        data[settings.tccloud_default_credentials_profile]["access_token"]
        == default_access_token
    )
    assert (
        data[settings.tccloud_default_credentials_profile]["refresh_token"]
        == default_refresh_token
    )

    new_profile_name = "new_profile"
    new_profile_access_token = "new_profile_access_token"
    new_profile_refresh_token = "new_profile_refresh_token"

    client.write_tokens_to_credentials_file(
        new_profile_access_token, new_profile_refresh_token, profile=new_profile_name
    )

    with open(credentials_file) as f:
        data = toml.load(f)

    # Default profile still exists
    assert (
        data[settings.tccloud_default_credentials_profile]["access_token"]
        == default_access_token
    )
    assert (
        data[settings.tccloud_default_credentials_profile]["refresh_token"]
        == default_refresh_token
    )

    # New profile added
    assert data[new_profile_name]["access_token"] == new_profile_access_token
    assert data[new_profile_name]["refresh_token"] == new_profile_refresh_token


def test_write_tokens_to_credentials_file_overwrites_tokens_of_existing_profiles(
    settings,
):
    client = _RequestsClient(settings=settings)
    credentials_file = (
        Path(settings.tccloud_base_directory) / settings.tccloud_credentials_file
    )

    # Credentials file does not yet exist
    assert not credentials_file.is_file()

    original_access_token = "default_access_token"
    original_refresh_token = "default_refresh_token"

    client.write_tokens_to_credentials_file(
        original_access_token, original_refresh_token
    )

    assert credentials_file.is_file()

    with open(credentials_file) as f:
        data = toml.load(f)

    assert (
        data[settings.tccloud_default_credentials_profile]["access_token"]
        == original_access_token
    )
    assert (
        data[settings.tccloud_default_credentials_profile]["refresh_token"]
        == original_refresh_token
    )

    new_access_token = "new__access_token"
    new_refresh_token = "new_refresh_token"

    client.write_tokens_to_credentials_file(new_access_token, new_refresh_token)

    with open(credentials_file) as f:
        data = toml.load(f)

    # Default profile has new tokens
    assert (
        data[settings.tccloud_default_credentials_profile]["access_token"]
        == new_access_token
    )
    assert (
        data[settings.tccloud_default_credentials_profile]["refresh_token"]
        == new_refresh_token
    )


def test__set_tokens_removes_username_password_from_attributes(
    settings, patch_token_endpoint
):
    username = "username"
    password = "super_secret"  # pragma: allowlist secret

    client = _RequestsClient(
        settings=settings, tccloud_username=username, tccloud_password=password
    )
    assert client._tccloud_username == username
    assert client._tccloud_password == password

    client._set_tokens()

    assert client._tccloud_username is None
    assert client._tccloud_password is None

    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]


def test__refresh_tokens_called_if_access_token_expired(
    settings, patch_token_endpoint, mocker, expired_jwt
):
    original_refresh_token = "og_refresh_token"
    client = _RequestsClient(settings=settings)
    client._access_token = expired_jwt
    client._refresh_token = original_refresh_token

    spy = mocker.spy(_RequestsClient, "_refresh_tokens")

    client._get_access_token()

    spy.assert_called_once_with(client, original_refresh_token)
    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]


def test__refresh_tokens_writes_to_credentials_file_only_if_flag_set(
    settings, patch_token_endpoint, expired_jwt
):
    original_refresh_token = "my_refresh_token"

    credentials_file = (
        settings.tccloud_base_directory / settings.tccloud_credentials_file
    )
    assert not credentials_file.is_file()

    client = _RequestsClient(settings=settings)
    client._access_token = expired_jwt
    client._refresh_token = original_refresh_token

    client._refresh_tokens(original_refresh_token)

    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]
    assert not credentials_file.is_file()

    client._tokens_set_from_file = True
    client._refresh_tokens(original_refresh_token)
    assert credentials_file.is_file()

    with open(credentials_file) as f:
        data = toml.load(f)

    assert (
        data[settings.tccloud_default_credentials_profile]["access_token"]
        == patch_token_endpoint["access_token"]
    )
    assert (
        data[settings.tccloud_default_credentials_profile]["refresh_token"]
        == patch_token_endpoint["refresh_token"]
    )


def test__refresh_tokens_not_called_if_access_token_not_expired(settings, mocker, jwt):
    original_refresh_token = "og_refresh_token"

    client = _RequestsClient(settings=settings)
    client._access_token = jwt
    client._refresh_token = original_refresh_token

    spy = mocker.spy(_RequestsClient, "_refresh_tokens")

    access_token = client._get_access_token()

    spy.assert_not_called()
    assert access_token == jwt
    assert client._access_token == jwt
    assert client._refresh_token == original_refresh_token


def test__set_tokens_called_if_access_token_expired_and_no_refresh_token_set(
    settings, mocker, expired_jwt
):
    client = _RequestsClient(settings=settings)
    client._access_token = expired_jwt

    mocked = mocker.patch.object(_RequestsClient, "_set_tokens", autospec=True)

    client._get_access_token()

    mocked.assert_called_once()


def test_compute(settings, patch_compute_endpoints, water, jwt):
    client = _RequestsClient(settings=settings)
    client._access_token = jwt

    model = Model(method="B3LYP", basis="6-31g")
    atomic_input = AtomicInput(molecule=water, model=model, driver="energy")

    future_result = client.compute(atomic_input, engine="psi4")

    assert isinstance(future_result, FutureResult)
    assert future_result.task_id == patch_compute_endpoints["task_id"]
    assert future_result.client is client


def test_compute_batch(settings, patch_compute_endpoints_batch, water, jwt):
    client = _RequestsClient(settings=settings)
    client._access_token = jwt

    model = Model(method="B3LYP", basis="6-31g")
    atomic_input = AtomicInput(molecule=water, model=model, driver="energy")

    future_result = client.compute([atomic_input, atomic_input], engine="psi4")

    assert isinstance(future_result, FutureResultGroup)
    assert future_result.task_id == patch_compute_endpoints_batch["task_id"]
    assert (
        future_result.subtask_ids[0]
        == patch_compute_endpoints_batch["subtasks"][0]["task_id"]
    )
    assert future_result.client is client


def test_compute_procedure(settings, patch_compute_endpoints, water, jwt):
    client = _RequestsClient(settings=settings)
    client._access_token = jwt

    input_spec = QCInputSpecification(
        driver="gradient",
        model={"method": "b3lyp", "basis": "6-31g"},
    )

    opt_input = OptimizationInput(
        input_specification=input_spec,
        initial_molecule=water,
        protocols={"trajectory": "all"},
        keywords={"program": "terachem_pbs"},
    )

    future_result = client.compute_procedure(opt_input, "geometric")

    assert isinstance(future_result, FutureResult)
    assert future_result.task_id == patch_compute_endpoints["task_id"]
    assert future_result.client is client


def test_compute_procedure_batch(settings, patch_compute_endpoints_batch, water, jwt):
    client = _RequestsClient(settings=settings)
    client._access_token = jwt

    input_spec = QCInputSpecification(
        driver="gradient",
        model={"method": "b3lyp", "basis": "6-31g"},
    )

    opt_input = OptimizationInput(
        input_specification=input_spec,
        initial_molecule=water,
        protocols={"trajectory": "all"},
        keywords={"program": "terachem_pbs"},
    )

    future_result = client.compute_procedure(opt_input, "geometric")

    assert isinstance(future_result, FutureResultGroup)
    assert future_result.task_id == patch_compute_endpoints_batch["task_id"]
    assert (
        future_result.subtask_ids[0]
        == patch_compute_endpoints_batch["subtasks"][0]["task_id"]
    )
    assert future_result.client is client


def test_result_pending(settings, jwt, httpx_mock: HTTPXMock):
    client = _RequestsClient(settings=settings)
    client._access_token = jwt

    httpx_mock.add_response(json={"compute_status": "PENDING", "result": None})

    status, result = client.result({"task_id": "fake_id"})

    assert status == TaskStatus.PENDING
    assert result is None


def test_result_success(settings, jwt, httpx_mock: HTTPXMock):
    client = _RequestsClient(settings=settings)
    client._access_token = jwt
    atomic_result = AtomicResult.parse_file(
        Path(__file__).parent / "water.b3lyp.6-31g.energy.json"
    )
    url = re.compile(".*/compute/result")
    httpx_mock.add_response(
        url=url,
        json={"compute_status": "SUCCESS", "result": json.loads(atomic_result.json())},
    )

    status, result = client.result({"task_id": "fake_id"})

    assert status == "SUCCESS"
    assert isinstance(AtomicResult(**result), AtomicResult)


def test__decode_access_token():
    client = _RequestsClient()

    jwt = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Il9xLWdWTjlVZFRfQkdJeGgxOXJiNSJ9.eyJpc3MiOiJodHRwczovL2Rldi1tdHpsYWIudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVmYjg4MjhmMWJkYTAwMDA3NWUxNGIwYSIsImF1ZCI6Imh0dHBzOi8vdGVyYWNoZW1jbG91ZC5kZXYubXR6bGFiLmNvbSIsImlhdCI6MTYxMDU5OTcxNywiZXhwIjoxNjEwNjg2MTE3LCJhenAiOiJsUXZmS2RsZnhMRTBFOW1WRUlsNThXaTlnWDJBd1dvcCIsInNjb3BlIjoiY29tcHV0ZTpwdWJsaWMgY29tcHV0ZTpwcml2YXRlIG9mZmxpbmVfYWNjZXNzIiwiZ3R5IjoicGFzc3dvcmQiLCJwZXJtaXNzaW9ucyI6WyJjb21wdXRlOnByaXZhdGUiLCJjb21wdXRlOnB1YmxpYyJdfQ.OOV8KfmmzMIj049gzRHPqyxbQD7QfYqNT4tqLz6qUd8YmcWyc3rhcoU_We5RUfWsgN_-9w04p3KUsjUWopKO0curmdHsUVGPLg3yFsWbbjd_QgD2BOTwv_IEzGzTtx3a2tjoEepuxzbkyBWE_n2-cV9yPh0tX5p3UO9KFt1ptIE-ucsqH3liPypqR4TcUq_3pLPe_LcqUNTBrFUndZzvvxUSsdidHOekiqTL9eWC8XDqZ_x9kKSa32Whm_AMGFoAqJawUQKt13qItmoxk5xTZeSU7l3Cyi52vpnuSjG-5XAlH3pQ3yk1KUjLtq0GkWK0csmK-W7H7qMd2A9N_ZMQXQ"  # pragma: allowlist secret

    known_payload = {
        "iss": "https://dev-mtzlab.us.auth0.com/",
        "sub": "auth0|5fb8828f1bda000075e14b0a",
        "aud": "https://terachemcloud.dev.mtzlab.com",
        "iat": 1610599717,
        "exp": 1610686117,
        "azp": "lQvfKdlfxLE0E9mVEIl58Wi9gX2AwWop",  # pragma: allowlist secret
        "scope": "compute:public compute:private offline_access",
        "gty": "password",
        "permissions": ["compute:private", "compute:public"],
    }

    decoded_payload = client._decode_access_token(jwt)
    assert decoded_payload == known_payload


def test__set_tokens_gets_new_access_token_if_credentials_file_expired(
    credentials_file, expired_jwt, settings, mocker, patch_token_endpoint
):
    refresh_token = "credentials_file_refresh_token"
    credentials_file(expired_jwt, refresh_token)
    client = _RequestsClient(settings=settings)

    spy = mocker.spy(_RequestsClient, "_refresh_tokens")

    client._set_tokens()
    spy.assert_called_once_with(client, refresh_token)
    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]
