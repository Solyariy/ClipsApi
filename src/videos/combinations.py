import random
from itertools import product
from os import PathLike

from src.models import VideoSetup
from src.utils import flatten_blocks


def get_video_combs(blocks: dict[str, list[str]]):
    return list(product(*blocks.values()))


def get_random_audio(
        blocks: dict[str, list[str]], limit: int
):
    t = tuple(flatten_blocks(blocks))
    return [
        t[i % len(t)]
        for i in random.sample(range(limit * 2), limit)
    ]


def get_random_speach(blocks: list[dict[str, str | PathLike]], limit):
    return [
        blocks[i % len(blocks)]
        for i in random.sample(range(limit * 2), limit)
    ]


def get_video_setups(
        video_blocks, audio_blocks, speach_blocks
):
    videos = get_video_combs(video_blocks)
    audio = get_random_audio(audio_blocks, len(videos))
    speach = get_random_speach(speach_blocks, len(videos))
    return [
        VideoSetup(
            clips_path=videos[i],
            audio_path=audio[i],
            **speach[i]
        )
        for i in range(len(videos))
    ]
