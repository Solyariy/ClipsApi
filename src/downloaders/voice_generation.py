import json
from pathlib import Path

from elevenlabs.client import AsyncElevenLabs
from src.config import TEMP_PATH, ELEVENLABS_API_KEY, TEXT_TO_SPEACH, VOICES_PATH
import httpx
import aiofiles


class TextToSpeechManager:
    def __init__(
            self,
            path: Path,
            text_to_speach: TEXT_TO_SPEACH,
            client: httpx.AsyncClient,
    ):
        self.path = path
        self.text_to_speach = text_to_speach
        self.elevenlabs = AsyncElevenLabs(
            api_key=ELEVENLABS_API_KEY,
            httpx_client=client
        )

    async def update_voices_info(self):
        response = await self.elevenlabs.voices.get_all()
        print(len(response.voices))
        print(response.voices)
        data = {
            v.name: {
                "voice_id": v.voice_id,
                "model_ids": v.high_quality_base_model_ids
            }
            for v in response.voices
        }
        data = json.dumps(data)
        async with aiofiles.open(VOICES_PATH, "w") as f:
            await f.write(data)

    async def generate_speach(
            self,
            text: str,
            voice: str,
    ):
        ...


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
        t = TextToSpeechManager(Path(__file__), [{"as": "as"}], client)
        await t.update_voices_info()


import asyncio
if __name__ == '__main__':
    asyncio.run(main())

