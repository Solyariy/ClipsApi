from pathlib import Path
from typing import Annotated
import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = bool(os.getenv("DEBUG"))

TEMP_PATH = Path(__file__).parent / "temp"
VOICES_PATH = TEMP_PATH / "voices.json"

BLOCKS = Annotated[
    dict[str, list[str]], "video/audio blocks"
]
TEXT_TO_SPEACH = Annotated[
    list[dict[str, str]], "text and voice setups"
]
CHUNKS_SIZE = 1024 * 128
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_MODEL_ID = "eleven_multilingual_v2"
ELEVENLABS_OUTPUT_FORMAT = "mp3_44100_128"