from sqlalchemy import Result, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Users


async def add_repitation(t_user_id: int, db_session: AsyncSession) -> float:
    stmt = (
        update(Users)
        .where(Users.t_user_id == t_user_id)
        .values(repitation=Users.repitation + 0.25)
        .returning(Users.repitation)
    )

    result: Result = await db_session.execute(stmt)
    new_repitation = result.scalar_one()

    await db_session.commit()

    return new_repitation
