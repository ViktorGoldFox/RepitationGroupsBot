from typing import List

from logzero import logger
from sqlalchemy import Result, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import GroupUser, Users


async def set_repitation_delta(
    t_user_id: int, delta: float, db_session: AsyncSession
) -> float:
    logger.debug(
        "set_repitation_delta | user_id=%s | delta=%s",
        t_user_id,
        delta,
    )
    stmt = (
        update(Users)
        .where(Users.t_user_id == t_user_id)
        .values(repitation=Users.repitation + delta)
        .returning(Users.repitation)
    )

    result: Result = await db_session.execute(stmt)
    new_repitation = result.scalar_one()

    await db_session.commit()
    logger.debug(
        "set_repitation_delta committed | user_id=%s | new_rep=%s",
        t_user_id,
        new_repitation,
    )

    return new_repitation


async def set_repitation(
    t_user_id: int, new_rep: float, db_session: AsyncSession
) -> float:
    logger.debug(
        "set_repitation | user_id=%s | new_rep=%s",
        t_user_id,
        new_rep,
    )
    stmt = (
        update(Users)
        .where(Users.t_user_id == t_user_id)
        .values(repitation=new_rep)
        .returning(Users.repitation)
    )

    result: Result = await db_session.execute(stmt)
    new_repitation = result.scalar_one()

    await db_session.commit()
    logger.debug(
        "set_repitation committed | user_id=%s | new_rep=%s",
        t_user_id,
        new_repitation,
    )

    return new_repitation


async def get_top_rep_of_chat(t_chat_id: int, db_session: AsyncSession) -> List[Users]:
    logger.debug("get_top_rep_of_chat | chat_id=%s", t_chat_id)
    stmt = (
        select(Users)
        .join(GroupUser, GroupUser.user_id == Users.t_user_id)
        .where(GroupUser.group_id == t_chat_id)
        .order_by(desc(Users.repitation))
        .limit(5)
    )

    result = await db_session.execute(stmt)
    top_users = result.scalars().all()
    logger.debug(
        "get_top_rep_of_chat result | chat_id=%s | count=%s",
        t_chat_id,
        len(top_users),
    )

    return top_users
