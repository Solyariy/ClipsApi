from elevenlabs.client import AsyncElevenLabs
from src.config import TEMP_PATH, ELEVENLABS_API_KEY
import httpx
import aiofiles


class TextToSpeech:
    def __init__(self, client: httpx.AsyncClient):
        self.elevenlabs = AsyncElevenLabs(
            api_key=ELEVENLABS_API_KEY,
            httpx_client=client
        )

    # async def

    async def test(self):
        audio = self.elevenlabs.text_to_speech.stream(
            text="The first move is what sets everything in motion.",
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        with open(TEMP_PATH / "test_audio.mp3", "wb") as f:
            async for chunk in audio:
                f.write(chunk)


async def main():
    async with httpx.AsyncClient() as client:
        t = TextToSpeech(client)
        await t.test()


import asyncio
if __name__ == '__main__':
    asyncio.run(main())
