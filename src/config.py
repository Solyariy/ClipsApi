from pathlib import Path
from typing import Annotated
import os
from dotenv import load_dotenv
from pydantic import HttpUrl

load_dotenv()

TEMP_PATH = Path(__file__).parent / "temp"
BLOCKS = Annotated[
    dict[str, list[HttpUrl]], "video/audio blocks"
]
CHUNKS_SIZE = 1024 * 128
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
