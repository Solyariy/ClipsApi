import asyncio

from loguru import logger


async def download_all_files(
        speach_manager,
        blocks_manager
) -> dict:
    results = await asyncio.gather(
        speach_manager.gather_tasks(),
        blocks_manager.gather_tasks()
    )
    logger.info(f"RESULTS {results}")
    successes_speach, failures_speach = results[0]
    successes_blocks, failures_blocks = results[1]

    logger.info(f"SUCCESS SPEACH: {successes_speach}")
    if failures_speach:
        logger.warning(f"FAILURE SPEACH: {failures_speach}")
        for e in failures_speach:
            logger.warning(f"\n{e}\n")

    logger.info(f"SUCCESS BLOCKS: {successes_blocks}")
    if failures_blocks:
        logger.warning(f"FAILURE BLOCKS: {failures_blocks}")
        for e in failures_blocks:
            logger.warning(f"\n{e}\n")

    return dict(
        successes_speach=successes_speach,
        failures_speach=failures_speach,
        successes_blocks=successes_blocks,
        failures_blocks=failures_blocks
    )
