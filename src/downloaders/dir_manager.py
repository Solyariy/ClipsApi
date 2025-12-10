import os
import shutil

from src.settings import config


class DirManager:
    def __init__(self, task_uuid: str):
        self.task_uuid = task_uuid
        # self._temp_dir = None
        self.path = str(config.TEMP_PATH / task_uuid)

    def create_dir(self):
        os.mkdir(self.path)

    def cleanup(self):
        shutil.rmtree(self.path)

    # def __enter__(self):
    #     if config.DEBUG:
    #         path = config.TEMP_PATH / uuid.uuid4().hex
    #         os.mkdir(path)
    #         self.path = str(path)
    #     else:
    #         self._temp_dir = tempfile.TemporaryDirectory(
    #             dir=config.TEMP_PATH,
    #             suffix=self.task_uuid
    #         )
    #         self.path = self._temp_dir.name
    #     return self
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     if config.DEBUG:
    #         os.listdir(self.path)
    #         # os.rmdir(self.path)
    #     else:
    #         self._temp_dir.cleanup()
