"""
Deal flow handlers for Big Stepa Safe Escrow Bot.
Manages the complete deal lifecycle using FSM states.
"""

import logging
from typing import Callable
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from database.db_methods import DealStatus
from services import AIService
from services.ai_service import ParsedDeal
from config import config
from keyboards.inline import (
    get_main_menu,
    get_deal_role_selection,
    get_deal_confirmation,
    get_partner_confirmation,
    get_payment_keyboard,
    get_delivery_confirmation,
    get_cancel_keyboard,
    get_deal_list_keyboard,
    get_back_to_menu,
    get_settings_keyboard,
)

router = Router(name="deal_flow")
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# [AUDIT FIX] Security Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

def can_access_deal(user_id: int, deal: dict | None) -> bool:
    """
    [AUDIT FIX] Check if user has permission to access/modify a deal.
    Returns True if user is seller, buyer, or creator.
    """
    if not deal:
        return False
    
    allowed_ids = [
        deal.get("seller_id"),
        deal.get("buyer_id"), 
        deal.get("creator_id"),
    ]
    return user_id in [uid for uid in allowed_ids if uid is not None]


def safe_parse_deal_id(callback_data: str) -> int | None:
    """
    [AUDIT FIX] Safely parse deal_id from callback data.
    Returns None if parsing fails (prevents injection attacks).
    """
    try:
        parts = callback_data.split(":")
        if len(parts) >= 2:
            return int(parts[1])
    except (ValueError, IndexError):
        pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# FSM States
# ─────────────────────────────────────────────────────────────────────────────

class DealCreation(StatesGroup):
    """States for deal creation flow."""
    selecting_role = State()
    entering_description = State()
    confirming_deal = State()
    waiting_partner = State()


class PaymentFlow(StatesGroup):
    """States for payment flow."""
    waiting_proof = State()
    

# ─────────────────────────────────────────────────────────────────────────────
# Deal Creation Flow
# ─────────────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "create_deal")
async def start_deal_creation(callback: CallbackQuery, state: FSMContext, _: Callable):
    """Start deal creation — ask for role."""
    await state.set_state(DealCreation.selecting_role)
    
    await callback.message.edit_text(
        _("select_role_title"),
        reply_markup=get_deal_role_selection(_),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("role:"), DealCreation.selecting_role)
