from datetime import UTC, datetime
from typing import List

from sqlalchemy import Result, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Rest


async def issued_rest(
    target_t_user_id: int,
    target_display: str,
    issued_by_t_user_id: int,
    issued_by_display: str,
    end_at: str | None,
    t_chat_id: int,
    db_session: AsyncSession,
) -> None:
    if end_at and end_at.casefold() not in {"неизвестно", "unknown"}:
        end_at_datetime = datetime.fromisoformat(end_at).replace(tzinfo=UTC)
    else:
        end_at_datetime = None

    new_rest = Rest(
        t_chat_id=t_chat_id,
        target_t_user_id=target_t_user_id,
        target_display=target_display,
        issued_by=issued_by_t_user_id,
        issued_by_display=issued_by_display,
        end_at=end_at_datetime,
    )

    db_session.add(new_rest)
    await db_session.commit()


async def delete_rest(
    t_chat_id: int, target_t_user_id: int, db_session: AsyncSession
) -> None:
    stmt = delete(Rest).where(
        Rest.t_chat_id == t_chat_id, Rest.target_t_user_id == target_t_user_id
    )

    await db_session.execute(stmt)
    await db_session.commit()


async def get_all_rest(t_chat_id: int, db_session: AsyncSession):
    stmt = select(Rest).where(Rest.t_chat_id == t_chat_id).order_by(
        Rest.created_at.desc()
    )

    result: Result = await db_session.execute(stmt)

    all_rests = result.scalars().all()

    return all_rests
