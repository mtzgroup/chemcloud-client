import json
import sys
from base64 import urlsafe_b64decode
from getpass import getpass
from pathlib import Path
from time import time
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w
from qcio.utils import json_dumps

from chemcloud.models import FutureOutput, FutureOutputGroup

from .config import Settings, settings
from .models import QCIOInputsOrList


class _RequestsClient:
    """Interface for making http requests to ChemCloud.

    This class should never be instantiated by end users. End users should use the
    CCClient class to interact with ChemCloud.

    Main Features:
        - Manages credentials for making authenticated requests.
        - All public methods in should enforce a contract of returning python data
            objects to the caller rather than dicts or request/response objects.
        - public methods:
            - hello_world()
            - compute()
            - output()
            - write_tokens_to_credentials_file()

    """

    def __init__(
        self,
        *,
        chemcloud_username: Optional[str] = None,
        chemcloud_password: Optional[str] = None,
        profile: Optional[str] = None,
        settings: Settings = settings,
        chemcloud_domain: Optional[str] = None,
    ):
        self._chemcloud_username = chemcloud_username
        self._chemcloud_password = chemcloud_password
        self._settings = settings
        self._profile = profile or settings.chemcloud_credentials_profile
        self._access_token: str = ""
        self._refresh_token: str = ""
        self._chemcloud_domain = chemcloud_domain or settings.chemcloud_domain
        # If set to True future refresh_tokens calls will also write new tokens to
        # Credentials file
        self._tokens_set_from_file: bool = False

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self._chemcloud_domain}, profile={self._profile})"
        )

    def _set_tokens(self) -> None:
        """Set self._access_token and self._refresh_token"""
        un = self._chemcloud_username or self._settings.chemcloud_username
        pw = self._chemcloud_password or self._settings.chemcloud_password
        credentials_file = (
            self._settings.chemcloud_base_directory
            / self._settings.chemcloud_credentials_file
        )

        unauth_msg = "You must authenticate with ChemCloud to make this request."

        if un and pw:  # username/password passed in or found in environment
            access_token, refresh_token = self._tokens_from_username_password(un, pw)

        elif credentials_file.is_file():  # Look for tokens in credentials file
            with open(credentials_file, "rb") as f:
                credentials = tomllib.load(f)
            try:
                access_token = credentials[self._profile]["access_token"]
                refresh_token = credentials[self._profile]["refresh_token"]
            except KeyError:
                print(unauth_msg)
                access_token, refresh_token = self._set_tokens_from_user_input()
            else:
                self._tokens_set_from_file = True
                if self._expired_access_token(access_token):
                    access_token, refresh_token = self._refresh_tokens(refresh_token)
        else:
            print(unauth_msg)
            access_token, refresh_token = self._set_tokens_from_user_input()

        # Remove sensitive credentials from object
        self._chemcloud_username, self._chemcloud_password = None, None

        self._access_token, self._refresh_token = access_token, refresh_token

    def _set_tokens_from_user_input(self):
        """Request user to input username/password to get access tokens"""
        while True:
            msg = "Please enter your ChemCloud"
            username = input(msg + " username: ")
            password = getpass(msg + " password: ")

            try:
                print("Authenticating...")
                return self._tokens_from_username_password(username, password)
            except httpx.HTTPStatusError as e:
                print(e)
                print(
                    "Login Failed! Did you enter your credentials correctly? If you "
                    "do not have a ChemCloud account please visit "
                    f"{self._chemcloud_domain}/signup to create an account."
                )

    def _get_access_token(self) -> str:
        """Top-level method to get an access token for authenticated requests"""
        if self._access_token:
            # Check Expiration
            if self._expired_access_token(self._access_token):
                print("Refreshing Access Token...")
                if self._refresh_token:
                    self._refresh_tokens(self._refresh_token)
                else:
                    self._set_tokens()
            else:
                return self._access_token
        else:
            self._set_tokens()

        return self._access_token

    def write_tokens_to_credentials_file(
        self,
        access_token: str,
        refresh_token: str,
        *,
        profile: str = settings.chemcloud_credentials_profile,
    ) -> None:
        """Writes access_token and refresh_token to configuration file"""
        assert (
            access_token and refresh_token
        ), "You must pass an access_token and refresh_token"

        credentials_file = (
            Path(self._settings.chemcloud_base_directory)
            / self._settings.chemcloud_credentials_file
        )

        if credentials_file.is_file():
            with open(credentials_file, "rb") as f:
                credentials = tomllib.load(f)
        else:
            credentials_file.parent.mkdir(parents=True, exist_ok=True)
            credentials = {}

        credentials[profile] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
        with open(credentials_file, "wb") as f:
            tomli_w.dump(credentials, f)

    def _request(
        self,
        method: str,
        route: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        api_call: bool = True,
    ):
        """Make HTTP request"""
        url = (
            f"{self._chemcloud_domain}"
            f"{self._settings.chemcloud_api_version_prefix if api_call else ''}{route}"
        )
        request = httpx.Request(
            method,
            url,
            headers=headers,
            data=data,
            params=params,
        )
        # Longer read timeouts for large batches of files
        with httpx.Client(timeout=httpx.Timeout(5.0, read=20.0)) as client:
            response = client.send(request)
        response.raise_for_status()
        return response.json()

    def _authenticated_request(self, method: str, route: str, **kwargs):
        """Make authenticated HTTP request"""
        kwargs["headers"] = kwargs.get("headers", {})
        access_token = self._get_access_token()
        kwargs["headers"]["Authorization"] = f"Bearer {access_token}"
        return self._request(
            method,
            route,
            **kwargs,
        )

    def _tokens_from_username_password(
        self, username: str, password: str
    ) -> Tuple[str, str]:
        """Exchanges username/password for access_token and refresh_token"""
        data = {
            "grant_type": "password",
            "username": username,
            "password": password,
            # get refresh_token
            "scope": "offline_access compute:public compute:private",
        }
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = self._request(
            "post",
            "/oauth/token",
            headers=headers,
            data=data,
        )

        return response["access_token"], response["refresh_token"]

    def _refresh_tokens(self, refresh_token: str) -> Tuple[str, str]:
        """Get new access and refresh tokens."""
        data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = self._request(
            "post",
            "/oauth/token",
            headers=headers,
            data=data,
        )
        # Return new refresh_token if issued, keep current token if no new token
        # issued. New refresh_token issued if refresh token rotation activated on
        # Auth0 backend.
        self._access_token, self._refresh_token = (
            response["access_token"],
            response.get("refresh_token", refresh_token),
        )
        if self._tokens_set_from_file:
            # If tokens were originally set from a credentials file then update that
            # file with the new values
            self.write_tokens_to_credentials_file(
                self._access_token, self._refresh_token, profile=self._profile
            )
        return self._access_token, self._refresh_token

    def _expired_access_token(self, jwt: str) -> bool:
        """Checks expiration of JWT (access token)"""
        payload = self._decode_access_token(jwt)
        return payload["exp"] <= (
            int(time()) + self._settings.chemcloud_access_token_expiration_buffer
        )

    @staticmethod
    def _decode_access_token(jwt: str) -> Dict[str, Any]:
        """Decode jwt string and return dictionary of payload claims."""
        payload = jwt.split(".")[1]
        encoded_payload = payload.encode("ascii")

        # Helper section taken from python-jose.utils.base64url_decode
        rem = len(encoded_payload) % 4

        if rem > 0:
            encoded_payload += b"=" * (4 - rem)

        json_string = urlsafe_b64decode(encoded_payload).decode("utf-8")
        return json.loads(json_string)

    def _result_id_to_future_result(self, input_data, result_id):
        if isinstance(input_data, list):
            return FutureOutputGroup(task_id=result_id, client=self)
        return FutureOutput(task_id=result_id, client=self)

    def compute(
        self,
        inp_obj: QCIOInputsOrList,
        params: Optional[Dict[str, Any]] = None,
    ) -> Union[FutureOutput, FutureOutputGroup]:
        """Submit a computation to ChemCloud"""
        result_id = self._authenticated_request(
            "post",
            "/compute",
            data=json_dumps(inp_obj),  # type: ignore
            params=params or {},
        )
        return self._result_id_to_future_result(inp_obj, result_id)

    def output(
        self,
        task_id: str,
    ) -> Tuple[str, Union[Optional[Any], Optional[List[Any]]]]:
        """Check the output of a compute job, returns status and output (if available).

        Parameters:
            result_id: The ID of the result.

        Endpoint returns:
            class TaskResult(BaseModel):
                compute_status: TaskStatus (str)
                result: Optional[Union[PossibleResults, List[PossibleResults]]] = None
        """
        response = self._authenticated_request("get", f"/compute/output/{task_id}")

        return response["status"], response["program_output"]

    def hello_world(self, name: Optional[str] = None):
        """Ping hello-world endpoint on ChemCloud"""
        return self._request(
            "get", "/hello-world", params={"name": name}, api_call=False
        )
