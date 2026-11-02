"""Settings loaded from environment variables and the .env file."""

from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _is_blank(secret: SecretStr | None) -> bool:
    return secret is None or not secret.get_secret_value().strip()


class Settings(BaseSettings):
    """All server settings. Field names map to env vars case-insensitively,
    e.g. `companies_house_api_key` reads COMPANIES_HOUSE_API_KEY."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # .env also holds vars for other tools, e.g. ANTHROPIC_API_KEY
    )

    companies_house_api_key: SecretStr | None = None
    ch_transport_mode: Literal["live", "replay", "record"] = "live"

    mcp_transport: Literal["stdio", "http"] = "stdio"
    mcp_http_host: str = "127.0.0.1"
    mcp_http_port: int = Field(default=8000, ge=1, le=65535)
    mcp_http_token: SecretStr | None = None

    ch_rate_limit_per_5min: int = Field(default=600, gt=0)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    @model_validator(mode="after")
    def _check_required_secrets(self) -> Self:
        # Replay mode reads saved fixtures only, so CI can run without a key.
        if self.ch_transport_mode != "replay" and _is_blank(self.companies_house_api_key):
            raise ValueError("COMPANIES_HOUSE_API_KEY is required unless CH_TRANSPORT_MODE=replay.")
        if self.mcp_transport == "http" and _is_blank(self.mcp_http_token):
            raise ValueError("MCP_HTTP_TOKEN is required when MCP_TRANSPORT=http.")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once per process."""
    return Settings()
