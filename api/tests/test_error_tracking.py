"""Error tracking is off unless a Better Stack DSN is set."""

import pytest
import sentry_sdk

from app.error_tracking import setup_error_tracking
from app.settings import Settings


@pytest.fixture
def init_calls(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, object]]:
    """Records the calls to sentry_sdk.init instead of starting Sentry."""
    calls: list[dict[str, object]] = []

    def fake_init(**options: object) -> None:
        calls.append(options)

    monkeypatch.setattr(sentry_sdk, "init", fake_init)
    return calls


@pytest.mark.parametrize("dsn", [None, ""])
def test_nothing_starts_without_a_dsn(
    init_calls: list[dict[str, object]], dsn: str | None
) -> None:
    assert setup_error_tracking(Settings(better_stack_errors_dsn=dsn)) is False
    assert init_calls == []


def test_a_dsn_starts_it_without_personal_data(
    init_calls: list[dict[str, object]],
) -> None:
    settings = Settings(
        better_stack_errors_dsn="https://key@errors.example.com/1",
        environment="production",
    )

    assert setup_error_tracking(settings) is True
    [options] = init_calls
    assert options["dsn"] == "https://key@errors.example.com/1"
    assert options["environment"] == "production"
    assert options["send_default_pii"] is False
    assert options["max_request_body_size"] == "never"
