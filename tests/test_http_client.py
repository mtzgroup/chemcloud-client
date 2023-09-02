import json
import re
from pathlib import Path

import toml
from pytest_httpx import HTTPXMock
from qcio import Model, ProgramInput, SinglePointOutput

from chemcloud.config import Settings
from chemcloud.http_client import _RequestsClient
from chemcloud.models import (
    GROUP_ID_PREFIX,
    FutureResult,
    FutureResultGroup,
    TaskStatus,
)


def test_passing_username_password_are_prioritized_for_auth(
    mocker, monkeypatch, settings, credentials_file, patch_token_endpoint, jwt
):
    # Set environment variables
    monkeypatch.setenv("CHEMCLOUD_USERNAME", "env_username", prepend=False)
    monkeypatch.setenv("CHEMCLOUD_PASSWORD", "env_password", prepend=False)

    # Create Credentials file
    refresh_token = "credentials_file_refresh_token"
    credentials_file(jwt, refresh_token)

    spy = mocker.spy(_RequestsClient, "_tokens_from_username_password")

    # Instantiate client
    passed_username = "passed_username"
    passed_password = "passed_password"  # pragma: allowlist secret
    client = _RequestsClient(
        chemcloud_username=passed_username,
        chemcloud_password=passed_password,
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
    monkeypatch.setenv("CHEMCLOUD_USERNAME", env_username, prepend=False)
    monkeypatch.setenv("CHEMCLOUD_PASSWORD", env_password, prepend=False)

    # Create Credentials file
    refresh_token = "credentials_file_refresh_token"
    credentials_file(jwt, refresh_token)

    spy = mocker.spy(_RequestsClient, "_tokens_from_username_password")

    settings_with_patched_envars = Settings(
        chemcloud_base_directory=settings.chemcloud_base_directory
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


def test_username_pwd_requested_if_no_credentials_available_to_create_credentials_file(
    settings, monkeypatch, patch_token_endpoint, mocker
):
    # Hack using "no" for username since this will also return "no" for configuring
    # credentials file
    username = "user_input_username"
    password = "user_input_password"  # pragma: allowlist secret

    monkeypatch.setattr("builtins.input", lambda _: username)
    monkeypatch.setattr("chemcloud.http_client.getpass", lambda x: password)

    spy = mocker.spy(_RequestsClient, "_tokens_from_username_password")

    client = _RequestsClient(settings=settings)
    client._set_tokens()

    spy.assert_called_once_with(client, username, password)
    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]

    credentials_file = (
        Path(settings.chemcloud_base_directory) / settings.chemcloud_credentials_file
    )

    # Credentials file does not yet exist
    assert not credentials_file.is_file()


def test_write_tokens_to_credentials_file(settings):
    client = _RequestsClient(settings=settings)
    credentials_file = (
        Path(settings.chemcloud_base_directory) / settings.chemcloud_credentials_file
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
        data[settings.chemcloud_credentials_profile]["access_token"]
        == test_access_token
    )
    assert (
        data[settings.chemcloud_credentials_profile]["refresh_token"]
        == test_refresh_token
    )


def test_write_tokens_to_credentials_file_adds_new_profiles_to_credentials_file(
    settings,
):
    client = _RequestsClient(settings=settings)
    credentials_file = (
        Path(settings.chemcloud_base_directory) / settings.chemcloud_credentials_file
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
        data[settings.chemcloud_credentials_profile]["access_token"]
        == default_access_token
    )
    assert (
        data[settings.chemcloud_credentials_profile]["refresh_token"]
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
        data[settings.chemcloud_credentials_profile]["access_token"]
        == default_access_token
    )
    assert (
        data[settings.chemcloud_credentials_profile]["refresh_token"]
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
        Path(settings.chemcloud_base_directory) / settings.chemcloud_credentials_file
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
        data[settings.chemcloud_credentials_profile]["access_token"]
        == original_access_token
    )
    assert (
        data[settings.chemcloud_credentials_profile]["refresh_token"]
        == original_refresh_token
    )

    new_access_token = "new__access_token"
    new_refresh_token = "new_refresh_token"

    client.write_tokens_to_credentials_file(new_access_token, new_refresh_token)

    with open(credentials_file) as f:
        data = toml.load(f)

    # Default profile has new tokens
    assert (
        data[settings.chemcloud_credentials_profile]["access_token"] == new_access_token
    )
    assert (
        data[settings.chemcloud_credentials_profile]["refresh_token"]
        == new_refresh_token
    )


def test__set_tokens_removes_username_password_from_attributes(
    settings, patch_token_endpoint
):
    username = "username"
    password = "super_secret"  # pragma: allowlist secret

    client = _RequestsClient(
        settings=settings, chemcloud_username=username, chemcloud_password=password
    )
    assert client._chemcloud_username == username
    assert client._chemcloud_password == password

    client._set_tokens()

    assert client._chemcloud_username is None
    assert client._chemcloud_password is None

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
        settings.chemcloud_base_directory / settings.chemcloud_credentials_file
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
        data[settings.chemcloud_credentials_profile]["access_token"]
        == patch_token_endpoint["access_token"]
    )
    assert (
        data[settings.chemcloud_credentials_profile]["refresh_token"]
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

    Model(method="B3LYP", basis="6-31g")
    atomic_input = ProgramInput(
        molecule=water, model={"method": "b3lyp", "basis": "6-31g"}, calctype="energy"
    )

    future_result = client.compute(atomic_input, {"program": "psi4"})
    assert isinstance(future_result, FutureResult)
    assert future_result.id == patch_compute_endpoints
    assert future_result.client is client


def test_compute_batch(settings, patch_compute_endpoints, water, jwt):
    client = _RequestsClient(settings=settings)
    client._access_token = jwt

    model = Model(method="B3LYP", basis="6-31g")
    atomic_input = ProgramInput(molecule=water, model=model, calctype="energy")

    future_result = client.compute([atomic_input, atomic_input], {"program": "psi4"})

    assert isinstance(future_result, FutureResultGroup)
    assert future_result.id == f"{GROUP_ID_PREFIX}{patch_compute_endpoints}"
    assert future_result.client is client


def test_result_pending(settings, jwt, httpx_mock: HTTPXMock):
    client = _RequestsClient(settings=settings)
    client._access_token = jwt

    httpx_mock.add_response(json={"state": "PENDING", "result": None})

    status, result = client.output("fake_id")

    assert status == TaskStatus.PENDING
    assert result is None


def test_result_success(settings, jwt, httpx_mock: HTTPXMock):
    client = _RequestsClient(settings=settings)
    client._access_token = jwt
    spo = SinglePointOutput.model_validate_json(
        (Path(__file__).parent / "water.b3lyp.6-31g.energy.json").read_text()
    )
    url = re.compile(".*/compute/output")
    httpx_mock.add_response(
        url=url,
        json={"state": "SUCCESS", "result": json.loads(spo.model_dump_json())},
    )

    status, result = client.output("fake_id")

    assert status == "SUCCESS"
    assert isinstance(SinglePointOutput(**result), SinglePointOutput)


def test__decode_access_token():
    client = _RequestsClient()

    jwt = (Path(__file__).resolve().parent / "jwt.txt").read_text()

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
