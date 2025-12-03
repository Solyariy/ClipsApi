import asyncio
import uuid

import aiofiles
import aiofiles.os
import aiohttp
from pathlib import Path

from src.config import BLOCKS, CHUNKS_SIZE, TEMP_PATH


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
        self.path = TEMP_PATH / str(task_uuid)

    async def create_dir(self):
        await aiofiles.os.mkdir(self.path)

    async def clean_dir(self):
        await aiofiles.os.remove(self.path)

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


async def main():
    async with aiohttp.ClientSession() as session:
        manager = FileManager(
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
        )
        video_url = "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/2025-09-14%2016.02.30.mp4"
        audio_url = "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/audiobible3.mp3"
        await manager.create_dir()
        await manager.download_file(url=video_url, block_name="block1", file_index="1")
        await manager.download_file(url=audio_url, block_name="audio1", file_index="1")
        await asyncio.sleep(5)
        await manager.clean_dir()


if __name__ == '__main__':
    asyncio.run(main())
