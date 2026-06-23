from datetime import datetime, timedelta, timezone

from aiogram import Bot, types
from aiogram.filters import Filter
from logzero import logger
from sqlalchemy import and_, delete, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import db_helper
from database.models import Groups, GroupUser, RepitationActions, Users


class IsReplyMessage(Filter):
    async def __call__(self, message: types.Message) -> bool:
        is_reply = message.reply_to_message is not None
        logger.debug(
            "Filter IsReplyMessage | chat_id=%s | message_id=%s | result=%s",
            message.chat.id,
            message.message_id,
            is_reply,
        )
        return is_reply


class IsGroup(Filter):
    async def __call__(self, message: types.Message) -> bool:
        if message.chat.type not in ["group", "supergroup"]:
            logger.info(
                "Filter IsGroup rejected message | chat_id=%s | chat_type=%s | message_id=%s",
                message.chat.id,
                message.chat.type,
                message.message_id,
            )
            await message.answer("Эта команда работает только в группе.")

            return False

        logger.debug(
            "Filter IsGroup passed | chat_id=%s | chat_type=%s | message_id=%s",
            message.chat.id,
            message.chat.type,
            message.message_id,
        )
        return True


class EnsureRepitationRegistration(Filter):
    async def __call__(self, message: types.Message) -> bool:
        db_session: AsyncSession = db_helper.get_scoped_session()
        logger.debug(
            "Filter EnsureRepitationRegistration checking | chat_id=%s | user_id=%s",
            message.chat.id,
            message.reply_to_message.from_user.id,
        )

        group_stmt = select(exists(Groups).where(Groups.t_chat_id == message.chat.id))
        user_stmt = select(
            exists(Users).where(Users.t_user_id == message.reply_to_message.from_user.id)
        )
        link_stmt = select(
            exists(GroupUser).where(
                and_(
                    GroupUser.user_id == message.reply_to_message.from_user.id,
                    GroupUser.group_id == message.chat.id,
                )
            )
        )

        is_group_exists = await db_session.scalar(group_stmt)
        if not is_group_exists:
            logger.info("Registering new group | chat_id=%s", message.chat.id)
            db_session.add(Groups(t_chat_id=message.chat.id))

        is_user_exists = await db_session.scalar(user_stmt)
        if not is_user_exists:
            logger.info(
                "Registering new user | user_id=%s | username=@%s",
                message.reply_to_message.from_user.id,
                message.reply_to_message.from_user.username,
            )
            db_session.add(
                Users(
                    t_user_id=message.reply_to_message.from_user.id,
                    t_user_name=message.reply_to_message.from_user.username,
                    t_user_fullname=message.reply_to_message.from_user.full_name,
                )
            )

        is_link_exists = await db_session.scalar(link_stmt)
        if not is_link_exists:
            logger.info(
                "Linking user to group | user_id=%s | group_id=%s",
                message.reply_to_message.from_user.id,
                message.chat.id,
            )
            db_session.add(
                GroupUser(
                    user_id=message.reply_to_message.from_user.id,
                    group_id=message.chat.id,
                )
            )

        await db_session.commit()
        await db_session.close()
        return True


class CheckArgsColl(Filter):
    def __init__(self, await_args_coll: int, is_hard_check: bool = True) -> None:
        self.await_args_coll: int = await_args_coll
        self.is_hard_check: bool = is_hard_check

    async def __call__(self, message: types.Message) -> bool:
        logger.debug(
            "Filter CheckArgsColl | message_id=%s | text=%r | expected=%s | hard=%s",
            message.message_id,
            message.text,
            self.await_args_coll,
            self.is_hard_check,
        )
        if self.is_hard_check:
            if (len(str(message.text).split()) - 1) != self.await_args_coll:
                logger.info(
                    "Filter CheckArgsColl rejected | message_id=%s | expected=%s | actual=%s",
                    message.message_id,
                    self.await_args_coll,
                    len(str(message.text).split()) - 1,
                )
                await message.answer(
                    f"Недостаточно аргументов. Ожидалось {self.await_args_coll}."
                )

                return False
        else:
            if (len(str(message.text).split()) - 1) < self.await_args_coll:
                logger.info(
                    "Filter CheckArgsColl rejected | message_id=%s | expected_min=%s | actual=%s",
                    message.message_id,
                    self.await_args_coll,
                    len(str(message.text).split()) - 1,
                )
                await message.answer(
                    f"Недостаточно аргументов. Ожидалось {self.await_args_coll}."
                )

                return False

        return True


