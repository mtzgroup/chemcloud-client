import json
import re
from base64 import b64encode
from pathlib import Path
from time import time

import pytest
import tomli_w
from pytest_httpx import HTTPXMock
from qcio import ProgramInput, Structure

from chemcloud.config import Settings


def _jwt_from_payload(payload: dict[str, str]) -> str:
    """Convert payload to fake JWT"""
    b64_encoded_access_token = b64encode(json.dumps(payload).encode("utf-8")).decode(
        "utf-8"
    )
    return f"header.{b64_encoded_access_token}.signature"


@pytest.fixture(scope="function")
def settings(tmp_path):
    test_settings = {"chemcloud_base_directory": tmp_path}
    return Settings(**test_settings)


@pytest.fixture
def credentials_file(settings):
    """Fixture for writing credentials files"""

    def _write_credentials_file(
        access_token: str,
        refresh_token: str = "credentials_file_refresh_token",
        profile: str = settings.chemcloud_credentials_profile,
    ):
        credentials = {
            profile: {"access_token": access_token, "refresh_token": refresh_token}
        }
        credentials_file = (
            settings.chemcloud_base_directory / settings.chemcloud_credentials_file
        )
        with open(credentials_file, "wb+") as f:
            tomli_w.dump(credentials, f)

    return _write_credentials_file


@pytest.fixture
def patch_token_endpoint(httpx_mock: HTTPXMock):
    """Patch httpx methods against /oauth/token endpoint"""
    PATCH_VALUES = {
        "access_token": "fake_access_token",
        "refresh_token": "fake_refresh_token",
        "task_id": "fake_task_id",
    }

    # Patch /oath/token
    token_endpoint = re.compile(r".*/oauth/token")
    httpx_mock.add_response(
        url=token_endpoint,
        json={
            "access_token": PATCH_VALUES["access_token"],
            "refresh_token": PATCH_VALUES["refresh_token"],
        },
        is_reusable=True,
    )

    yield PATCH_VALUES


@pytest.fixture
def patch_compute_endpoints(httpx_mock: HTTPXMock):
    """Patch httpx methods against /compute endpoint"""
    PATCH_VALUES = "fake_task_id"

    compute_endpoint = re.compile(r".*/compute*")
    httpx_mock.add_response(url=compute_endpoint, json=PATCH_VALUES, is_reusable=True)

    yield PATCH_VALUES


@pytest.fixture
def patch_openapi_endpoint(httpx_mock: HTTPXMock):
    """Patch httpx methods against /openapi endpoint"""
    httpx_mock.add_response(
        url=re.compile(r".*/openapi\.json$"),
        json={
            "components": {
                "schemas": {"SupportedPrograms": {"enum": ["psi4", "terachem"]}}
            }
        },
        is_reusable=True,
    )


@pytest.fixture
def water():
    return Structure.open(Path(__file__).parent / "water.json")


@pytest.fixture
def jwt(settings):
    payload = {
        "exp": int(time() + settings.chemcloud_access_token_expiration_buffer) + 10,
    }
    return _jwt_from_payload(payload)


@pytest.fixture
def expired_jwt(settings):
    payload = {"exp": int(time()) - 1}
    return _jwt_from_payload(payload)


@pytest.fixture
def prog_input(water):
    """Function that returns ProgramInput of calctype."""

    return ProgramInput(
        structure=water,
        calctype="energy",
        model={"method": "hf", "basis": "sto-3g"},
        keywords={
            "maxiter": 100,
            "purify": "no",
            "some-bool": False,
            "displacement": 1e-3,
            "thermo_temp": 298.15,
        },
    )
