from pathlib import Path
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Base Settings configuration. Do not instantiate directly, use settings object on module"""

    tccloud_username: Optional[str] = None
    tccloud_password: Optional[str] = None
    tccloud_base_directory: Path = Path.home() / ".tccloud"
    tccloud_credentials_file: str = "credentials"
    tccloud_access_token_expiration_buffer: int = 15
    tccloud_domain: str = "https://tccloud.mtzlab.com"
    tccloud_api_version_prefix: str = "/api/v1"
    tccloud_default_credentials_profile: str = "default"
    tcfe_keywords: str = "tcfe:keywords"


settings = Settings()
