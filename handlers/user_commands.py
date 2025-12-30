"""
User command handlers for Big Stepa Safe Escrow Bot.
Handles /start, /help, main menu navigation.
"""

import logging
from typing import Callable
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import Database
from keyboards.inline import get_main_menu, get_back_to_menu, get_settings_keyboard

router = Router(name="user_commands")
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Welcome Messages
# ─────────────────────────────────────────────────────────────────────────────

WELCOME_MESSAGE = """
🛡️ <b>Big Stepa Safe</b> — Secure Escrow Service

Welcome! I help you make safe deals with strangers online.

<b>How it works:</b>
1️⃣ <b>Create Deal</b> — Describe your trade in plain text
2️⃣ <b>AI Parses</b> — I extract deal details automatically  
3️⃣ <b>Both Confirm</b> — Seller & Buyer accept terms
4️⃣ <b>Buyer Pays</b> — Funds go to escrow wallet
5️⃣ <b>Admin Verifies</b> — Human confirms payment
6️⃣ <b>Seller Delivers</b> — Product/service sent
7️⃣ <b>Funds Released</b> — Seller gets paid

🔐 <b>Your safety is guaranteed</b> — no one loses money!

Choose an action below:
"""

HOW_IT_WORKS = """
📖 <b>How Big Stepa Safe Works</b>

<b>For Sellers:</b>
• Guaranteed payment before you start work
• Buyer can't run away with your product
• Dispute resolution if issues arise

<b>For Buyers:</b>
• Money stays safe until you receive the item
• Full refund if seller fails to deliver
• Human admin reviews every transaction

<b>Fees:</b>
• 3% escrow fee (paid by initiator)
• Minimum deal: $10 equivalent

<b>Supported Currencies:</b>
USDT (TRC20), BTC, ETH, RUB (SBP), USD

⚠️ <b>Important:</b>
• Never send payment outside this bot
• Always wait for admin confirmation
• Keep proof of all communications
"""

SUPPORT_MESSAGE = """
📞 <b>Support</b>

Having issues? Contact our admin directly:

👤 @BigStepaNino (Admin)

<b>Response time:</b> Usually within 1 hour

For urgent matters (active deal issues), reply to this message with:
• Your deal ID
• Description of the problem
"""


# ─────────────────────────────────────────────────────────────────────────────
# Command Handlers
# ─────────────────────────────────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: Message, db: Database, state: FSMContext, _: Callable):
    """Handle /start command."""
    # Clear any existing state
    await state.clear()
    
    # Register/update user in database
    await db.upsert_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    logger.info(f"👤 User started: {message.from_user.id} (@{message.from_user.username})")
    
    await message.answer(
        _("welcome"),
        reply_markup=get_main_menu(_),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "settings")
async def callback_settings(callback: CallbackQuery, _: Callable):
    """Show settings menu."""
    await callback.message.edit_text(
        _("settings_title"),
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_lang:"))
async def callback_set_lang(callback: CallbackQuery, db: Database, state: FSMContext):
    """Change user language."""
    new_lang = callback.data.split(":")[1]
    await db.update_user_language(callback.from_user.id, new_lang)
    
    # We need a new translation function for the current request
    from locales.translations import get_text
    def _new(key: str, **kwargs) -> str:
        return get_text(key, new_lang, **kwargs)
        
    await callback.message.edit_text(
        _new("main_menu_title"),
        reply_markup=get_main_menu(_new),
        parse_mode="HTML"
    )
    await callback.answer(f"Language changed to {new_lang.upper()}")


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext, _: Callable):
    """Return to main menu."""
    await state.clear()
    await callback.message.edit_text(
        _("main_menu_title"),
        reply_markup=get_main_menu(_),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery, state: FSMContext, _: Callable):
    """Cancel current operation and return to menu."""
    await state.clear()

    # Using a generic cancel message or main menu
    await callback.message.edit_text(
        _("main_menu_title"),
        reply_markup=get_main_menu(_),
        parse_mode="HTML"
    )
    await callback.answer("Cancelled")


@router.callback_query(F.data == "how_it_works")
async def callback_how_it_works(callback: CallbackQuery, _: Callable):
    """Show how the escrow service works."""
    await callback.message.edit_text(
        HOW_IT_WORKS,
        reply_markup=get_back_to_menu(_),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "support")
async def callback_support(callback: CallbackQuery, _: Callable):
    """Show support contact information."""
    await callback.message.edit_text(
        SUPPORT_MESSAGE,
        reply_markup=get_back_to_menu(_),
        parse_mode="HTML"
    )
    await callback.answer()
