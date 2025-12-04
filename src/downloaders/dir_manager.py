import os
import tempfile
from pathlib import Path


class DirManager:
    def __init__(
            self,
            task_uuid: str,
    ):
        self.task_uuid = task_uuid

    def __enter__(self):
        self.temp_dir = tempfile.TemporaryDirectory(
            dir="temp",
            suffix=self.task_uuid
        )
        self.path = Path(self.temp_dir.name)
        # self.path = TEMP_PATH / self.task_uuid
        # os.mkdir(self.path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(os.listdir(self.path))
        self.temp_dir.cleanup()
