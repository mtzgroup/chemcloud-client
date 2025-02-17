import asyncio
import json
import logging
import sys
from base64 import urlsafe_b64decode
from getpass import getpass
from pathlib import Path
from time import time
from typing import Any, Optional, Union
from urllib.parse import urlencode

import httpx
import tomli_w
from pydantic import BaseModel
from qcio.utils import json_dumps

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from .config import Settings, settings

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class _HttpClient:
    """
    Internal, asynchronous HTTP client for interacting with the ChemCloud API.

    Provides run_parallel_requests method as a synchronous API for external consumers.

    Responsibilities:
      - Handle authentication (token management, refresh, etc.)
      - Make HTTP requests (with retries, timeouts, etc.)
      - Return raw JSON/dict data for the domain layer to process.

    This class should not contain any domain-specific logic.
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
        self._profile = profile or self._settings.chemcloud_credentials_profile
        self._access_token: str = ""
        self._refresh_token: str = ""
        self._chemcloud_domain = chemcloud_domain or self._settings.chemcloud_domain
        self._tokens_set_from_file: bool = False
        self._httpx_timeout = httpx.Timeout(
            self._settings.chemcloud_timeout, read=self._settings.chemcloud_read_timeout
        )
        self._async_client = httpx.AsyncClient(timeout=self._httpx_timeout)
        # Use an asyncio lock to ensure only one token refresh happens at a time.
        # Must create lock when even loop is active to setting to None here.
        self._token_refresh_lock: Optional[asyncio.Lock] = None

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self._chemcloud_domain}, profile={self._profile})"
        )

    async def _request_async(
        self,
        method: str,
        route: str,
        *,
        headers: Optional[dict[str, str]] = None,
        data: Optional[Union[dict[str, Any], str]] = None,
        params: Optional[dict[str, Any]] = None,
        api_call: bool = True,
        max_attempts: int = 3,
        backoff_factor: float = 1.0,
    ) -> Any:
        """Asynchronous HTTP request with retry logic."""
        url, content = self._build_url_and_content(route, data, api_call, headers)

        # Retry for RequestErrors (non HTTPStatusErrors)
        for attempt in range(1, max_attempts + 1):
            try:
                response = await self._async_client.request(
                    method, url, headers=headers, content=content, params=params
                )
                logger.debug(
                    f"Received response (attempt {attempt}): {response.status_code}"
                )

                response.raise_for_status()
                return response.json()
            except httpx.RequestError as exc:
                logger.error(f"Request error on attempt {attempt} for {url}: {exc}")
                if attempt == max_attempts:
                    raise
                # Exponential backoff
                sleep_time = backoff_factor * 2**attempt
                logger.debug(f"Retrying in {sleep_time} seconds...")
                await asyncio.sleep(sleep_time)

    async def _authenticated_request_async(
        self, method: str, route: str, **kwargs
    ) -> Any:
        """Asynchronous version of _authenticated_request."""
        auth_kwargs = await self._add_auth_headers(**kwargs)
        return await self._request_async(method, route, **auth_kwargs)

    async def _run_parallel_requests_async(
        self,
        coroutines: list[Any],
        concurrency: Optional[int] = None,
        return_exceptions: bool = False,
    ) -> list[Any]:
        """Async API to run multiple coroutines concurrently."""
        semaphore = asyncio.Semaphore(
            concurrency or self._settings.chemcloud_concurrency
        )

        async def sem_task(coro):
            async with semaphore:
                return await coro

        tasks = [sem_task(coro) for coro in coroutines]
        return await asyncio.gather(*tasks, return_exceptions=return_exceptions)

    def run_parallel_requests(
        self,
        coroutines: list[Any],
        concurrency: Optional[int] = None,
        return_exceptions: bool = False,
    ) -> list[Any]:
        """Synchronous API to run multiple coroutines concurrently."""
        # Create a fresh AsyncClient so that it's bound to the new event loop.
        client = httpx.AsyncClient(timeout=self._httpx_timeout)

        # Temporarily swap out the persistent client
        original_async_client = self._async_client
        self._async_client = client

        try:
            return asyncio.run(
                self._run_parallel_requests_async(
                    coroutines, concurrency, return_exceptions
                )
            )
        finally:
            self._async_client = original_async_client

    def _build_url_and_content(
        self,
        route: str,
        data: Optional[Any],
        api_call: bool,
        headers: Optional[dict[str, str]] = None,
    ) -> tuple[str, Union[str, bytes]]:
        """Builds URL and serializes request content appropriately."""
        url = (
            f"{self._chemcloud_domain}"
            f"{self._settings.chemcloud_api_version_prefix if api_call else ''}{route}"
        )

        # Auth requests do not use JSON content type.
        if (
            headers
            and headers.get("content-type", "").lower()
            == "application/x-www-form-urlencoded"
        ):
            content = urlencode(data) if data else ""
        # All other requests serialize data as JSON
        else:
            content = (
                json_dumps(data)
                if isinstance(data, (BaseModel, list))
                else json.dumps(data or {})
            )

        return url, content

    async def _add_auth_headers(self, **kwargs) -> Any:
        """Add authorization header to request headers."""
        kwargs["headers"] = kwargs.get("headers", {})
        token = await self.get_access_token()
        kwargs["headers"]["Authorization"] = f"Bearer {token}"
        return kwargs

    async def get_access_token(self) -> str:
        """
        Returns a valid access token asynchronously.
        Uses a lock to ensure only one refresh occurs at a time.
        """
        if self._access_token and not self._is_token_expired(self._access_token):
            logger.debug("Access token is valid, returning cached token.")
            return self._access_token

        # Lazily create the lock in an async context where an event loop is active.
        if self._token_refresh_lock is None:
            self._token_refresh_lock = asyncio.Lock()

        async with self._token_refresh_lock:
            # Double-check after acquiring the lock in case another task refreshed it.
            if self._access_token and not self._is_token_expired(self._access_token):
                logger.debug(
                    "Access token refreshed by another coroutine, returning updated token."
                )
                return self._access_token

            if self._refresh_token:
                logger.info(
                    "Access token expired. Refreshing tokens using refresh token."
                )
                await self._refresh_tokens(self._refresh_token)
            else:
                logger.info(f"No refresh token set.")
                await self._set_tokens()

            return self._access_token

    async def _refresh_tokens(self, refresh_token: str) -> None:
        """Get new access and refresh tokens asynchronously."""
        logger.info("Refreshing tokens...")
        data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = await self._request_async(
            "post", "/oauth/token", headers=headers, data=data
        )
        # Return new refresh_token if issued, keep current token if no new token
        # issued. New refresh_token issued if refresh token rotation activated on
        # Auth0 backend.
        self._access_token = response["access_token"]
        self._refresh_token = response.get("refresh_token", refresh_token)
        if self._tokens_set_from_file:  # tokens originally set from file
            self.write_tokens_to_credentials_file(
                self._access_token, self._refresh_token, profile=self._profile
            )

    async def _set_tokens(self) -> None:
        """
        Sets self._access_token and self._refresh_token.

        Initializes tokens by one of the following (in order of precedence):
            1. If username and password are passed in, use those to get tokens.
            2. If username and password are found in the environment, use those.
            3. If tokens are found in the credentials file, use those (refresh if
                expired).
            4. If none of the above, ask the user to input username and password (tokens
                will not be saved to credentials file for future sessions).
        """
        logger.info("Attempting to set tokens.")

        un = self._chemcloud_username or self._settings.chemcloud_username
        pw = self._chemcloud_password or self._settings.chemcloud_password
        credentials_file = (
            self._settings.chemcloud_base_directory
            / self._settings.chemcloud_credentials_file
        )

        unauth_msg = (
            "You must authenticate with ChemCloud to make this request.\n"
            f"If you don't have an account, please signup at: {self._chemcloud_domain}/signup"
        )

        if un and pw:  # Passed to __init__ or environment credentials.
            logger.info(
                "Using username and password passed to __init__ or found in environment to create tokens."
            )
            (
                self._access_token,
                self._refresh_token,
            ) = await self._tokens_from_username_password(un, pw)
            # Remove sensitive information if passed to __init__.
            self._chemcloud_username, self._chemcloud_password = None, None

        elif credentials_file.is_file():
            with open(credentials_file, "rb") as f:
                credentials = tomllib.load(f)
            try:
                self._access_token = credentials[self._profile]["access_token"]
                self._refresh_token = credentials[self._profile]["refresh_token"]
            except KeyError:
                logger.info("Profile not found in credentials file.")
                print(unauth_msg)
                (
                    self._access_token,
                    self._refresh_token,
                ) = await self._set_tokens_from_user_input()
            else:
                logger.info("Setting tokens from credentials file.")
                self._tokens_set_from_file = True
                if self._is_token_expired(self._access_token):
                    await self._refresh_tokens(self._refresh_token)
        else:
            print(unauth_msg)
            (
                self._access_token,
                self._refresh_token,
            ) = await self._set_tokens_from_user_input()

    async def _set_tokens_from_user_input(self) -> tuple[str, str]:
        """Request user to input credentials until authentication succeeds."""
        while True:
            msg = "Please enter your ChemCloud"
            email_address = input(f"{msg} email address: ")
            password = getpass(f"{msg} password: ")

            try:
                print("Authenticating...")
                access_token, refresh_token = await self._tokens_from_username_password(
                    email_address, password
                )
            except httpx.HTTPStatusError as e:
                print(e)
                print(
                    "Login Failed! Did you enter your credentials correctly? "
                    f"Visit {self._chemcloud_domain}/signup to create an account."
                )
            else:
                print("Success!")
                # Ask user if they want to write tokens to credentials file.
                write_to_file = input(
                    "Would you like to save these credentials for future sessions? (y/n): "
                )
                if write_to_file.lower() == "y":
                    self.write_tokens_to_credentials_file(
                        access_token, refresh_token, profile=self._profile
                    )
                return access_token, refresh_token

    async def _tokens_from_username_password(
        self, username: str, password: str
    ) -> tuple[str, str]:
        """Exchanges username/password for access_token and refresh_token asynchronously."""
        data = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": "offline_access compute:public compute:private",
        }
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = await self._request_async(
            "post", "/oauth/token", headers=headers, data=data
        )
        return response["access_token"], response["refresh_token"]

    def _is_token_expired(self, jwt: str) -> bool:
        payload = self._decode_access_token(jwt)
        return payload["exp"] <= (
            int(time()) + self._settings.chemcloud_access_token_expiration_buffer
        )

    @staticmethod
    def _decode_access_token(jwt: str) -> dict[str, Any]:
        """Decode jwt string and return dictionary of payload claims."""
        payload = jwt.split(".")[1]
        encoded_payload = payload.encode("ascii")
        rem = len(encoded_payload) % 4
        if rem > 0:
            encoded_payload += b"=" * (4 - rem)
        json_string = urlsafe_b64decode(encoded_payload).decode("utf-8")
        return json.loads(json_string)

    def write_tokens_to_credentials_file(
        self,
        access_token: str,
        refresh_token: str,
        *,
        profile: Optional[str] = None,
    ) -> None:
        """Writes access_token and refresh_token to configuration file"""
        assert access_token and refresh_token, "Both tokens must be provided"
        profile = profile or self._settings.chemcloud_credentials_profile

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
