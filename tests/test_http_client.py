import sys
from pathlib import Path

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from chemcloud.config import Settings
from chemcloud.http_client import _HttpClient


@pytest.mark.asyncio
async def test_passing_username_password_are_prioritized_for_auth(
    mocker, monkeypatch, settings, credentials_file, patch_token_endpoint, jwt
):
    # Set environment variables
    monkeypatch.setenv("CHEMCLOUD_USERNAME", "env_username", prepend=False)
    monkeypatch.setenv("CHEMCLOUD_PASSWORD", "env_password", prepend=False)

    # Create Credentials file
    refresh_token = "credentials_file_refresh_token"
    credentials_file(jwt, refresh_token)

    spy = mocker.spy(_HttpClient, "_tokens_from_username_password")

    # Instantiate client
    passed_username = "passed_username"
    passed_password = "passed_password"  # pragma: allowlist secret
    client = _HttpClient(
        chemcloud_username=passed_username,
        chemcloud_password=passed_password,
        settings=settings,
    )
    await client._set_tokens()

    spy.assert_called_once_with(client, passed_username, passed_password)
    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]


@pytest.mark.asyncio
async def test_environment_variables_used_for_auth_if_no_passed_values(
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

    spy = mocker.spy(_HttpClient, "_tokens_from_username_password")

    settings_with_patched_envars = Settings(
        chemcloud_base_directory=settings.chemcloud_base_directory
    )

    # Instantiate client
    client = _HttpClient(
        settings=settings_with_patched_envars,
    )

    await client._set_tokens()

    spy.assert_called_once_with(client, env_username, env_password)
    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]


@pytest.mark.asyncio
async def test_credentials_file_used_for_auth_if_no_passed_values_or_envvars(
    settings, credentials_file, jwt
):
    # Create Credentials file
    refresh_token = "credentials_file_refresh_token"

    credentials_file(jwt, refresh_token)

    # Instantiate client
    client = _HttpClient(settings=settings)
    await client._set_tokens()

    assert client._access_token == jwt
    assert client._refresh_token == refresh_token


@pytest.mark.asyncio
async def test_username_pwd_requested_if_no_credentials_available_to_create_credentials_file(
    settings, monkeypatch, patch_token_endpoint, mocker
):
    # Hack using "no" for username since this will also return "no" for configuring
    # credentials file
    username = "user_input_username"
    password = "user_input_password"  # pragma: allowlist secret

    monkeypatch.setattr("builtins.input", lambda _: username)
    monkeypatch.setattr("chemcloud.http_client.getpass", lambda x: password)

    spy = mocker.spy(_HttpClient, "_tokens_from_username_password")

    client = _HttpClient(settings=settings)
    await client._set_tokens()

    spy.assert_called_once_with(client, username, password)
    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]

    credentials_file = (
        Path(settings.chemcloud_base_directory) / settings.chemcloud_credentials_file
    )

    # Credentials file does not yet exist
    assert not credentials_file.is_file()


def test_write_tokens_to_credentials_file(settings):
    client = _HttpClient(settings=settings)
    credentials_file = (
        Path(settings.chemcloud_base_directory) / settings.chemcloud_credentials_file
    )

    # Credentials file does not yet exist
    assert not credentials_file.is_file()

    test_access_token = "test_access_token"
    test_refresh_token = "test_refresh_token"

    client.write_tokens_to_credentials_file(test_access_token, test_refresh_token)

    assert credentials_file.is_file()

    with open(credentials_file, "rb") as f:
        data = tomllib.load(f)

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
    client = _HttpClient(settings=settings)
    credentials_file = (
        Path(settings.chemcloud_base_directory) / settings.chemcloud_credentials_file
    )

    # Credentials file does not yet exist
    assert not credentials_file.is_file()

    default_access_token = "default_access_token"
    default_refresh_token = "default_refresh_token"

    client.write_tokens_to_credentials_file(default_access_token, default_refresh_token)

    assert credentials_file.is_file()

    with open(credentials_file, "rb") as f:
        data = tomllib.load(f)

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

    with open(credentials_file, "rb") as f:
        data = tomllib.load(f)

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
    client = _HttpClient(settings=settings)
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

    with open(credentials_file, "rb") as f:
        data = tomllib.load(f)

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

    with open(credentials_file, "rb") as f:
        data = tomllib.load(f)

    # Default profile has new tokens
    assert (
        data[settings.chemcloud_credentials_profile]["access_token"] == new_access_token
    )
    assert (
        data[settings.chemcloud_credentials_profile]["refresh_token"]
        == new_refresh_token
    )


