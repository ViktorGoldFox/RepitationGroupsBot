from time import monotonic

from aiogram import BaseMiddleware
from aiogram.types import Message
from logzero import logger


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        start_time = monotonic()

        if isinstance(event, Message):
            username = event.from_user.username if event.from_user else "unknown"
            logger.info(
                "Incoming message | chat_id=%s | user=@%s | user_id=%s | text=%r",
                event.chat.id,
                username,
                event.from_user.id if event.from_user else None,
                event.text,
            )
        else:
            logger.info("Incoming event | type=%s", type(event).__name__)

        try:
            result = await handler(event, data)
            logger.debug(
                "Handled event | type=%s | duration=%.3fs",
                type(event).__name__,
                monotonic() - start_time,
            )
            return result
        except Exception:
            logger.exception(
                "Handler failed | type=%s | duration=%.3fs",
                type(event).__name__,
                monotonic() - start_time,
            )
            raise

