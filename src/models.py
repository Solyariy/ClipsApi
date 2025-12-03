import uuid

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
    video_blocks: dict[str, list[HttpUrl]]
    audio_blocks: dict[str, list[HttpUrl]]
    text_to_speach: list[dict[str, str]]


class Video(BaseModel):
    uuid_: UUID4 = Field(
        default_factory=lambda: uuid.uuid4().hex
    )
    clips: tuple[str, ...]
    audio: str
    text: str
    voice: str
