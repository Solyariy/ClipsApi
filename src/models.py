import uuid
from src.config import BLOCKS

from pydantic import (
    UUID4,
    BaseModel,
    Field,
    HttpUrl,
)


class TaskPost(BaseModel):
    uuid_: UUID4 = Field(
        default_factory=lambda: uuid.uuid4().hex
    )
    task_name: str
    video_blocks: BLOCKS
    audio_blocks: BLOCKS
    text_to_speach: list[dict[str, str]]


class Video(BaseModel):
    uuid_: UUID4 = Field(
        default_factory=lambda: uuid.uuid4().hex
    )
    clips: tuple[str, ...]
    audio: str
    text: str
    voice: str
