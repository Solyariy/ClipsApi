import asyncio
import logging
import sys
import httpx
# import uvicorn
from fastapi import FastAPI
from loguru import logger
from google.cloud.storage import Client
from src.config import DEBUG, GOOGLE_APPLICATION_CREDENTIALS, GOOGLE_STORAGE_BUCKET_NAME
from src.utils import VoiceCache
from contextlib import asynccontextmanager
from src.downloaders.scripts import download_voices_info
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
        gcs_client = Client.from_service_account_json(GOOGLE_APPLICATION_CREDENTIALS)
        app.state.gcs_bucket = gcs_client.bucket(GOOGLE_STORAGE_BUCKET_NAME)
        app.state.httpx_client = client
        app.state.speach_semaphore = asyncio.Semaphore(2)
        yield
        gcs_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(main_router)

# if __name__ == '__main__':
#     uvicorn.run("src.main:app", host="0.0.0.0", port=8000, log_config=None, reload=True)