async def select_role(callback: CallbackQuery, state: FSMContext, _: Callable):
    """Handle role selection."""
    role = callback.data.split(":")[1]
    
    await state.update_data(user_role=role)
    await state.set_state(DealCreation.entering_description)
    
    role_text = _("role_seller") if role == "seller" else _("role_buyer")
    
    await callback.message.edit_text(
        _("describe_deal_title", role=role_text),
        reply_markup=get_cancel_keyboard(_),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(DealCreation.entering_description)
async def process_deal_description(
    message: Message, 
    state: FSMContext, 
    ai_service: AIService,
    db: Database,
    _: Callable
):
    """Process user's deal description with AI."""
    user_text = message.text
    
    if not user_text or len(user_text) < 10:
        await message.answer(
            _("describe_deal_title"),
            reply_markup=get_cancel_keyboard(_)
        )
        return
    
    processing_msg = await message.answer(_("analyzing_ai"), parse_mode="HTML")
    
    try:
        parsed: ParsedDeal = await ai_service.parse_deal(user_text)
        
        data = await state.get_data()
        user_role = data.get("user_role", "seller")
        
        if user_role == "seller":
            parsed.seller_username = f"@{message.from_user.username}" if message.from_user.username else None
        else:
            parsed.buyer_username = f"@{message.from_user.username}" if message.from_user.username else None
        
        if not parsed.is_valid:
            await processing_msg.edit_text(
                f"⚠️ <b>Could not parse deal completely</b>\n\n"
                f"Missing required fields: {', '.join(parsed.missing_fields)}\n\n"
                f"Please try again with a clearer description including:\n"
                f"• Amount and currency\n"
                f"• What's being traded\n"
                f"• The other party's @username",
                parse_mode="HTML",
                reply_markup=get_cancel_keyboard(_)
            )
            return
        
        deal_id = await db.create_deal(
            creator_id=message.from_user.id,
            amount=parsed.amount,
            currency=parsed.currency,
            item_description=parsed.item_description,
            seller_username=parsed.seller_username,
            buyer_username=parsed.buyer_username,
            deadline_hours=parsed.deadline_hours,
        )
        
        if user_role == "seller":
            await db.set_deal_seller(
                deal_id, 
                message.from_user.id, 
                message.from_user.username
            )
        else:
            await db.set_deal_buyer(
                deal_id, 
                message.from_user.id, 
                message.from_user.username
            )
        
        await state.update_data(deal_id=deal_id, parsed_deal=parsed.raw_json)
        await state.set_state(DealCreation.confirming_deal)
        
        await processing_msg.edit_text(
            f"{_('deal_card_title', deal_id=deal_id)}\n\n"
            f"{parsed.to_display_card()}\n\n"
            f"{_('deal_review_prompt')}",
            reply_markup=get_deal_confirmation(deal_id, _),
            parse_mode="HTML"
        )
        
    except ValueError as e:
        await processing_msg.edit_text(
            f"❌ <b>AI Parsing Failed</b>\n\n{str(e)}\n\n",
            parse_mode="HTML",
            reply_markup=get_cancel_keyboard(_)
        )
    except Exception as e:
        logger.error(f"Deal creation error: {e}")
        await processing_msg.edit_text(
            f"❌ <b>Error</b>\n\n{str(e)[:100]}",
            parse_mode="HTML",
            reply_markup=get_main_menu(_)
        )


@router.callback_query(F.data.startswith("deal:") & F.data.endswith(":confirm_send"))
async def confirm_and_send_deal(callback: CallbackQuery, state: FSMContext, db: Database, bot: Bot, _: Callable):
    """Confirm deal and send invitation to partner."""
    # [AUDIT FIX] Safe parsing
    deal_id = safe_parse_deal_id(callback.data)
    if not deal_id:
        await callback.answer("❌ Invalid request", show_alert=True)
        return
    
    deal = await db.get_deal(deal_id)
    
    if not deal:
        await callback.answer("Deal not found!", show_alert=True)
        return
    
    # [AUDIT FIX] Access control
    if not can_access_deal(callback.from_user.id, deal):
        await callback.answer("⛔ Access denied!", show_alert=True)
        logger.warning(f"[SECURITY] User {callback.from_user.id} tried to confirm deal #{deal_id} without permission")
        return
    
    data = await state.get_data()
    user_role = data.get("user_role", "seller")
    
    partner_username = deal["buyer_username"] if user_role == "seller" else deal["seller_username"]
    
    if not partner_username:
        await callback.message.edit_text(
            f"⚠️ <b>Partner Username Missing</b>\n\n"
            f"We couldn't detect the other party's @username from your description.\n\n"
            f"Please share this deal link with them:\n\n"
            f"<code>/join_deal {deal_id}</code>",
            parse_mode="HTML",
            reply_markup=get_back_to_menu(_)
        )
        await callback.answer()
        return
    
    partner = await db.find_user_by_username(partner_username.lstrip("@"))
    
    if partner:
        try:
            p_lang = partner.get("language", "ru")
            from locales.translations import get_text
            def _p(key, **kwargs): return get_text(key, p_lang, **kwargs)
            
            partner_role = _p("role_buyer") if user_role == "seller" else _p("role_seller")
            
            notification = _p(
                "new_deal_invitation",
                creator=callback.from_user.username or "Someone",
                item=deal['item_description'],
                amount=deal['amount'],
                currency=deal['currency'],
                role=partner_role,
                deadline=deal['deadline_hours'] or '?'
            )
            
            await bot.send_message(
                partner["user_id"],
                notification,
                reply_markup=get_partner_confirmation(deal_id, _p),
                parse_mode="HTML"
            )
            
            await db.update_deal_status(
                deal_id, 
                DealStatus.PENDING_BUYER if user_role == "seller" else DealStatus.PENDING_SELLER
            )
            
            await callback.message.edit_text(
                _("invitation_sent", deal_id=deal_id, partner=partner_username),
                parse_mode="HTML",
                reply_markup=get_back_to_menu(_)
            )
            
        except Exception as e:
            logger.error(f"Failed to notify partner: {e}")
            await callback.message.edit_text(
                _("partner_not_registered", partner=partner_username, bot_username=(await bot.get_me()).username, deal_id=deal_id),
                parse_mode="HTML",
                reply_markup=get_back_to_menu(_)
            )
    else:
        await callback.message.edit_text(
            _("partner_not_registered", partner=partner_username, bot_username=(await bot.get_me()).username, deal_id=deal_id),
            parse_mode="HTML",
            reply_markup=get_back_to_menu(_)
        )
    
    await state.clear()
    await callback.answer()


# ─────────────────────────────────────────────────────────────────────────────
# Partner Confirmation
# ─────────────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("confirm:") & F.data.endswith(":accept"))
async def partner_accepts_deal(callback: CallbackQuery, db: Database, bot: Bot, _: Callable):
    """Partner accepts the deal terms."""
    # [AUDIT FIX] Safe parsing
    deal_id = safe_parse_deal_id(callback.data)
    if not deal_id:
        await callback.answer("❌ Invalid request", show_alert=True)
        return
    
    deal = await db.get_deal(deal_id)
    
    if not deal:
        await callback.answer("Deal not found!", show_alert=True)
        return
    
    user_id = callback.from_user.id
    username = callback.from_user.username
    
    if deal["seller_id"] is None:
        await db.set_deal_seller(deal_id, user_id, username)
        role = _("role_seller")
        is_buyer = False
    elif deal["buyer_id"] is None:
        await db.set_deal_buyer(deal_id, user_id, username)
        role = _("role_buyer")
        is_buyer = True
    else:
        await callback.answer("Already has both parties!", show_alert=True)
        return
    
    await db.update_deal_status(deal_id, DealStatus.CONFIRMED)
    
    next_step = _("next_step_pay") if is_buyer else _("next_step_wait")
    
    await callback.message.edit_text(
        _("deal_accepted_self", deal_id=deal_id, role=role, next_step=next_step, item=deal['item_description'], amount=deal['amount'], currency=deal['currency']),
        parse_mode="HTML",
        reply_markup=get_back_to_menu(_)
    )
    
    creator = await db.get_user(deal["creator_id"])
    c_lang = creator.get("language", "ru") if creator else "ru"
    from locales.translations import get_text
    def _c(key, **kwargs): return get_text(key, c_lang, **kwargs)
    
    try:
        if is_buyer:
            await callback.message.answer(
                _("payment_instructions", amount=deal['amount'], currency=deal['currency'], wallet=config.wallet_address, deal_id=deal_id),
                reply_markup=get_payment_keyboard(deal_id, _),
                parse_mode="HTML"
            )
            await db.update_deal_status(deal_id, DealStatus.PAYMENT_PENDING)

            msg = f"🎉 <b>Deal #{deal_id} Confirmed!</b>\n\nBuyer @{username} joined. Waiting for payment."
            await bot.send_message(deal["creator_id"], msg, parse_mode="HTML")
        else:
            await bot.send_message(
                deal["creator_id"],
                _c("payment_instructions", amount=deal['amount'], currency=deal['currency'], wallet=config.wallet_address, deal_id=deal_id),
                reply_markup=get_payment_keyboard(deal_id, _c),
                parse_mode="HTML"
            )
            await db.update_deal_status(deal_id, DealStatus.PAYMENT_PENDING)

            msg = f"🎉 <b>Deal #{deal_id} Confirmed!</b>\n\nSeller @{username} joined. Please pay."
            await bot.send_message(deal["creator_id"], msg, parse_mode="HTML")
            
    except Exception as e:
        # [AUDIT FIX] Proper error logging instead of bare except
        logger.error(f"Failed to notify creator: {e}")
    
    await callback.answer("Accepted! ✅")


@router.callback_query(F.data.startswith("confirm:") & F.data.endswith(":decline"))
async def partner_declines_deal(callback: CallbackQuery, db: Database, bot: Bot, _: Callable):
    """Partner declines the deal."""
    # [AUDIT FIX] Safe parsing
    deal_id = safe_parse_deal_id(callback.data)
    if not deal_id:
        await callback.answer("❌ Invalid request", show_alert=True)
        return
    
    deal = await db.get_deal(deal_id)
    
    if not deal:
        await callback.answer("Deal not found!", show_alert=True)
        return
    
    await db.update_deal_status(deal_id, DealStatus.CANCELLED)
    
    await callback.message.edit_text(
        f"❌ <b>Deal #{deal_id} Declined</b>\n\n"
        f"You have declined this deal.\n"
        f"The other party will be notified.",
        parse_mode="HTML",
        reply_markup=get_back_to_menu(_)
    )
    
    try:
        await bot.send_message(
            deal["creator_id"],
            f"❌ <b>Deal #{deal_id} Declined</b>\n\n"
            f"@{callback.from_user.username} has declined your deal invitation.\n\n"
            f"You can create a new deal with /menu.",
            parse_mode="HTML"
        )
    except Exception as e:
        # [AUDIT FIX] Proper error logging
        logger.error(f"Failed to notify creator of decline: {e}")
    
    await callback.answer("Deal declined")


# ─────────────────────────────────────────────────────────────────────────────
# Payment Flow
# ─────────────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("deal:") & F.data.endswith(":paid"))
async def buyer_claims_paid(callback: CallbackQuery, state: FSMContext, db: Database, _: Callable):
    """Buyer claims they've paid — ask for proof."""
    # [AUDIT FIX] Safe parsing
    deal_id = safe_parse_deal_id(callback.data)
    if not deal_id:
        await callback.answer("❌ Invalid request", show_alert=True)
        return
    
    deal = await db.get_deal(deal_id)
    
    # [AUDIT FIX] Verify this is the buyer
    if not deal or callback.from_user.id != deal.get("buyer_id"):
        await callback.answer("⛔ Only buyer can submit payment!", show_alert=True)
        logger.warning(f"[SECURITY] User {callback.from_user.id} tried to claim payment for deal #{deal_id}")
        return
    
    await state.update_data(paying_deal_id=deal_id)
    await state.set_state(PaymentFlow.waiting_proof)
    
    await callback.message.edit_text(
        _("send_proof_title"),
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(_)
    )
    await callback.answer()


@router.message(PaymentFlow.waiting_proof)
async def receive_payment_proof(message: Message, state: FSMContext, db: Database, bot: Bot, _: Callable):
    """Receive and forward payment proof to admin."""
    data = await state.get_data()
    deal_id = data.get("paying_deal_id")
    
    if not deal_id:
        await state.clear()
        await message.answer(_("session_expired") if callable(_) else "Session expired. Please start again.", reply_markup=get_main_menu(_))
        return
    
    deal = await db.get_deal(deal_id)
    if not deal:
        await state.clear()
        await message.answer("Deal not found.", reply_markup=get_main_menu(_))
        return
    
    proof = None
    proof_type = "text"
    
    if message.photo:
        proof = message.photo[-1].file_id
        proof_type = "photo"
    elif message.document:
        proof = message.document.file_id
        proof_type = "document"
    elif message.text:
        proof = message.text
        proof_type = "text"
    else:
        await message.answer(
            "⚠️ Please send a screenshot, document, or TXID text.",
            reply_markup=get_cancel_keyboard(_)
        )
        return
    
    await db.set_payment_proof(deal_id, proof, tx_id=proof if proof_type == "text" else None)
    
    admin_notification = (
        f"💳 <b>Payment Verification Required</b>\n\n"
        f"<b>Deal #{deal_id}</b>\n"
        f"📦 Item: {deal['item_description']}\n"
        f"💰 Amount: {deal['amount']} {deal['currency']}\n"
        f"👤 Seller: @{deal['seller_username']}\n"
        f"👤 Buyer: @{message.from_user.username}\n\n"
        f"<b>Proof type:</b> {proof_type.upper()}\n"
    )
    
    if proof_type == "text":
        admin_notification += f"<b>TXID:</b> <code>{proof}</code>"
    
    try:
        from keyboards.inline import get_admin_payment_verification
        
        await bot.send_message(
            config.admin_id,
            admin_notification,
            parse_mode="HTML"
        )
        
        if proof_type == "photo":
            await bot.send_photo(
                config.admin_id,
                proof,
                caption=f"Payment proof for Deal #{deal_id}",
                reply_markup=get_admin_payment_verification(deal_id)
            )
        elif proof_type == "document":
            await bot.send_document(
                config.admin_id,
                proof,
                caption=f"Payment proof for Deal #{deal_id}",
                reply_markup=get_admin_payment_verification(deal_id)
            )
        else:
            await bot.send_message(
                config.admin_id,
                f"Verify this payment:",
                reply_markup=get_admin_payment_verification(deal_id)
            )
        
        await message.answer(
            _("proof_submitted", deal_id=deal_id),
            parse_mode="HTML",
            reply_markup=get_back_to_menu(_)
        )
        
    except Exception as e:
        # [AUDIT FIX] Proper error logging
        logger.error(f"Failed to forward proof to admin: {e}")
        await message.answer(
            f"⚠️ <b>Error</b>\n\n"
            f"Failed to send proof to admin. Please try again or contact support.",
            parse_mode="HTML",
            reply_markup=get_main_menu(_)
        )
    
    await state.clear()


# ─────────────────────────────────────────────────────────────────────────────
# Buyer Confirms Receipt
# ─────────────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("deal:") & F.data.endswith(":received"))
async def buyer_confirms_receipt(callback: CallbackQuery, db: Database, bot: Bot, _: Callable):
    """Buyer confirms item received — trigger fund release."""
    # [AUDIT FIX] Safe parsing
    deal_id = safe_parse_deal_id(callback.data)
    if not deal_id:
        await callback.answer("❌ Invalid request", show_alert=True)
        return
    
    deal = await db.get_deal(deal_id)
    
    if not deal:
        await callback.answer("Deal not found!", show_alert=True)
        return
    
    # [AUDIT FIX] Verify this is the buyer
    if callback.from_user.id != deal["buyer_id"]:
        await callback.answer("⛔ Only buyer can confirm receipt!", show_alert=True)
        logger.warning(f"[SECURITY] User {callback.from_user.id} tried to confirm receipt for deal #{deal_id}")
        return
    
    await db.update_deal_status(deal_id, DealStatus.COMPLETED)
    await db.complete_deal(deal_id)
    
    await callback.message.edit_text(
        _("deal_completed_buyer", deal_id=deal_id),
        parse_mode="HTML",
        reply_markup=get_back_to_menu(_)
    )
    
    try:
        await bot.send_message(
            deal["seller_id"],
            f"🎉 <b>Deal #{deal_id} Completed!</b>\n\nBuyer confirmed receipt. Funds will be released.",
            parse_mode="HTML"
        )
    except Exception as e:
        # [AUDIT FIX] Proper error logging instead of bare except: pass
        logger.warning(f"Failed to notify seller of completion: {e}")
    
    await callback.answer("Completed!")


@router.callback_query(F.data == "my_deals")
async def show_my_deals(callback: CallbackQuery, db: Database, _: Callable):
    """Show user's deals."""
    deals = await db.get_user_deals(callback.from_user.id)
    
    if not deals:
        await callback.message.edit_text(
            _("main_menu_title"),
            reply_markup=get_main_menu(_),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            f"📋 <b>Your Deals</b>",
            reply_markup=get_deal_list_keyboard(deals, _),
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data.startswith("deal:") & F.data.endswith(":view"))
async def view_deal_details(callback: CallbackQuery, db: Database, _: Callable):
    """View details of a specific deal."""
    # [AUDIT FIX] Safe parsing
    deal_id = safe_parse_deal_id(callback.data)
    if not deal_id:
        await callback.answer("❌ Invalid request", show_alert=True)
        return
    
    deal = await db.get_deal(deal_id)
    
    # [AUDIT FIX] Access control - only participants can view
    if not can_access_deal(callback.from_user.id, deal):
        await callback.answer("⛔ Access denied!", show_alert=True)
        logger.warning(f"[SECURITY] User {callback.from_user.id} tried to view deal #{deal_id} without permission")
        return
    
    if not deal:
        await callback.answer("Deal not found!", show_alert=True)
        return
    
    details = (
        f"🔐 <b>Deal #{deal_id}</b>\n\n"
        f"<b>Status:</b> {deal['status']}\n"
        f"📦 <b>Item:</b> {deal['item_description']}\n"
        f"💰 <b>Amount:</b> {deal['amount']} {deal['currency']}\n"
    )
    
    await callback.message.edit_text(
        details,
        reply_markup=get_back_to_menu(_),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("deal:") & F.data.endswith(":cancel"))
async def cancel_deal(callback: CallbackQuery, db: Database, state: FSMContext, _: Callable):
    """Cancel a deal."""
    # [AUDIT FIX] Safe parsing of deal_id
    deal_id = safe_parse_deal_id(callback.data)
    if not deal_id:
        await callback.answer("❌ Invalid request", show_alert=True)
        return
    
    deal = await db.get_deal(deal_id)
    
    # [AUDIT FIX] Access control - only participants can cancel
    if not can_access_deal(callback.from_user.id, deal):
        await callback.answer("⛔ Access denied!", show_alert=True)
        logger.warning(f"[SECURITY] User {callback.from_user.id} tried to cancel deal #{deal_id} without permission")
        return
    
    await db.update_deal_status(deal_id, DealStatus.CANCELLED)
    await state.clear()
    
    await callback.message.edit_text(
        f"❌ Deal #{deal_id} Cancelled.",
        parse_mode="HTML",
        reply_markup=get_back_to_menu(_)
    )
    await callback.answer()
