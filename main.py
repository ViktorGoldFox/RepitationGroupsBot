import asyncio
from datetime import datetime
from logzero import logger, logfile
#=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶
from bot import bot
from aiogram import types
from aiogram.filters import Command
#=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶
from Core import config as configs
from database import db_helper
from sqlalchemy.ext.asyncio import AsyncSession

#=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶
logfile(configs.bot.logs_path)
#=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶=̶

async def run():
    await db_helper.on_startup()
    await bot.on_startup()

if __name__ == "__main__":
    print(f"Version: {configs.bot.version}")

    logger.info(f"Бот успешно запущен в {datetime.now()}")

    asyncio.run(run())