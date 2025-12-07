import os
import uuid
from pathlib import Path

import aiofiles

from src.settings import config


class DirManager:
    def __init__(self, task_uuid: str):
        self.task_uuid = task_uuid
        self._temp_dir = None
        self.path = None

    async def __aenter__(self):
        if config.DEBUG:
            path = config.TEMP_PATH / uuid.uuid4().hex
            os.mkdir(path)
            self.path = Path(path)
        else:
            self._temp_dir = aiofiles.tempfile.TemporaryDirectory(
                dir=config.TEMP_PATH,
                suffix=self.task_uuid
            )
            self.path = await self._temp_dir.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if config.DEBUG:
            os.listdir(self.path)
        else:
            await self._temp_dir.__aexit__(exc_type, exc_val, exc_tb)
