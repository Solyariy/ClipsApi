# ClipsApi

### Copy with GitHub
```bash
  git clone https://github.com/Solyariy/ClipsApi.git
```
### Configure .env file
```dotenv
MAIN_DEBUG=1
MAIN_PROCESSOR_BAR_TICK=20

ELEVENLABS_API_KEY=
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
ELEVENLABS_OUTPUT_FORMAT=mp3_44100_128

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# do not change DOWNLOADS_CPU for proper work of Elevenlabs Api
DOWNLOADS_CPU=1
GROUPER_CPU=2
PROCESSING_CPU=2

FLOWER_BROKER_URL=redis://redis:6379/0
FLOWER_UNAUTHENTICATED_API=true

# credentials is a json key that can be obtained in service account settings
GOOGLE_CREDENTIALS_PATH=
GOOGLE_STORAGE_BUCKET_NAME=
```
### Build the docker image
```bash
  docker-compose build
```
### Run the docker container
```bash
  docker-compose run
```
### Check the connection
```
http://localhost:8000/api/v1
```
### Path to the process_media
```
http://localhost:8000/api/v1/process_media
```
### Accepted body:
```
class TaskPost(BaseModel):
    uuid_: str = Field(
        default_factory=lambda: uuid.uuid4().hex
    )
    task_name: str
    video_blocks: dict[str, list[HttpUrl]]
    audio_blocks: dict[str, list[HttpUrl]]
    text_to_speach: list[dict[str, str]]
```
### Features
* Celery and Redis for queue management
* FastApi for routing
* MoviePy for clips processing
### Optimization
1. Data collection processed asynchronously 
using asyncio.gather() and single httpx.AsyncClient, 
so a lot of time saved waiting.
2. Calls to Elevenlabs Api restricted with asyncio.Semaphore(2) 
according to their restriction for max concurrent requests.
3. Usage of 3 celery workers for different tasks with ability 
to change their max cores used in env. 
Every video processed in its own task, and all videos are processed 
in parallel. After processing, video automatically uploaded to GCS 
to save local space. In the end local directory is deleted.
4. To use Elevenlabs we need voice_id instead of voice from request, so 
as the app launches script downloads all voices from elevenlabs api, 
saves as json in temp directory and util called get_voice_info uses already loaded in 
memory dict in VoiceCache class. As the result no time spent on loading from file. 
Additional endpoint "/api/v1/update-voices" can be called to update voices info from 
elevenlabs api.
5. At first all dependencies (AsyncClient, GoogleStorageClient, 
asyncio.Semaphore) were created once in FastApi lifespan, to save resources. 
But Celery works differently so this idea was aborted, but left as comments as mention.
### New learned features
* Complex task management in Celery, due to usage of vast instruments.
* Working with MoviePy for video processing.
### Used instruments
* FastApi
* Celery
* MoviePy
* Docker, docker-compose
* loguru
* httpx
* pydantic
* isort
* uvicorn
