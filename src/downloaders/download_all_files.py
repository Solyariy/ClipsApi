from loguru import logger


async def download_all_files(
        speach_manager,
        blocks_manager
):
    successes_speach, failures_speach = await speach_manager.gather_tasks()
    successes_blocks, failures_blocks = await blocks_manager.gather_tasks()

    logger.debug(f"SUCCESS SPEACH: {successes_speach}")
    if failures_speach:
        logger.debug(f"FAILURE SPEACH: {failures_speach}")
        for e in failures_speach:
            logger.warning(f"\n{e}\n")

    logger.debug(f"SUCCESS BLOCKS: {successes_blocks}")
    if failures_blocks:
        logger.debug(f"FAILURE BLOCKS: {failures_blocks}")
        for e in failures_blocks:
            logger.warning(f"\n{e}\n")

    return dict(
        successes_speach=successes_speach,
        failures_speach=failures_speach,
        successes_blocks=successes_blocks,
        failures_blocks=failures_blocks
    )