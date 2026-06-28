from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.repitation.filters import IsAdmin, IsGroup
from bot.rest import crud
from bot.utils.formatting import format_user_mention_html, format_user_storage
from database import db_helper

rest_router = Router()


def _parse_rest_arguments(
    message: Message,
) -> tuple[int | None, str | None, str | None]:
    args = str(message.text or "").split()[1:]

    if message.reply_to_message:
        if not args:
            return message.reply_to_message.from_user.id, None, None

        if args[0].casefold() != "до":
            return (
                None,
                None,
                (
                    "Неверные аргументы.\n"
                    "Используй: ответом на сообщение `/rest` или `/rest до <дата>`."
                ),
            )

        if len(args) < 2:
            return None, None, "Не указано время окончания реста."

        return message.reply_to_message.from_user.id, args[1], None

    if not args:
        return (
            None,
            None,
            (
                "Неверные аргументы.\n"
                "Используй: `/rest` в ответ на сообщение или `/rest <user_id> [до <дата>]`."
            ),
        )

    if args[0].casefold() == "до":
        return (
            None,
            None,
            ("Сначала укажи пользователя.\nИспользуй: `/rest <user_id> [до <дата>]`."),
        )

    try:
        target_id = int(args[0])
    except ValueError:
        return None, None, "Первый аргумент должен быть `user_id`."

    if len(args) == 1:
        return target_id, None, None

    if args[1].casefold() != "до":
        return (
            None,
            None,
            ("Неверные аргументы.\nИспользуй: `/rest <user_id> [до <дата>]`."),
        )

    if len(args) < 3:
        return None, None, "Не указано время окончания реста."

    return target_id, args[2], None


async def _resolve_user_storage(
    bot: Bot, chat_id: int, user_id: int | None, message_user
) -> str:
    if message_user is not None:
        return format_user_storage(
            message_user.username,
            message_user.full_name,
        )

    if user_id is None:
        return "Unknown user"

    try:
        chat_member = await bot.get_chat_member(chat_id, user_id)
    except Exception:
        return str(user_id)

    return format_user_storage(chat_member.user.username, chat_member.user.full_name)


def _render_user_label_html(user_id: int, label: str | None) -> str:
    if not label:
        return "Unknown user"

    if label.startswith("@"):
        return format_user_mention_html(user_id, label[1:], None)

    if label.isdigit():
        return label

    return format_user_mention_html(user_id, None, label)


def _validate_end_at(end_at: str | None) -> str | None:
    if end_at is None:
        return None

    if end_at.casefold() in {"неизвестно", "unknown"}:
        return None

    datetime.fromisoformat(end_at)
    return end_at


@rest_router.message(Command("rest"), IsGroup(), IsAdmin())
async def assing_rest(message: Message, bot: Bot):
    db_session: AsyncSession = db_helper.get_scoped_session()
    try:
        target_id, end_at, error = _parse_rest_arguments(message)
        if error:
            await message.reply(error, parse_mode=ParseMode.HTML)
            return

        if target_id is None:
            await message.reply("Не удалось определить пользователя.")
            return

        try:
            end_at = _validate_end_at(end_at)
        except ValueError:
            await message.reply(
                "Неверный формат времени.\n"
                "Используй ISO формат, например: `2026-06-28T18:30:00`, "
                "либо не указывай время вовсе.",
                parse_mode=ParseMode.HTML,
            )
            return

        target_display = await _resolve_user_storage(
            bot=bot,
            chat_id=message.chat.id,
            user_id=target_id,
            message_user=message.reply_to_message.from_user
            if message.reply_to_message
            else None,
        )
        issuer_display = format_user_storage(
            message.from_user.username,
            message.from_user.full_name,
        )

        await crud.issued_rest(
            target_t_user_id=target_id,
            target_display=target_display,
            issued_by_t_user_id=message.from_user.id,
            issued_by_display=issuer_display,
            end_at=end_at,
            t_chat_id=message.chat.id,
            db_session=db_session,
        )

        await message.reply(
            f"{format_user_mention_html(message.from_user.id, message.from_user.username, message.from_user.full_name)} "
            f"выдал рест {_render_user_label_html(target_id, target_display)} "
            f"до {end_at or 'неизвестно'}",
            parse_mode=ParseMode.HTML,
        )
    finally:
        await db_session.close()


@rest_router.message(Command("unrest"), IsGroup(), IsAdmin())
async def unrest(message: Message, bot: Bot):
    db_session: AsyncSession = db_helper.get_scoped_session()
    try:
        args = str(message.text).split()[1:]
        if not message.reply_to_message and not args:
            await message.reply(
                "Неверные аргументы.\n"
                "Используй: `/unrest` в ответ на сообщение или `/unrest <user_id>`.",
                parse_mode=ParseMode.HTML,
            )
            return

        if message.reply_to_message:
            target_id = message.reply_to_message.from_user.id
        else:
            try:
                target_id = int(args[0])
            except ValueError:
                await message.reply(
                    "Первый аргумент должен быть `user_id`.", parse_mode=ParseMode.HTML
                )
                return

        target_display = await _resolve_user_storage(
            bot=bot,
            chat_id=message.chat.id,
            user_id=target_id,
            message_user=message.reply_to_message.from_user
            if message.reply_to_message
            else None,
        )

        await crud.delete_rest(
            t_chat_id=message.chat.id, target_t_user_id=target_id, db_session=db_session
        )

        await message.reply(
            f"{format_user_mention_html(message.from_user.id, message.from_user.username, message.from_user.full_name)} "
            f"снял рест {_render_user_label_html(target_id, target_display)}",
            parse_mode=ParseMode.HTML,
        )
    finally:
        await db_session.close()


@rest_router.message(
    F.text.casefold().strip().in_({"кто рест", "кто отдыхает"}), IsGroup(), IsAdmin()
)
async def show_all_rests(message: Message):
    db_session: AsyncSession = db_helper.get_scoped_session()
    try:
        all_rests = await crud.get_all_rest(
            t_chat_id=message.chat.id, db_session=db_session
        )

        if not all_rests:
            await message.reply("Сейчас никто не стоит на ресте.")
            return

        rest_lines = []
        for rest in all_rests:
            if isinstance(rest.end_at, datetime):
                end_at = rest.end_at.strftime("%d.%m.%Y %H:%M")
            else:
                end_at = "без срока"

            created_at = (
                rest.created_at.strftime("%d.%m.%Y %H:%M")
                if isinstance(rest.created_at, datetime)
                else "неизвестно"
            )
            target_display = _render_user_label_html(
                rest.target_t_user_id, rest.target_display
            )
            issued_by_display = _render_user_label_html(
                rest.issued_by, rest.issued_by_display
            )

            rest_lines.append(
                f"• {target_display} | выдал: {issued_by_display} | когда: {created_at} | до: {end_at}"
            )

        await message.reply(
            "Кто сейчас на ресте:\n\n" + "\n".join(rest_lines),
            parse_mode=ParseMode.HTML,
        )
    finally:
        await db_session.close()
