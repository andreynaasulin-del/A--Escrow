"""
Middleware for handling user localization.
Automatically detects user language and injects it into handler context.
"""

from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from database import Database
from locales.translations import get_text


class L10nMiddleware(BaseMiddleware):
    """
    Middleware that determines the user's language and provides 
    a translation helper function to handlers.
    """
    
    def __init__(self, db: Database):
        self.db = db
        super().__init__()
        
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Get user from event
        user: User = data.get("event_from_user")
        
        if not user:
            return await handler(event, data)
            
        # Get user from database to find language preference
        db_user = await self.db.get_user(user.id)
        
        # Determine language: prioritize DB setting, default to Russian
        if db_user and db_user.get("language"):
            # User has explicit language preference
            lang = db_user["language"]
        else:
            # New user or no preference - default to Russian
            lang = "ru"
            
        # Add language and translation helper to data
        data["lang"] = lang
        
        # Create a tiny helper for the handler
        def _(key: str, **kwargs) -> str:
            return get_text(key, lang, **kwargs)
            
        data["_"] = _
        
        return await handler(event, data)
