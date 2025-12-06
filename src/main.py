import asyncio
import logging
import sys
import httpx
import uvicorn
from fastapi import FastAPI
from loguru import logger
from src.config import DEBUG
from src.utils import VoiceCache
from contextlib import asynccontextmanager
from src.scripts import download_voices_info
from src.api.main_router import router as main_router

logger.remove()
if DEBUG:
    logger.add(sys.stdout)
else:
    logger.add(sys.stdout, serialize=True)


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


for name in logging.root.manager.loggerDict:
    if name in "uvicorn":
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.setLevel(logging.INFO)
        uvicorn_logger.addHandler(InterceptHandler())


@asynccontextmanager
async def lifespan(app: FastAPI):
    if DEBUG:
        logger.debug("DEBUG mode")
    async with httpx.AsyncClient() as client:
        await download_voices_info(client=client)
        VoiceCache.load_voices()
        app.state.httpx_client = client
        app.state.speach_semaphore = asyncio.Semaphore(2)
        yield


app = FastAPI(lifespan=lifespan)

app.include_router(main_router)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None, reload=True)
