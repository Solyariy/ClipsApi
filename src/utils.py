from itertools import chain

from src.config import BLOCKS, VOICES_CACHE
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


def get_voice_id(name: str):
    return VOICES_CACHE.get(name)
