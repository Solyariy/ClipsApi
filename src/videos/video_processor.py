from pathlib import Path

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
    concatenate_videoclips,
)

from src.config import TEMP_PATH
from src.models import VideoSetup


class VideoProcessor:
    def __init__(self, path: Path, video_setups: list[VideoSetup]):
        self.setups = video_setups
        self.path = path
        self.clips: list[VideoFileClip] = []
        self.audio: list[AudioFileClip] = []

    def clean_audio(self):
        for audio in self.audio:
            audio.close()
        self.audio.clear()

    def clean_clips(self):
        for clip in self.clips:
            clip.close()
        self.clips.clear()

    def process_setup(self, setup: VideoSetup):
        self.clips.extend(
            VideoFileClip(
                filename=filename,
                audio=False
            )
            for filename in setup.clips_path
        )
        video = concatenate_videoclips(self.clips, method="compose")

        self.audio.append(
            AudioFileClip(
                filename=setup.audio_path
            ).with_volume_scaled(
                factor=0.2
            ).with_start(
                video.start
            ).with_duration(
                video.duration
            )
        )
        self.audio.append(
            AudioFileClip(filename=setup.speach_path).with_start()
        )
        audio = CompositeAudioClip(self.audio)

        audio.write_audiofile(TEMP_PATH / "test.mp3", fps=30)
