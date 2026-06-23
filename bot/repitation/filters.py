from typing import List

from aiogram import types
from aiogram.filters import Filter
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import db_helper
from database.models import Groups, Users


class IsReplyMessage(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return message.reply_to_message is not None


class IsGroup(Filter):
    async def __call__(self, message: types.Message) -> bool:
        if message.chat.type not in ["group", "supergroup"]:
            await message.answer("Используйте данную команду в группе.")

            return False

        return True


class GroupRegister(Filter):
    async def __call__(self, message: types.Message) -> bool:
        db_session: AsyncSession = db_helper.get_scoped_session()

        stmt = select(exists(Groups).where(Groups.t_chat_id == message.chat.id))

        is_exists = await db_session.scalar(stmt)

        if not is_exists:
            new_groups = Groups(t_chat_id=message.chat.id)

            db_session.add(new_groups)
            await db_session.commit()

        return True


class UserRegister(Filter):
    async def __call__(self, message: types.Message) -> bool:
        db_session: AsyncSession = db_helper.get_scoped_session()

        stmt = select(exists(Users).where(Users.t_user_id == message.from_user.id))

        is_exists_user = await db_session.scalar(stmt)

        if not is_exists_user:
            new_user = Users(
                t_user_id=message.from_user.id,
                t_user_name=message.from_user.username,
            )

            db_session.add(new_user)
            await db_session.commit()

        return True