class NotReplyToMind(Filter):
    async def __call__(self, message: types.Message) -> bool:
        if message.from_user.id == message.reply_to_message.from_user.id:
            logger.info(
                "Filter NotReplyToMind rejected self-action | user_id=%s | message_id=%s",
                message.from_user.id,
                message.message_id,
            )
            await message.reply("Нельзя менять репутацию самому себе.")

            return False

        logger.debug(
            "Filter NotReplyToMind passed | actor_id=%s | target_id=%s | message_id=%s",
            message.from_user.id,
            message.reply_to_message.from_user.id,
            message.message_id,
        )
        return True


class IsAdmin(Filter):
    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)

        if member.status not in {"administrator", "creator"}:
            logger.info(
                "Filter IsAdmin rejected | user_id=%s | chat_id=%s | status=%s",
                message.from_user.id,
                message.chat.id,
                member.status,
            )
            await message.reply("Команда /setrep доступна только администраторам группы.")
            return False

        logger.debug(
            "Filter IsAdmin passed | user_id=%s | chat_id=%s | status=%s",
            message.from_user.id,
            message.chat.id,
            member.status,
        )
        return True


class RepitationRateLimit(Filter):
    def __init__(self, max_actions: int = 3, window_seconds: int = 300) -> None:
        self.max_actions = max_actions
        self.window_seconds = window_seconds

    async def __call__(self, message: types.Message) -> bool:
        action = str(message.text or "").strip()
        db_session: AsyncSession = db_helper.get_scoped_session()
        logger.debug(
            "Filter RepitationRateLimit checking | chat_id=%s | user_id=%s | action=%s",
            message.chat.id,
            message.from_user.id,
            action,
        )

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=self.window_seconds)

        await db_session.execute(
            delete(RepitationActions).where(RepitationActions.created_at < cutoff)
        )

        count_stmt = select(func.count()).select_from(RepitationActions).where(
            RepitationActions.t_chat_id == message.chat.id,
            RepitationActions.t_user_id == message.from_user.id,
            RepitationActions.created_at >= cutoff,
        )
        actions_count = await db_session.scalar(count_stmt) or 0

        if actions_count >= self.max_actions:
            oldest_stmt = (
                select(RepitationActions.created_at)
                .where(
                    RepitationActions.t_chat_id == message.chat.id,
                    RepitationActions.t_user_id == message.from_user.id,
                    RepitationActions.created_at >= cutoff,
                )
                .order_by(RepitationActions.created_at.asc())
                .limit(1)
            )
            oldest_action = await db_session.scalar(oldest_stmt)

            if oldest_action is None:
                retry_after = self.window_seconds
            else:
                elapsed = (now - oldest_action).total_seconds()
                retry_after = max(int(self.window_seconds - elapsed) + 1, 1)

            await db_session.commit()
            await db_session.close()
            logger.info(
                "Filter RepitationRateLimit rejected | chat_id=%s | user_id=%s | action=%s | count=%s | retry_after=%s",
                message.chat.id,
                message.from_user.id,
                action,
                actions_count,
                retry_after,
            )
            await message.reply(
                f"Слишком часто. Можно использовать +реп/-реп не более 3 раз за 5 минут.\n"
                f"Попробуй снова через {retry_after} сек."
            )
            return False

        db_session.add(
            RepitationActions(
                t_chat_id=message.chat.id,
                t_user_id=message.from_user.id,
                action=action,
            )
        )
        await db_session.commit()
        await db_session.close()
        logger.debug(
            "Filter RepitationRateLimit passed | chat_id=%s | user_id=%s | action=%s | count=%s",
            message.chat.id,
            message.from_user.id,
            action,
            actions_count + 1,
        )
        return True
