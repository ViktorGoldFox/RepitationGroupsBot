import asyncio
from datetime import datetime

from logzero import logger, logfile

from bot import bot
from Core import config as configs
from database import db_helper

logfile(configs.bot.logs_path)

async def run():
    logger.info("Initializing database")
    await db_helper.on_startup()
    try:
        logger.info("Starting bot")
        await bot.on_startup()
    finally:
        logger.info("Shutting down database")
        await db_helper.close()
        await bot.on_shutdown()

if __name__ == "__main__":
    logger.info("Version: %s", configs.bot.version)

    logger.info("Bot process started at %s", datetime.now())

    try:
        asyncio.run(run())
    except Exception:
        logger.exception("Bot crashed")
        raise
