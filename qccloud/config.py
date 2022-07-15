from pathlib import Path
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Base Settings configuration. Do not instantiate directly, use settings object on module"""

    qccloud_username: Optional[str] = None
    qccloud_password: Optional[str] = None
    qccloud_base_directory: Path = Path.home() / ".qccloud"
    qccloud_credentials_file: str = "credentials"
    qccloud_access_token_expiration_buffer: int = 15
    qccloud_domain: str = "https://qccloud.mtzlab.com"
    qccloud_api_version_prefix: str = "/api/v1"
    qccloud_default_credentials_profile: str = "default"
    tcfe_keywords: str = "tcfe:keywords"


settings = Settings()
