from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Any, Dict
from sqlalchemy.ext.asyncio import async_sessionmaker
from aiogram.types import Message

class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker: async_sessionmaker):
        self.sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        async with self.sessionmaker() as session:
            data["session"] = session 
            return await handler(event, data)