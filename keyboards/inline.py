"""
Inline keyboard builders for Big Stepa Safe Escrow Bot.
All user interactions happen through inline keyboards.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ─────────────────────────────────────────────────────────────────────────────
# Callback Data Prefixes (for parsing in handlers)
# ─────────────────────────────────────────────────────────────────────────────

class CallbackPrefix:
    """Callback data prefixes for routing."""
    CREATE_DEAL = "create_deal"
    MY_DEALS = "my_deals"
    DEAL_ACTION = "deal"  # deal:{deal_id}:{action}
    ADMIN = "admin"       # admin:{deal_id}:{action}
    CONFIRM = "confirm"   # confirm:{deal_id}:{party}
    CANCEL = "cancel"


# ─────────────────────────────────────────────────────────────────────────────
# Main Menu
# ─────────────────────────────────────────────────────────────────────────────

def get_main_menu(_) -> InlineKeyboardMarkup:
    """Main bot menu keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("btn_create_deal"),
            callback_data=CallbackPrefix.CREATE_DEAL
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("btn_my_deals"),
            callback_data=CallbackPrefix.MY_DEALS
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("btn_how_it_works"),
            callback_data="how_it_works"
        ),
        InlineKeyboardButton(
            text=_("btn_settings"),
            callback_data="settings"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("btn_support"),
            callback_data="support"
        )
    )
    
    return builder.as_markup()


# ─────────────────────────────────────────────────────────────────────────────
# Deal Flow Keyboards
# ─────────────────────────────────────────────────────────────────────────────

def get_deal_role_selection(_) -> InlineKeyboardMarkup:
    """Ask user their role in the deal."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=_("btn_seller"), callback_data="role:seller"),
        InlineKeyboardButton(text=_("btn_buyer"), callback_data="role:buyer")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_cancel"), callback_data=CallbackPrefix.CANCEL)
    )
    
    return builder.as_markup()


def get_deal_confirmation(deal_id: int, _) -> InlineKeyboardMarkup:
    """Confirm or cancel parsed deal."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("btn_confirm_send"),
            callback_data=f"deal:{deal_id}:confirm_send"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("btn_edit_description"),
            callback_data=f"deal:{deal_id}:edit"
        ),
        InlineKeyboardButton(
            text=_("btn_cancel"),
            callback_data=f"deal:{deal_id}:cancel"
        )
    )
    
    return builder.as_markup()


def get_partner_confirmation(deal_id: int, _) -> InlineKeyboardMarkup:
    """Partner (second party) confirmation keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("btn_accept_terms"),
            callback_data=f"confirm:{deal_id}:accept"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("btn_decline"),
            callback_data=f"confirm:{deal_id}:decline"
        ),
        InlineKeyboardButton(
            text=_("btn_negotiate"),
            callback_data=f"confirm:{deal_id}:negotiate"
        )
    )
    
    return builder.as_markup()


def get_payment_keyboard(deal_id: int, _) -> InlineKeyboardMarkup:
    """Buyer payment confirmation keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("btn_i_paid"),
            callback_data=f"deal:{deal_id}:paid"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("btn_cancel"),
            callback_data=f"deal:{deal_id}:cancel"
        )
    )
    
    return builder.as_markup()


def get_delivery_confirmation(deal_id: int, _) -> InlineKeyboardMarkup:
    """Buyer confirms item received."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("btn_item_received"),
            callback_data=f"deal:{deal_id}:received"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("btn_dispute"),
            callback_data=f"deal:{deal_id}:dispute"
        )
    )
    
    return builder.as_markup()


# ─────────────────────────────────────────────────────────────────────────────
# Settings Keyboards
# ─────────────────────────────────────────────────────────────────────────────

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Settings menu for language selection."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🇷🇺 Russian", callback_data="set_lang:ru"),
        InlineKeyboardButton(text="🇺🇸 English", callback_data="set_lang:en")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")
    )
    
    return builder.as_markup()


# ─────────────────────────────────────────────────────────────────────────────
# Admin Panel Keyboards
# ─────────────────────────────────────────────────────────────────────────────

def get_admin_payment_verification(deal_id: int) -> InlineKeyboardMarkup:
    """Admin buttons to verify or reject payment."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="✅ Money Received",
            callback_data=f"admin:{deal_id}:verify"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="❌ Fake/Cancel",
            callback_data=f"admin:{deal_id}:reject"
        ),
        InlineKeyboardButton(
            text="🔍 Investigate",
            callback_data=f"admin:{deal_id}:investigate"
        )
    )
    
    return builder.as_markup()


def get_admin_release_confirmation(deal_id: int) -> InlineKeyboardMarkup:
    """Admin confirms fund release to seller."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="💰 Release Funds to Seller",
            callback_data=f"admin:{deal_id}:release"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⏸️ Hold - Need Review",
            callback_data=f"admin:{deal_id}:hold"
        )
    )
    
    return builder.as_markup()


def get_admin_main_panel() -> InlineKeyboardMarkup:
    """Admin main panel menu."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📊 Stats", callback_data="admin:stats"),
        InlineKeyboardButton(text="⏳ Pending Payments", callback_data="admin:pending")
    )
    builder.row(
        InlineKeyboardButton(text="🔍 Search Deal", callback_data="admin:search"),
        InlineKeyboardButton(text="⚠️ Active Disputes", callback_data="admin:disputes")
    )
    
    return builder.as_markup()


# ─────────────────────────────────────────────────────────────────────────────
# Utility Keyboards
# ─────────────────────────────────────────────────────────────────────────────

def get_back_to_menu(_) -> InlineKeyboardMarkup:
    """Simple back to main menu button."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=_("btn_main_menu"), callback_data="main_menu")
    )
    return builder.as_markup()


def get_cancel_keyboard(_) -> InlineKeyboardMarkup:
    """Cancel current operation."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=_("btn_cancel"), callback_data=CallbackPrefix.CANCEL)
    )
    return builder.as_markup()


def get_deal_list_keyboard(deals: list[dict], _) -> InlineKeyboardMarkup:
    """Generate keyboard from list of deals."""
    builder = InlineKeyboardBuilder()
    
    for deal in deals[:10]:
        status_emoji = {
            "draft": "📝",
            "pending_buyer": "⏳",
            "pending_seller": "⏳",
            "confirmed": "✅",
            "payment_pending": "💳",
            "payment_sent": "📤",
            "payment_verified": "💰",
            "in_progress": "🔨",
            "delivered": "📦",
            "completed": "🎉",
            "disputed": "⚠️",
            "cancelled": "❌",
        }.get(deal["status"], "❓")
        
        text = f"{status_emoji} #{deal['deal_id']} - {deal['amount']} {deal['currency']}"
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f"deal:{deal['deal_id']}:view"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text=_("btn_main_menu"), callback_data="main_menu")
    )
    
    return builder.as_markup()
