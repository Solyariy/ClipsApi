from os import PathLike
from pathlib import Path
import tempfile
from loguru import logger

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
    concatenate_videoclips, concatenate_audioclips,
)

from src.models import VideoSetup


class VideoProcessor:
    def __init__(
            self,
            path: str,
    ):
        self.path = Path(path)

    @staticmethod
    def _validate_paths(setup: VideoSetup) -> None:
        for clip_path in setup.clips_path:
            if not Path(clip_path).exists():
                raise FileNotFoundError(f"Clip not found: {clip_path}")

        if not Path(setup.audio_path).exists():
            raise FileNotFoundError(f"Audio not found: {setup.audio_path}")

        if not Path(setup.speach_path).exists():
            raise FileNotFoundError(f"Speech not found: {setup.speach_path}")

    def process(self, save_to_path: PathLike, setup: VideoSetup) -> tempfile.NamedTemporaryFile:
        self._validate_paths(setup)

        clips = [VideoFileClip(path) for path in setup.clips_path]
        final_video = concatenate_videoclips(clips, method="compose")

        bg_audio = AudioFileClip(setup.audio_path).with_volume_scaled(factor=0.2)

        loops_needed = int(final_video.duration / bg_audio.duration) + 1
        looped_audio = concatenate_audioclips([bg_audio] * loops_needed)
        looped_audio = looped_audio.subclipped(0, final_video.duration)

        speech = AudioFileClip(setup.speach_path)

        composite_audio = CompositeAudioClip([looped_audio, speech])

        final_video = final_video.with_audio(composite_audio)

        final_video.write_videofile(
            save_to_path,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=self.path / f"temp_audio_{setup.uuid_}.m4a",
            remove_temp=True,
        )

        for clip in clips:
            clip.close()
        bg_audio.close()
        speech.close()
        final_video.close()
