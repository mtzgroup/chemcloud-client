from pathlib import Path
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Base Settings configuration. Do not instantiate directly, use settings object on module"""

    chemcloud_username: Optional[str] = None
    chemcloud_password: Optional[str] = None
    chemcloud_base_directory: Path = Path.home() / ".chemcloud"
    chemcloud_credentials_file: str = "credentials"
    chemcloud_access_token_expiration_buffer: int = 15
    chemcloud_domain: str = "https://chemcloud.mtzlab.com"
    chemcloud_api_version_prefix: str = "/api/v1"
    chemcloud_default_credentials_profile: str = "default"
    tcfe_keywords: str = "tcfe:keywords"


settings = Settings()
