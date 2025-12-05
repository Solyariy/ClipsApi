import asyncio
from pathlib import Path

import aiofiles
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
        extension = get_extension(url)
        filename = self.path / f"{block_name}_{file_index}{extension}"
        async with self.client.stream("GET", url=str(url)) as response:
            async with aiofiles.open(filename, "wb") as f:
                iter_chunks = response.aiter_bytes(CHUNKS_SIZE)
                async for chunk in iter_chunks:
                    await f.write(chunk)
        return block_name, filename, extension

    async def gather_tasks(self):
        tasks = [
            self.download_file(*info)
            for block in (self.video_blocks, self.audio_blocks)
            for info in get_url_info(block)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        failures = []
        temp_video_blocks = {key: [] for key in self.video_blocks.keys()}
        temp_audio_blocks = {key: [] for key in self.audio_blocks.keys()}

        for result in results:
            if isinstance(result, Exception):
                failures.append(result)
                continue
            block_name, filename, extension = result
            if extension == ".mp4":
                temp_video_blocks[block_name].append(filename)
            elif extension == ".mp3":
                temp_audio_blocks[block_name].append(filename)

        successes = {
            "video_blocks": temp_video_blocks,
            "audio_blocks": temp_audio_blocks
        }

        return successes, failures
