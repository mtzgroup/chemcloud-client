from typing import Dict, List, Optional

from .config import settings
from .http_client import _RequestsClient
from .models import AtomicInput, FutureResult


class TCClient:
    def __init__(
        self,
        *,
        tccloud_username: Optional[str] = None,
        tccloud_password: Optional[str] = None,
        profile: Optional[str] = None,
        tccloud_domain: Optional[str] = None,
    ):
        self._client = _RequestsClient(
            tccloud_username=tccloud_username,
            tccloud_password=tccloud_password,
            profile=profile,
            tccloud_domain=tccloud_domain,
        )
        self._openapi_spec: Optional[Dict] = None

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._client._tccloud_domain}, profile={self.profile})"

    def _set_openapi_specification(self):
        """Gets OpenAPI specification from TeraChem Cloud Server"""
        self._openapi_spec = self._client._request(
            "get", "/openapi.json", api_call=False
        )

    @property
    def profile(self):
        """Profile being used for authentication with TeraChem Cloud"""
        return self._client._profile

    @property
    def supported_engines(self) -> Optional[List[str]]:
        """Compute engines currently supported by TeraChem Cloud"""
        if not self._openapi_spec:
            self._set_openapi_specification()
        try:
            assert self._openapi_spec is not None
            engines = self._openapi_spec["components"]["schemas"]["SupportedEngines"][
                "enum"
            ]
        except IndexError:
            print("Cannot locate currently supported engines.")
            engines = None
        return engines

    def hello_world(self):
        """A simple endpoint to check connectivity to TeraChem Cloud"""
        return self._client.hello_world()

    def compute(self, atomic_input: AtomicInput, engine: str) -> FutureResult:
        """Submit a computation to TeraChem Cloud"""
        if self.supported_engines is not None:
            assert (
                engine in self.supported_engines
            ), f"Please use one of the following engines: {self.supported_engines}"
        return self._client.compute(atomic_input, engine)

    def configure(self, profile: str = settings.tccloud_default_credentials_profile):
        """Configure credentials file with tokens"""
        access_token, refresh_token = self._client._set_tokens_from_user_input()
        self._client.write_tokens_to_credentials_file(
            access_token, refresh_token, profile=profile
        )
        print(
            f"'{profile}' profile configured! Username/password not required for future use of TCClient"
        )
