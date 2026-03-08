from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from config import settings


class AccessControlMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        from_user = getattr(event, "from_user", None)

        if from_user is None:
            message = getattr(event, "message", None)
            if message is not None:
                from_user = getattr(message, "from_user", None)

        if from_user is None:
            return await handler(event, data)

        if from_user.id not in settings.allowed_user_ids:
            return None

        return await handler(event, data)