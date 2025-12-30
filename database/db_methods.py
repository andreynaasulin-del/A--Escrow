"""
Database methods for Big Stepa Safe Escrow Bot.
Uses aiosqlite for async SQLite operations.
"""

import aiosqlite
import logging
from datetime import datetime
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class DealStatus(str, Enum):
    """Deal lifecycle states."""
    DRAFT = "draft"                    # AI parsed, awaiting confirmation
    PENDING_BUYER = "pending_buyer"    # Waiting for buyer confirmation
    PENDING_SELLER = "pending_seller"  # Waiting for seller confirmation
    CONFIRMED = "confirmed"            # Both parties confirmed
    PAYMENT_PENDING = "payment_pending"  # Waiting for buyer payment
    PAYMENT_SENT = "payment_sent"      # Buyer claims payment sent
    PAYMENT_VERIFIED = "payment_verified"  # Admin verified payment
    IN_PROGRESS = "in_progress"        # Seller working on delivery
    DELIVERED = "delivered"            # Seller delivered item
    COMPLETED = "completed"            # Buyer confirmed receipt, funds released
    DISPUTED = "disputed"              # Dispute raised
    CANCELLED = "cancelled"            # Deal cancelled


class Database:
    """Async SQLite database manager for escrow deals."""
    
    def __init__(self, db_path: str = "escrow.db"):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self) -> None:
        """Establish database connection and create tables."""
        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        await self._create_tables()
        logger.info(f"📦 Database connected: {self.db_path}")
    
    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            logger.info("📦 Database connection closed")
    
    async def _create_tables(self) -> None:
        """Create required database tables."""
        await self._connection.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                language TEXT DEFAULT 'ru',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS deals (
                deal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                creator_id INTEGER NOT NULL,
                seller_id INTEGER,
                seller_username TEXT,
                buyer_id INTEGER,
                buyer_username TEXT,
                amount REAL NOT NULL,
                currency TEXT NOT NULL DEFAULT 'USDT',
                item_description TEXT NOT NULL,
                deadline_hours INTEGER,
                status TEXT NOT NULL DEFAULT 'draft',
                payment_proof TEXT,
                tx_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (creator_id) REFERENCES users (user_id)
            );
            
            CREATE TABLE IF NOT EXISTS deal_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                deal_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deal_id) REFERENCES deals (deal_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_deals_status ON deals (status);
            CREATE INDEX IF NOT EXISTS idx_deals_seller ON deals (seller_id);
            CREATE INDEX IF NOT EXISTS idx_deals_buyer ON deals (buyer_id);
        """)
        await self._connection.commit()
    
    # ─────────────────────────────────────────────────────────────────────
    # User Methods
    # ─────────────────────────────────────────────────────────────────────
    
    async def upsert_user(self, user_id: int, username: Optional[str], first_name: Optional[str]) -> None:
        """Insert or update user information."""
        await self._connection.execute(
            """
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
            """,
            (user_id, username, first_name)
        )
        await self._connection.commit()

    async def update_user_language(self, user_id: int, language: str) -> None:
        """Update user's language preference."""
        await self._connection.execute(
            "UPDATE users SET language = ? WHERE user_id = ?",
            (language, user_id)
        )
        await self._connection.commit()
        logger.info(f"🌐 User {user_id} changed language to: {language}")
    
    async def get_user(self, user_id: int) -> Optional[dict]:
        """Get user by ID."""
        async with self._connection.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def find_user_by_username(self, username: str) -> Optional[dict]:
        """Find user by Telegram username."""
        # Normalize username (remove @ if present)
        username = username.lstrip("@")
        async with self._connection.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    # ─────────────────────────────────────────────────────────────────────
    # Deal Methods
    # ─────────────────────────────────────────────────────────────────────
    
    async def create_deal(
        self,
        creator_id: int,
        amount: float,
        currency: str,
        item_description: str,
        seller_username: Optional[str] = None,
        buyer_username: Optional[str] = None,
        deadline_hours: Optional[int] = None,
    ) -> int:
        """Create a new deal and return its ID."""
        cursor = await self._connection.execute(
            """
            INSERT INTO deals (
                creator_id, seller_username, buyer_username,
                amount, currency, item_description, deadline_hours, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                creator_id,
                seller_username,
                buyer_username,
                amount,
                currency,
                item_description,
                deadline_hours,
                DealStatus.DRAFT.value,
            )
        )
        await self._connection.commit()
        logger.info(f"✅ Deal #{cursor.lastrowid} created by user {creator_id}")
        return cursor.lastrowid
    
    async def get_deal(self, deal_id: int) -> Optional[dict]:
        """Get deal by ID."""
        async with self._connection.execute(
            "SELECT * FROM deals WHERE deal_id = ?", (deal_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def update_deal_status(self, deal_id: int, status: DealStatus) -> None:
        """Update deal status."""
        await self._connection.execute(
            """
            UPDATE deals 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE deal_id = ?
            """,
            (status.value, deal_id)
        )
        await self._connection.commit()
        logger.info(f"📝 Deal #{deal_id} status -> {status.value}")
    
    async def set_deal_seller(self, deal_id: int, seller_id: int, seller_username: Optional[str]) -> None:
        """Set the seller for a deal."""
        await self._connection.execute(
            """
            UPDATE deals 
            SET seller_id = ?, seller_username = ?, updated_at = CURRENT_TIMESTAMP
            WHERE deal_id = ?
            """,
            (seller_id, seller_username, deal_id)
        )
        await self._connection.commit()
    
    async def set_deal_buyer(self, deal_id: int, buyer_id: int, buyer_username: Optional[str]) -> None:
        """Set the buyer for a deal."""
        await self._connection.execute(
            """
            UPDATE deals 
            SET buyer_id = ?, buyer_username = ?, updated_at = CURRENT_TIMESTAMP
            WHERE deal_id = ?
            """,
            (buyer_id, buyer_username, deal_id)
        )
        await self._connection.commit()
    
    async def set_payment_proof(self, deal_id: int, proof: str, tx_id: Optional[str] = None) -> None:
        """Store payment proof (file_id or text) and optional TXID."""
        await self._connection.execute(
            """
            UPDATE deals 
            SET payment_proof = ?, tx_id = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE deal_id = ?
            """,
            (proof, tx_id, DealStatus.PAYMENT_SENT.value, deal_id)
        )
        await self._connection.commit()
    
    async def complete_deal(self, deal_id: int) -> None:
        """Mark deal as completed."""
        await self._connection.execute(
            """
            UPDATE deals 
            SET status = ?, completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE deal_id = ?
            """,
            (DealStatus.COMPLETED.value, deal_id)
        )
        await self._connection.commit()
        logger.info(f"🎉 Deal #{deal_id} completed!")
    
    async def get_user_deals(self, user_id: int, status: Optional[DealStatus] = None) -> list[dict]:
        """Get all deals where user is seller or buyer."""
        query = """
            SELECT * FROM deals 
            WHERE (seller_id = ? OR buyer_id = ? OR creator_id = ?)
        """
        params = [user_id, user_id, user_id]
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        query += " ORDER BY created_at DESC"
        
        async with self._connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_pending_payments(self) -> list[dict]:
        """Get all deals awaiting admin payment verification."""
        async with self._connection.execute(
            "SELECT * FROM deals WHERE status = ? ORDER BY updated_at ASC",
            (DealStatus.PAYMENT_SENT.value,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_active_deals_count(self) -> int:
        """Get count of active deals (not completed/cancelled)."""
        async with self._connection.execute(
            """
            SELECT COUNT(*) FROM deals 
            WHERE status NOT IN (?, ?)
            """,
            (DealStatus.COMPLETED.value, DealStatus.CANCELLED.value)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0
