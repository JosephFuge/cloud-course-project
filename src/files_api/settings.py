"""Define settings for FastAPI app."""

from pydantic import Field  # BaseModel,
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """
    Settings for the files API.

    Pydantic BaseSettings docs: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
    FastAPI guide to managing settings: https://fastapi.tiangolo.com/advanced/settings/
    """

    s3_bucket_name: str = Field(...)

    model_config = SettingsConfigDict(case_sensitive=False)
