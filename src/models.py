from pydantic import BaseModel, HttpUrl


class TaskPost(BaseModel):
    task_name: str
    video_blocks: dict[str, list[HttpUrl]]
    audio_blocks: dict[str, list[HttpUrl]]
    text_to_speach: list[dict[str, str]]


class Video(BaseModel):
    clips: tuple[str, ...]
    audio: str
    text: str
    voice: str
