from itertools import chain


def flatten_blocks(blocks: dict[str, list[str]]):
    yield from chain(*blocks.values())
