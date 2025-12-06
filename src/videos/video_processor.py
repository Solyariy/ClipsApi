from pathlib import Path

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
    concatenate_videoclips, concatenate_audioclips,
)

from src.config import TEMP_PATH
from src.models import VideoSetup


class VideoProcessor:
    def __init__(self, path: Path, video_setups: list[VideoSetup]):
        self.setups = video_setups
        self.path = path

    @staticmethod
    def _validate_paths(setup: VideoSetup) -> None:
        for clip_path in setup.clips_path:
            if not Path(clip_path).exists():
                raise FileNotFoundError(f"Clip not found: {clip_path}")

        if not Path(setup.audio_path).exists():
            raise FileNotFoundError(f"Audio not found: {setup.audio_path}")

        if not Path(setup.speach_path).exists():
            raise FileNotFoundError(f"Speech not found: {setup.speach_path}")

    def process_setup(self, setup: VideoSetup):
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
            self.path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )

        for clip in clips:
            clip.close()
        bg_audio.close()
        speech.close()
        final_video.close()

    def start_processing(self):
        for setup in self.setups:
            self.process_setup(setup)


if __name__ == "__main__":
    setup = VideoSetup(
        clips_path=(
            TEMP_PATH / "fa06f67fe765436ab8029bb90799f901/block1_1.mp4",
            TEMP_PATH / "fa06f67fe765436ab8029bb90799f901/block2_3.mp4",
            TEMP_PATH / "fa06f67fe765436ab8029bb90799f901/block3_1.mp4",
        ),
        audio_path=TEMP_PATH / "fa06f67fe765436ab8029bb90799f901/audio1_1.mp3",
        speach_path=TEMP_PATH / "fa06f67fe765436ab8029bb90799f901/be4b86b7dad84219864100027b48e7a7_Will.mp3",
        text="asds",
        voice="asdasd"
    )

    p = VideoProcessor(TEMP_PATH / "test_full_video_1.mp4", [setup])
    p.start_processing()