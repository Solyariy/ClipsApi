from pathlib import Path

from google.cloud.storage import Client
from loguru import logger

from src.models import VideoSetup
from src.videos.video_processor import VideoProcessor
from src.videos.storage_manager import StorageManager
import tempfile


def process_setup(
        processor: VideoProcessor,
        storage_manager: StorageManager,
        setup: VideoSetup
):
    with tempfile.NamedTemporaryFile(
            "wb", dir=processor.path, suffix=f"_{setup.uuid_}.mp4"
    ) as temp_file:
        logger.debug("TEMP FILE NAME: " + temp_file.name)
        try:
            processor.process(
                temp_file.name,
                setup
            )
            saved_url = storage_manager.upload(
                filename=f"{setup.uuid_}.mp4",
                path_from=temp_file.name
            )
        except Exception as e:
            logger.warning(f"Error for setup: {setup.model_dump_json()}, error: {e}")

    return saved_url
