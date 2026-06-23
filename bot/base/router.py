from aiogram import Router, types
from aiogram.filters import Command
from logzero import logger

base_router = Router()


@base_router.message(Command("start"))
async def bot_start(message: types.Message):
    logger.info(
        "Command /start | user=@%s | user_id=%s | chat_id=%s",
        message.from_user.username,
        message.from_user.id,
        message.chat.id,
    )

    await message.answer(
        "Привет. Я бот для репутации в группах.\n\n"
        "Что умею:\n"
        "• +реп - поднять репутацию в ответ на сообщение\n"
        "• -реп - понизить репутацию в ответ на сообщение\n"
        "• /setrep <число> - установить точную репутацию\n"
        "• топ реп - показать топ участников по репутации\n\n"
        "Ограничение: +реп и -реп можно использовать не чаще 3 раз за 5 минут.\n"
        "Напиши /help, если нужна краткая справка."
    )

    logger.debug("Sent /start response to user_id=%s", message.from_user.id)


@base_router.message(Command("help"))
async def bot_help(message: types.Message):
    logger.info(
        "Command /help | user=@%s | user_id=%s | chat_id=%s",
        message.from_user.username,
        message.from_user.id,
        message.chat.id,
    )

    await message.answer(
        "Справка по командам:\n\n"
        "• /start - приветствие и список возможностей\n"
        "• /help - эта справка\n"
        "• топ реп - топ участников группы\n\n"
        "Работает в ответ на сообщение пользователя:\n"
        "• +реп - повысить репутацию\n"
        "• -реп - понизить репутацию\n"
        "• /setrep <число> - установить конкретную репутацию (только админы)\n\n"
        "Ограничение: +реп и -реп можно использовать не чаще 3 раз за 5 минут.\n\n"
        "Пример: ответь на сообщение и отправь +реп."
    )

    logger.debug("Sent /help response to user_id=%s", message.from_user.id)
