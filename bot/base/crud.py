from sqlalchemy import select, Result, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from logzero import logger

from database.models import *
from untities import *

async def get_profile(session: AsyncSession, user_id: int):
    logger.debug("get_profile | user_id=%s", user_id)
    stmt = (
        select(Users)
        .where(Users.id == user_id)
    )

    result: Result = await session.execute(stmt)

    user = result.scalars().first()
    logger.debug("get_profile result | user_id=%s | found=%s", user_id, user is not None)

    return user if user is not None else False


async def create_profile(session: AsyncSession, new_user: User):
    logger.info("create_profile | user_id=%s", getattr(new_user, "t_user_id", None))
    created_user = Users(**new_user.model_dump())

    session.add(created_user)
    await session.commit()
    logger.debug("create_profile committed | user_id=%s", created_user.t_user_id)

    return True


async def del_profile(session: AsyncSession, user_id: int):
    logger.info("del_profile | user_id=%s", user_id)
    stmt = (
        delete(Users)
        .where((Users.id == user_id))
    )

    await session.execute(stmt)
    await session.commit()
    logger.debug("del_profile committed | user_id=%s", user_id)

    return True
