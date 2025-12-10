import uuid
from os import PathLike

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
)


class TaskPost(BaseModel):
    uuid_: str = Field(
        default_factory=lambda: uuid.uuid4().hex
    )
    task_name: str
    video_blocks: dict[str, list[HttpUrl]]
    audio_blocks: dict[str, list[HttpUrl]]
    text_to_speach: list[dict[str, str]]


class VideoSetup(BaseModel):
    uuid_: str = Field(
        default_factory=lambda: uuid.uuid4().hex
    )
    clips_path: tuple[PathLike, ...]
    audio_path: PathLike
    speach_path: PathLike
    text: str
    voice: str
