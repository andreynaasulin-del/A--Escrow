"""
Big Stepa Safe — Telegram Escrow Bot
Entry point for running the bot.

Architecture:
- AI (Claude) parses natural language deal descriptions
- Human (Admin) verifies payments for safety
- FSM manages user state throughout deal flow
"""

import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database import Database
from services import AIService
from handlers import setup_routers


# ─────────────────────────────────────────────────────────────────────────────
# Logging Configuration
# ─────────────────────────────────────────────────────────────────────────────

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Reduce noise from external libraries
logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Dependency Injection Middleware
# ─────────────────────────────────────────────────────────────────────────────

class DependencyMiddleware:
    """Injects shared dependencies (db, ai_service) into handlers."""
    
    def __init__(self, db: Database, ai_service: AIService):
        self.db = db
        self.ai_service = ai_service
    
    async def __call__(self, handler, event, data):
        data["db"] = self.db
        data["ai_service"] = self.ai_service
        return await handler(event, data)


# ─────────────────────────────────────────────────────────────────────────────
# Main Bot Function
# ─────────────────────────────────────────────────────────────────────────────

async def main():
    """Initialize and run the bot."""
    logger.info("🚀 Starting Big Stepa Safe Escrow Bot...")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Initialize Services
    # ─────────────────────────────────────────────────────────────────────────
    
    # Database
    db = Database(config.db_path)
    await db.connect()
    logger.info("✅ Database connected")
    
    # AI Service
    ai_service = AIService(config.openai_api_key)
    logger.info("✅ AI Service initialized (OpenAI GPT-4o)")
    
    # Health check AI
    if await ai_service.health_check():
        logger.info("✅ AI Service health check passed")
    else:
        logger.warning("⚠️ AI Service health check failed — bot will continue but AI parsing may not work")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Initialize Bot & Dispatcher
    # ─────────────────────────────────────────────────────────────────────────
    
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # FSM storage (use Redis in production for persistence)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Setup Middleware & Routers
    # ─────────────────────────────────────────────────────────────────────────
    
    # Register dependency    # Middlewares
    from locales.middleware import L10nMiddleware
    dp.update.middleware(L10nMiddleware(db))
    
    # Register dependency middleware
    dependency_middleware = DependencyMiddleware(db, ai_service)
    dp.message.middleware(dependency_middleware)
    dp.callback_query.middleware(dependency_middleware)
    
    # Setup routers
    main_router = setup_routers()
    dp.include_router(main_router)
    
    logger.info("✅ Handlers registered")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Startup Notification
    # ─────────────────────────────────────────────────────────────────────────
    
    try:
        me = await bot.get_me()
        logger.info(f"🤖 Bot username: @{me.username}")
        
        # Notify admin that bot started
        await bot.send_message(
            config.admin_id,
            f"🟢 <b>Bot Started</b>\n\n"
            f"Big Stepa Safe is online!\n"
            f"@{me.username}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning(f"Could not send startup notification: {e}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Start Polling
    # ─────────────────────────────────────────────────────────────────────────
    
    logger.info("🛡️ Big Stepa Safe is now running!")
    logger.info(f"👤 Admin ID: {config.admin_id}")
    logger.info(f"💳 Wallet: {config.wallet_address[:20]}...")
    
    try:
        # Delete webhook if any and start polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # Cleanup
        logger.info("🔴 Shutting down...")
        await db.close()
        await bot.session.close()
        logger.info("👋 Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
