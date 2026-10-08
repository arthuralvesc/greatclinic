import pytest
from pydantic import ValidationError

from app.core.config import Settings

REQUIRED = {
    "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/clinic",
    "AI_AGENT_API_KEY": "secret",
    "CLINIC_TIMEZONE": "America/Sao_Paulo",
    "SLOT_DURATION_MINUTES": "30",
    "MIN_BOOKING_NOTICE_MINUTES": "120",
    "MAX_BOOKING_ADVANCE_DAYS": "90",
    "MAX_ACTIVE_APPOINTMENTS_PER_PATIENT": "5",
}


@pytest.fixture
def full_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    for key, value in REQUIRED.items():
        monkeypatch.setenv(key, value)
    return monkeypatch


def test_loads_when_every_setting_is_present(full_env: pytest.MonkeyPatch) -> None:
    settings = Settings(_env_file=None)

    assert settings.ai_agent_api_key == "secret"
    assert settings.slot_duration_minutes == 30


@pytest.mark.parametrize("missing", sorted(REQUIRED))
def test_fails_fast_when_a_setting_is_missing(full_env: pytest.MonkeyPatch, missing: str) -> None:
    full_env.delenv(missing)

    with pytest.raises(ValidationError) as exc:
        Settings(_env_file=None)

    assert missing.lower() in str(exc.value).lower()
