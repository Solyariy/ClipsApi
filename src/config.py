from pathlib import Path
from typing import Annotated
import os
from dotenv import load_dotenv
from pydantic import HttpUrl

load_dotenv()

TEMP_PATH = Path(__file__).parent / "temp"
VOICES_PATH = TEMP_PATH / "voices.json"

BLOCKS = Annotated[
    dict[str, list[HttpUrl]], "video/audio blocks"
]
TEXT_TO_SPEACH = Annotated[
    list[dict[str, str]], "text and voice setups"
]
CHUNKS_SIZE = 1024 * 128
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
