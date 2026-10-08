from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings. Every field is required so the app fails fast at startup."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    ai_agent_api_key: str
    clinic_timezone: str
    slot_duration_minutes: int
    min_booking_notice_minutes: int
    max_booking_advance_days: int
    max_active_appointments_per_patient: int
