from sqlalchemy import select, Result, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import *
from untities import *

async def get_profile(session: AsyncSession, user_id: int):
    stmt = (
        select(Users)
        .where(Users.id == user_id)
    )

    result: Result = await session.execute(stmt)

    user = result.scalars().first()

    return user if user is not None else False


async def create_profile(session: AsyncSession, new_user: User):
    created_user = Users(**new_user.model_dump())

    session.add(created_user)
    await session.commit()

    return True


async def del_profile(session: AsyncSession, user_id: int):
    stmt = (
        delete(Users)
        .where((Users.id == user_id))
    )

    await session.execute(stmt)
    await session.commit()

    return True