from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from logzero import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.repitation import crud
from bot.repitation.filters import (
    CheckArgsColl,
    EnsureRepitationRegistration,
    IsGroup,
    IsAdmin,
    IsReplyMessage,
    RepitationRateLimit,
    NotReplyToMind,
)
from bot.utils import format_user_display
from database import db_helper

repitation_router = Router()


@repitation_router.message(
    F.text.in_({"+реп", "-реп"}),
    IsReplyMessage(),
    NotReplyToMind(),
    IsGroup(),
    EnsureRepitationRegistration(),
    RepitationRateLimit(),
)
async def delta_repitation(message: Message):
    db_session: AsyncSession = db_helper.get_scoped_session()
    logger.info(
        "Command %s | actor=@%s | actor_id=%s | target=@%s | target_id=%s | chat_id=%s",
        message.text,
        message.from_user.username,
        message.from_user.id,
        message.reply_to_message.from_user.username,
        message.reply_to_message.from_user.id,
        message.chat.id,
    )

    delta = 0.25 if message.text == "+реп" else -0.25

    new_rep = await crud.set_repitation_delta(
        t_user_id=message.reply_to_message.from_user.id,
        db_session=db_session,
        delta=delta,
    )

    action_text = "уважение" if delta > 0 else "неуважение"
    actor_display = format_user_display(
        message.from_user.username, message.from_user.full_name
    )
    target_display = format_user_display(
        message.reply_to_message.from_user.username,
        message.reply_to_message.from_user.full_name,
    )
    logger.info(
        "Repitation updated | target_id=%s | delta=%s | new_rep=%s",
        message.reply_to_message.from_user.id,
        delta,
        new_rep,
    )

    await message.reply(
        f"Реакция учтена.\n\n"
        f"• {actor_display} оказал {action_text} {target_display}\n"
        f"• Репутация {target_display}: {new_rep}",
    )

    await db_session.close()
    logger.debug("Closed DB session after repitation delta")


@repitation_router.message(
    Command("setrep"),
    CheckArgsColl(1),
    IsReplyMessage(),
    IsGroup(),
    IsAdmin(),
    EnsureRepitationRegistration(),
)
async def set_repitation(message: Message):
    db_session: AsyncSession = db_helper.get_scoped_session()
    logger.info(
        "Command /setrep | actor=@%s | actor_id=%s | target=@%s | target_id=%s | chat_id=%s | payload=%r",
        message.from_user.username,
        message.from_user.id,
        message.reply_to_message.from_user.username,
        message.reply_to_message.from_user.id,
        message.chat.id,
        message.text,
    )

    new_rep = float(str(message.text).split()[1])

    new_rep = await crud.set_repitation(
        t_user_id=message.reply_to_message.from_user.id,
        db_session=db_session,
        new_rep=new_rep,
    )

    logger.info(
        "Repitation set | target_id=%s | new_rep=%s",
        message.reply_to_message.from_user.id,
        new_rep,
    )
    target_display = format_user_display(
        message.reply_to_message.from_user.username,
        message.reply_to_message.from_user.full_name,
    )

    await message.reply(
        f"Готово.\n\n"
        f"• Пользователь: {target_display}\n"
        f"• Репутация: {new_rep}",
    )

    await db_session.close()
    logger.debug("Closed DB session after setrep")


@repitation_router.message(
    F.text.casefold().strip().in_({"топ реп", "топ репутации", "реп топ"})
)
async def top_of_repitation(message: Message):
    db_session: AsyncSession = db_helper.get_scoped_session()
    logger.info(
        "Command top | user=@%s | user_id=%s | chat_id=%s",
        message.from_user.username,
        message.from_user.id,
        message.chat.id,
    )

    rep_top = await crud.get_top_rep_of_chat(
        t_chat_id=message.chat.id, db_session=db_session
    )

    if not rep_top:
        await message.reply("Пока в этой группе нет участников в топе.")
        await db_session.close()
        logger.debug("Closed DB session after top request without results")
        return

    top_lines = []
    for index, user in enumerate(rep_top, start=1):
        username = format_user_display(user.t_user_name, user.t_user_fullname)
        top_lines.append(f"{index}. {username} - {user.repitation}")

    await message.reply(
        "Топ репутации в группе:\n\n" + "\n".join(top_lines),
    )

    await db_session.close()
    logger.debug("Closed DB session after top request")
