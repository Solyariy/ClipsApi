import asyncio
import os
import uuid

import aiofiles
import aiofiles.os
import aiohttp
from pathlib import Path

from src.config import BLOCKS, CHUNKS_SIZE, TEMP_PATH

import tempfile

from src.models import TaskPost
from src.utils import flatten_blocks, get_url_info


def get_temp_dir():
    t = tempfile.TemporaryDirectory(dir="temp")
    t.cleanup()


class FileManager:
    def __init__(
            self,
            task_uuid: str,
            video_blocks: BLOCKS,
            audio_blocks: BLOCKS,
            session: aiohttp.ClientSession,
    ):
        self.task_uuid = task_uuid
        self.session = session
        self.video_blocks = video_blocks
        self.audio_blocks = audio_blocks

    def __enter__(self):
        # self.temp_dir = tempfile.TemporaryDirectory(dir="temp")
        # self.path = Path(self.temp_dir.name)
        self.path = TEMP_PATH / str(uuid.uuid4())
        os.mkdir(self.path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.temp_dir.cleanup()
        ...

    async def download_file(
            self,
            url: str,
            block_name: str,
            file_index: str,
    ):
        file_settings = (
            self.path / f"{block_name}_{file_index}{Path(url).suffix.lower()}",
            "wb",
        )
        async with self.session.get(url=url) as response:
            if response.status != 200:
                raise ValueError(
                    "status != 200: " + response.status
                )
            async with aiofiles.open(*file_settings) as f:
                iter_chunks = response.content.iter_chunked(
                    CHUNKS_SIZE
                )
                async for chunk in iter_chunks:
                    await f.write(chunk)

    async def gather_tasks(self):
        tasks = [
            self.download_file(*info)
            for block in (self.video_blocks, self.audio_blocks)
            for info in get_url_info(block)
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)


async def main():
    async with aiohttp.ClientSession() as session:
        with FileManager(
                task_uuid=uuid.uuid4(),
                video_blocks={
                    "block1": [
                        "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/2025-09-14%2016.02.30.mp4"
                    ],
                    "block2": [
                        "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/8849_1.mp4",
                    ],
                },
                audio_blocks={
                    "audio1": [
                        "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/audiobible3.mp3"
                    ],
                },
                session=session
        ) as manager:
            await manager.gather_tasks()


if __name__ == '__main__':
    asyncio.run(main())
