from collections.abc import Iterator
from typing import Any

import pytest
from pydantic import ValidationError

from companies_house_mcp.config import Settings, get_settings

ENV_VARS = [
    "COMPANIES_HOUSE_API_KEY",
    "CH_TRANSPORT_MODE",
    "MCP_TRANSPORT",
    "MCP_HTTP_HOST",
    "MCP_HTTP_PORT",
    "MCP_HTTP_TOKEN",
    "CH_RATE_LIMIT_PER_5MIN",
    "LOG_LEVEL",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Stop the developer's real environment from leaking into tests."""
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def make(**kwargs: Any) -> Settings:
    # _env_file=None: ignore the real .env file on disk.
    # mypy can't see pydantic-settings' runtime-only `_env_file` argument.
    return Settings(_env_file=None, **kwargs)  # type: ignore[call-arg]


def test_defaults() -> None:
    s = make(companies_house_api_key="key")
    assert s.ch_transport_mode == "live"
    assert s.mcp_transport == "stdio"
    assert s.mcp_http_host == "127.0.0.1"
    assert s.mcp_http_port == 8000
    assert s.ch_rate_limit_per_5min == 600
    assert s.log_level == "INFO"


def test_reads_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COMPANIES_HOUSE_API_KEY", "env-key")
    monkeypatch.setenv("CH_RATE_LIMIT_PER_5MIN", "300")
    s = make()
    assert s.companies_house_api_key is not None
    assert s.companies_house_api_key.get_secret_value() == "env-key"
    assert s.ch_rate_limit_per_5min == 300


@pytest.mark.parametrize("key", [None, "", "   "])
def test_api_key_required_in_live_mode(key: str | None) -> None:
    with pytest.raises(ValidationError, match="COMPANIES_HOUSE_API_KEY"):
        make(companies_house_api_key=key)


def test_api_key_required_in_record_mode() -> None:
    with pytest.raises(ValidationError, match="COMPANIES_HOUSE_API_KEY"):
        make(ch_transport_mode="record")


def test_replay_mode_needs_no_api_key() -> None:
    s = make(ch_transport_mode="replay")
    assert s.companies_house_api_key is None


def test_http_requires_token() -> None:
    with pytest.raises(ValidationError, match="MCP_HTTP_TOKEN"):
        make(companies_house_api_key="key", mcp_transport="http")


def test_http_with_token_is_valid() -> None:
    s = make(companies_house_api_key="key", mcp_transport="http", mcp_http_token="tok")
    assert s.mcp_transport == "http"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("ch_transport_mode", "offline"),
        ("mcp_transport", "websocket"),
        ("log_level", "LOUD"),
        ("ch_rate_limit_per_5min", 0),
        ("mcp_http_port", 70000),
    ],
)
def test_invalid_values_rejected(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        make(companies_house_api_key="key", **{field: value})


def test_secrets_hidden_when_printed() -> None:
    s = make(companies_house_api_key="real-secret-key", mcp_http_token="real-token")
    for text in (repr(s), str(s)):
        assert "real-secret-key" not in text
        assert "real-token" not in text


def test_get_settings_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CH_TRANSPORT_MODE", "replay")
    monkeypatch.chdir("/")  # so no .env file is found
    assert get_settings() is get_settings()
