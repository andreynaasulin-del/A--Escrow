"""
Configuration loader for Big Stepa Safe Escrow Bot.
Loads environment variables and provides centralized config access.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Bot configuration container."""
    
    bot_token: str
    openai_api_key: str
    admin_id: int
    wallet_address: str
    db_path: str = "escrow.db"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        bot_token = os.getenv("BOT_TOKEN")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        admin_id = os.getenv("ADMIN_ID")
        wallet_address = os.getenv("WALLET_ADDRESS", "TRC20_WALLET_NOT_SET")
        
        if not bot_token:
            raise ValueError("BOT_TOKEN is required in .env")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is required in .env")
        if not admin_id:
            raise ValueError("ADMIN_ID is required in .env")
        
        return cls(
            bot_token=bot_token,
            openai_api_key=openai_api_key,
            admin_id=int(admin_id),
            wallet_address=wallet_address,
        )


# Global config instance
config = Config.from_env()
