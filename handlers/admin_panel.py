"""
Admin panel handlers for Big Stepa Safe Escrow Bot.
Human-in-the-loop verification of payments and fund releases.
"""

import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database import Database
from database.db_methods import DealStatus
from config import config
from keyboards.inline import (
    get_admin_main_panel,
    get_admin_release_confirmation,
    get_delivery_confirmation,
    get_back_to_menu,
)

router = Router(name="admin_panel")
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Admin Access Filter
# ─────────────────────────────────────────────────────────────────────────────

def is_admin(user_id: int) -> bool:
    """Check if user is the admin."""
    return user_id == config.admin_id


# ─────────────────────────────────────────────────────────────────────────────
# Admin Commands
# ─────────────────────────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message, db: Database):
    """Show admin panel."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Access denied. Admin only.")
        return
    
    active_count = await db.get_active_deals_count()
    pending = await db.get_pending_payments()
    
    await message.answer(
        f"🛡️ <b>Admin Panel</b>\n\n"
        f"📊 Active deals: {active_count}\n"
        f"⏳ Pending verifications: {len(pending)}\n\n"
        f"Choose an action:",
        reply_markup=get_admin_main_panel(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin:pending")
async def show_pending_payments(callback: CallbackQuery, db: Database):
    """Show pending payment verifications."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied!", show_alert=True)
        return
    
    pending = await db.get_pending_payments()
    
    if not pending:
        await callback.message.edit_text(
            "✅ <b>No Pending Verifications</b>\n\n"
            "All payments have been verified!",
            reply_markup=get_admin_main_panel(),
            parse_mode="HTML"
        )
    else:
        text = "⏳ <b>Pending Payment Verifications</b>\n\n"
        for deal in pending[:10]:
            text += (
                f"<b>Deal #{deal['deal_id']}</b>\n"
                f"  💰 {deal['amount']} {deal['currency']}\n"
                f"  👤 Buyer: @{deal['buyer_username']}\n"
                f"  📦 {deal['item_description'][:30]}...\n\n"
            )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_admin_main_panel(),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def show_stats(callback: CallbackQuery, db: Database):
    """Show admin statistics."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied!", show_alert=True)
        return
    
    active_count = await db.get_active_deals_count()
    pending = await db.get_pending_payments()
    
    await callback.message.edit_text(
        f"📊 <b>Statistics</b>\n\n"
        f"🔥 Active deals: {active_count}\n"
        f"⏳ Pending verifications: {len(pending)}\n\n"
        f"<i>More stats coming soon...</i>",
        reply_markup=get_admin_main_panel(),
        parse_mode="HTML"
    )
    await callback.answer()


# ─────────────────────────────────────────────────────────────────────────────
# Payment Verification
# ─────────────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:") & F.data.endswith(":verify"))
async def admin_verify_payment(callback: CallbackQuery, db: Database, bot: Bot):
    """Admin confirms payment received."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied!", show_alert=True)
        return
    
    deal_id = int(callback.data.split(":")[1])
    deal = await db.get_deal(deal_id)
    
    if not deal:
        await callback.answer("Deal not found!", show_alert=True)
        return
    
    # Update status
    await db.update_deal_status(deal_id, DealStatus.PAYMENT_VERIFIED)
    
    # Remove buttons from admin message (works with both text and photo messages)
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
        pass  # Ignore if can't edit
    
    # Send confirmation to admin
    await bot.send_message(
        callback.from_user.id,
        f"✅ <b>Payment Verified!</b>\n\n"
        f"Deal #{deal_id} payment confirmed.\n"
        f"Notifying both parties...",
        parse_mode="HTML"
    )
    
    # Notify seller to start work
    try:
        await bot.send_message(
            deal["seller_id"],
            f"💰 <b>Funds Secured!</b>\n\n"
            f"Deal #{deal_id} payment has been verified!\n\n"
            f"📦 <b>Item:</b> {deal['item_description']}\n"
            f"💵 <b>Amount:</b> {deal['amount']} {deal['currency']}\n"
            f"⏰ <b>Deadline:</b> {deal['deadline_hours'] or 'Not set'} hours\n\n"
            f"You can now start working on the delivery.\n"
            f"Notify buyer when ready!",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to notify seller: {e}")
    
    # Notify buyer that payment is confirmed
    try:
        from keyboards.inline import get_delivery_confirmation
        # Get buyer's language
        buyer = await db.get_user(deal["buyer_id"])
        b_lang = buyer.get("language", "ru") if buyer else "ru"
        from locales.translations import get_text
        def _b(key, **kwargs): return get_text(key, b_lang, **kwargs)
        
        await bot.send_message(
            deal["buyer_id"],
            _b("payment_confirmed_buyer", deal_id=deal_id),
            reply_markup=get_delivery_confirmation(deal_id, _b),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to notify buyer: {e}")
    
    # Update to in_progress
    await db.update_deal_status(deal_id, DealStatus.IN_PROGRESS)
    
    await callback.answer("Payment verified! ✅")


@router.callback_query(F.data.startswith("admin:") & F.data.endswith(":reject"))
async def admin_reject_payment(callback: CallbackQuery, db: Database, bot: Bot):
    """Admin rejects payment (fake/not received)."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied!", show_alert=True)
        return
    
    deal_id = int(callback.data.split(":")[1])
    deal = await db.get_deal(deal_id)
    
    if not deal:
        await callback.answer("Deal not found!", show_alert=True)
        return
    
    # Revert to payment pending
    await db.update_deal_status(deal_id, DealStatus.PAYMENT_PENDING)
    
    await callback.message.edit_text(
        f"❌ <b>Payment Rejected</b>\n\n"
        f"Deal #{deal_id} payment was not verified.\n"
        f"Buyer has been notified to retry.",
        parse_mode="HTML"
    )
    
    # Notify buyer
    try:
        from keyboards.inline import get_payment_keyboard
        await bot.send_message(
            deal["buyer_id"],
            f"❌ <b>Payment Not Verified</b>\n\n"
            f"Your payment for Deal #{deal_id} could not be verified.\n\n"
            f"Possible reasons:\n"
            f"• Transaction not found\n"
            f"• Incorrect amount\n"
            f"• Different wallet address\n\n"
            f"Please try again or contact support.",
            reply_markup=get_payment_keyboard(deal_id),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to notify buyer of rejection: {e}")
    
    await callback.answer("Payment rejected ❌")


@router.callback_query(F.data.startswith("admin:") & F.data.endswith(":investigate"))
async def admin_investigate(callback: CallbackQuery, db: Database):
    """Admin wants to investigate further."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied!", show_alert=True)
        return
    
    deal_id = int(callback.data.split(":")[1])
    deal = await db.get_deal(deal_id)
    
    if not deal:
        await callback.answer("Deal not found!", show_alert=True)
        return
    
    await callback.message.answer(
        f"🔍 <b>Investigation Mode</b>\n\n"
        f"<b>Deal #{deal_id} Full Details:</b>\n\n"
        f"📦 Item: {deal['item_description']}\n"
        f"💰 Amount: {deal['amount']} {deal['currency']}\n"
        f"👤 Seller: @{deal['seller_username']} (ID: {deal['seller_id']})\n"
        f"👤 Buyer: @{deal['buyer_username']} (ID: {deal['buyer_id']})\n"
        f"⏰ Deadline: {deal['deadline_hours']} hours\n"
        f"📋 Status: {deal['status']}\n"
        f"💳 TXID: {deal['tx_id'] or 'Not provided'}\n"
        f"📄 Proof: {deal['payment_proof'][:50] if deal['payment_proof'] else 'None'}...\n"
        f"📅 Created: {deal['created_at']}\n"
        f"📅 Updated: {deal['updated_at']}",
        parse_mode="HTML"
    )
    await callback.answer()


# ─────────────────────────────────────────────────────────────────────────────
# Fund Release
# ─────────────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:") & F.data.endswith(":release"))
async def admin_release_funds(callback: CallbackQuery, db: Database, bot: Bot):
    """Admin confirms funds released to seller."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied!", show_alert=True)
        return
    
    deal_id = int(callback.data.split(":")[1])
    deal = await db.get_deal(deal_id)
    
    if not deal:
        await callback.answer("Deal not found!", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"💰 <b>Funds Released!</b>\n\n"
        f"Deal #{deal_id} funds sent to @{deal['seller_username']}.\n"
        f"Amount: {deal['amount']} {deal['currency']}\n\n"
        f"✅ Deal officially completed!",
        parse_mode="HTML"
    )
    
    # Notify seller
    try:
        await bot.send_message(
            deal["seller_id"],
            f"💰 <b>Payment Received!</b>\n\n"
            f"You should receive {deal['amount']} {deal['currency']} for Deal #{deal_id}.\n\n"
            f"Thank you for using Big Stepa Safe! 🛡️\n"
            f"Please confirm receipt.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to notify seller of release: {e}")
    
    await callback.answer("Funds released! 💰")


@router.callback_query(F.data.startswith("admin:") & F.data.endswith(":hold"))
async def admin_hold_funds(callback: CallbackQuery, db: Database):
    """Admin holds funds for review."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied!", show_alert=True)
        return
    
    deal_id = int(callback.data.split(":")[1])
    deal = await db.get_deal(deal_id)
    
    if not deal:
        await callback.answer("Deal not found!", show_alert=True)
        return
    
    await db.update_deal_status(deal_id, DealStatus.DISPUTED)
    
    await callback.message.edit_text(
        f"⏸️ <b>Funds on Hold</b>\n\n"
        f"Deal #{deal_id} requires manual review.\n"
        f"Contact both parties for resolution.",
        reply_markup=get_admin_main_panel(),
        parse_mode="HTML"
    )
    await callback.answer("Funds held for review")
