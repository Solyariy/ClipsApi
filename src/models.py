import uuid
from os import PathLike

from src.config import BLOCKS

from pydantic import (
    UUID4,
    BaseModel,
    Field,
    FilePath
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
    uuid_: str = Field(
        default_factory=lambda: uuid.uuid4().hex
    )
    clips_path: tuple[PathLike, ...]
    audio_path: PathLike
    speach_path: PathLike
    text: str
    voice: str
