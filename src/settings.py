from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import RedisDsn, FilePath
from pathlib import Path
from typing import Annotated, ClassVar


class MainConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="main_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    DEBUG: bool = False
    SRC_PATH: Path = Path(__file__).parent
    TEMP_PATH: Path = SRC_PATH / "temp"
    VOICES_PATH: Path = TEMP_PATH / "voices.json"
    BLOCKS: ClassVar = Annotated[
        dict[str, list[str]], "video/audio blocks"
    ]
    TEXT_TO_SPEACH: ClassVar = Annotated[
        list[dict[str, str]], "text and voice setups"
    ]
    CHUNKS_SIZE: int = 1024 * 128


class ElevenlabsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="elevenlabs_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    API_KEY: str
    MODEL_ID: str
    OUTPUT_FORMAT: str


class CelerySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="celery_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    BROKER_URL: str
    RESULT_BACKEND: str


class GoogleSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="google_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    CREDENTIALS_PATH: FilePath
    STORAGE_BUCKET_NAME: str


config = MainConfig()
elevenlabs_settings = ElevenlabsSettings()
celery_settings = CelerySettings()
google_settings = GoogleSettings()
