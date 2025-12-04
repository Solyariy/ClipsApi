import asyncio
import os
import uuid

import aiofiles
import aiofiles.os
from pathlib import Path

import httpx

from src.config import BLOCKS, CHUNKS_SIZE

from src.utils import get_url_info, get_extension


class BlocksManager:
    def __init__(
            self,
            path: Path,
            video_blocks: BLOCKS,
            audio_blocks: BLOCKS,
            client: httpx.AsyncClient
    ):
        self.path = path
        self.video_blocks = video_blocks
        self.audio_blocks = audio_blocks
        self.client = client

    async def download_file(
            self,
            url: str,
            block_name: str,
            file_index: str,
    ):
        file_settings = (
            self.path / f"{block_name}_{file_index}{get_extension(url)}",
            "wb",
        )
        async with self.client.stream("GET", url=url) as response:
            async with aiofiles.open(*file_settings) as f:
                iter_chunks = response.aiter_bytes(CHUNKS_SIZE)
                async for chunk in iter_chunks:
                    await f.write(chunk)

    async def gather_tasks(self):
        tasks = [
            self.download_file(*info)
            for block in (self.video_blocks, self.audio_blocks)
            for info in get_url_info(block)
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)
