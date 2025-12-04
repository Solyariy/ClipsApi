import json
from itertools import chain

import aiofiles

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
    return Path(urlparse(url).path).suffix.lower()


class VoiceCache:
    data = None

    @classmethod
    async def load_voices(cls):
        async with aiofiles.open(VOICES_PATH, "r") as f:
            data = await f.read()
            cls.data = json.loads(data)


def get_voice_id(name: str):
    return VoiceCache.data.get(name)
