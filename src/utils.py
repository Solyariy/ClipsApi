import random
from itertools import chain, product

from src.models import Video


def get_video_combs(blocks: dict[str, list[str]]):
    return list(product(*blocks.values()))


def get_random_audio(
    blocks: dict[str, list[str]], limit: int
):
    t = tuple(chain(*blocks.values()))
    return [
        t[i % len(t)]
        for i in random.sample(range(limit * 2), limit)
    ]


def get_random_speach(blocks: list[dict[str, str]], limit):
    return [
        blocks[i % len(blocks)]
        for i in random.sample(range(limit * 2), limit)
    ]


def get_setups(video_blocks, audio_blocks, speach_blocks):
    videos = get_video_combs(video_blocks)
    audio = get_random_audio(audio_blocks, len(videos))
    speach = get_random_speach(speach_blocks, len(videos))
    return [
        Video(
            clips=videos[i],
            audio=audio[i],
            text=speach[i]["text"],
            voice=speach[i]["voice"],
        )
        for i in range(len(videos))
    ]


import json
import os

if __name__ == "__main__":
    with open(
        os.path.join("test", "test1.json"), "r"
    ) as file:
        data = json.load(file)
    print(
        *get_setups(
            data["video_blocks"],
            data["audio_blocks"],
            data["text_to_speach"],
        ),
        sep="\n",
    )
