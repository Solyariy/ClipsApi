import json
from itertools import chain

from src.config import BLOCKS, VOICES_PATH
from urllib.parse import urlparse
from pathlib import Path


def flatten_blocks(blocks: BLOCKS):
    yield from chain(*blocks.values())


def get_url_info(blocks: BLOCKS):
    for block_name, urls in blocks.items():
        for index, url in enumerate(urls, 1):
            yield url, block_name, index


def get_extension(url):
    return Path(urlparse(str(url)).path).suffix.lower()


class VoiceCache:
    data: dict[str, dict] | None = None

    @classmethod
    def load_voices(cls):
        with open(VOICES_PATH, "r") as f:
            cls.data = json.load(f)

    @classmethod
    def get_voice_info(cls, name: str):
        if cls.data is None:
            cls.load_voices()
        return cls.data.get(name)


def get_voice_info(name: str) -> dict[str, str | list[str]]:
    if info := VoiceCache.get_voice_info(name=name):
        return info
    raise ValueError(
        f"Voice with name: {name} was not found, "
        f"try to use PUT /update-voices to update existing data"
    )
