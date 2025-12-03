from pathlib import Path
from typing import Annotated

TEMP_PATH = Path(__file__).parent / "temp"
BLOCKS = Annotated[
    dict[str, list[str]], "video/audio blocks"
]
CHUNKS_SIZE = 1024 * 128
