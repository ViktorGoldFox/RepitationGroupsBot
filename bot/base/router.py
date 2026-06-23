from aiogram import Router, types
from aiogram.filters import Command
from logzero import logger
from sqlalchemy.ext.asyncio import AsyncSession

from database import db_helper

base_router = Router()


@base_router.message(Command("start"))
async def bot_start(message: types.Message):
    logger.debug(
        f"bot_start \n Username: {message.from_user.username} \n User_id: {message.from_user.id}"
    )
    session: AsyncSession = db_helper.get_scoped_session()

    await message.answer("Start")

    logger.info(f"@{message.from_user.username} вывел start")

    await session.close()
