from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.repitation import crud
from bot.repitation.filters import GroupRegister, IsGroup, IsReplyMessage, UserRegister
from database import db_helper

repitation_router = Router()


@repitation_router.message(
    Command("+реп"), IsReplyMessage(), IsGroup(), GroupRegister, UserRegister()
)
async def plus_repitation(message: Message):
    db_session: AsyncSession = db_helper.get_scoped_session()

    await crud.add_repitation(message.from_user.id, db_session)

    await db_session.close()
