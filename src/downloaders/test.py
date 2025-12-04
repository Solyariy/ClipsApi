import asyncio
import uuid

import httpx

from src.downloaders.dir_manager import DirManager
from src.downloaders.media_manager import MediaManager


async def main():
    async with httpx.AsyncClient() as client:
        with DirManager(
                task_uuid=uuid.uuid4().hex,
        ) as dir_manager:
            dm = MediaManager(
                dir_manager.path,
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
                client=client
            )
            await dm.gather_tasks()


if __name__ == '__main__':
    asyncio.run(main())