@pytest.mark.asyncio
async def test__set_tokens_removes_username_password_from_attributes(
    settings, patch_token_endpoint
):
    username = "username"
    password = "super_secret"  # pragma: allowlist secret

    client = _HttpClient(
        settings=settings, chemcloud_username=username, chemcloud_password=password
    )
    assert client._chemcloud_username == username
    assert client._chemcloud_password == password

    await client._set_tokens()

    assert client._chemcloud_username is None
    assert client._chemcloud_password is None

    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]


@pytest.mark.asyncio
async def test__refresh_tokens_called_if_access_token_expired(
    settings, patch_token_endpoint, mocker, expired_jwt
):
    original_refresh_token = "og_refresh_token"
    client = _HttpClient(settings=settings)
    client._access_token = expired_jwt
    client._refresh_token = original_refresh_token

    spy = mocker.spy(_HttpClient, "_refresh_tokens")

    await client.get_access_token()

    spy.assert_called_once_with(client, original_refresh_token)
    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]


@pytest.mark.asyncio
async def test__refresh_tokens_writes_to_credentials_file_only_if_flag_set(
    settings, patch_token_endpoint, expired_jwt
):
    original_refresh_token = "my_refresh_token"

    credentials_file = (
        settings.chemcloud_base_directory / settings.chemcloud_credentials_file
    )
    assert not credentials_file.is_file()

    client = _HttpClient(settings=settings)
    client._access_token = expired_jwt
    client._refresh_token = original_refresh_token

    await client._refresh_tokens(original_refresh_token)

    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]
    assert not credentials_file.is_file()

    client._tokens_set_from_file = True
    await client._refresh_tokens(original_refresh_token)
    assert credentials_file.is_file()

    with open(credentials_file, "rb") as f:
        data = tomllib.load(f)

    assert (
        data[settings.chemcloud_credentials_profile]["access_token"]
        == patch_token_endpoint["access_token"]
    )
    assert (
        data[settings.chemcloud_credentials_profile]["refresh_token"]
        == patch_token_endpoint["refresh_token"]
    )


@pytest.mark.asyncio
async def test__refresh_tokens_not_called_if_access_token_not_expired(
    settings, mocker, jwt
):
    original_refresh_token = "og_refresh_token"

    client = _HttpClient(settings=settings)
    client._access_token = jwt
    client._refresh_token = original_refresh_token

    spy = mocker.spy(_HttpClient, "_refresh_tokens")

    access_token = await client.get_access_token()

    spy.assert_not_called()
    assert access_token == jwt
    assert client._access_token == jwt
    assert client._refresh_token == original_refresh_token


@pytest.mark.asyncio
async def test__set_tokens_called_if_access_token_expired_and_no_refresh_token_set(
    settings, mocker, expired_jwt
):
    client = _HttpClient(settings=settings)
    client._access_token = expired_jwt

    mocked = mocker.patch.object(_HttpClient, "_set_tokens", autospec=True)

    await client.get_access_token()

    mocked.assert_called_once()


def test__decode_access_token():
    client = _HttpClient()

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


@pytest.mark.asyncio
async def test__set_tokens_gets_new_access_token_if_credentials_file_expired(
    credentials_file, expired_jwt, settings, mocker, patch_token_endpoint
):
    refresh_token = "credentials_file_refresh_token"
    credentials_file(expired_jwt, refresh_token)
    client = _HttpClient(settings=settings)

    spy = mocker.spy(_HttpClient, "_refresh_tokens")

    await client._set_tokens()
    spy.assert_called_once_with(client, refresh_token)
    assert client._access_token == patch_token_endpoint["access_token"]
    assert client._refresh_token == patch_token_endpoint["refresh_token"]
