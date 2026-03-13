from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_SERVICE_DIR = Path(__file__).resolve().parents[2]
_REPO_ROOT = _SERVICE_DIR.parent


class Settings(BaseSettings):
    mcp_service_name: str = Field(default="Poco MCP Service", alias="MCP_SERVICE_NAME")
    mcp_transport: str = Field(default="http", alias="MCP_TRANSPORT")
    mcp_host: str = Field(default="0.0.0.0", alias="MCP_HOST")
    mcp_port: int = Field(default=8090, alias="MCP_PORT")

    backend_base_url: str = Field(
        default="http://127.0.0.1:8000/api/v1",
        alias="BACKEND_BASE_URL",
    )
    backend_admin_api_key: str = Field(default="", alias="BACKEND_ADMIN_API_KEY")
    backend_global_api_key: str = Field(default="", alias="BACKEND_GLOBAL_API_KEY")
    backend_timeout_seconds: float = Field(default=20, alias="BACKEND_TIMEOUT_SECONDS")

    analytics_default_timezone: str = Field(
        default="Asia/Shanghai",
        alias="ANALYTICS_DEFAULT_TIMEZONE",
    )
    analytics_default_top_limit: int = Field(default=10, alias="ANALYTICS_DEFAULT_TOP_LIMIT")

    model_config = SettingsConfigDict(
        env_file=(
            _SERVICE_DIR / ".env",
            _REPO_ROOT / ".env",
        ),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
