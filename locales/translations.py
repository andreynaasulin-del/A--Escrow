"""
Translation strings for Big Stepa Safe Escrow Bot.
Supports Russian (default) and English.
"""

MESSAGES = {
    "welcome": {
        "ru": (
            "🛡️ <b>Big Stepa Safe</b> — Безопасный Escrow сервис\n\n"
            "Добро пожаловать! Я помогу провести безопасную сделку с незнакомым человеком в интернете.\n\n"
            "<b>Как это работает:</b>\n"
            "1️⃣ <b>Создание сделки</b> — Опишите условия текстом\n"
            "2️⃣ <b>AI Парсинг</b> — Я сам вытащу детали сделки\n"
            "3️⃣ <b>Подтверждение</b> — Оба участника принимают условия\n"
            "4️⃣ <b>Оплата</b> — Покупатель вносит средства в бот\n"
            "5️⃣ <b>Проверка</b> — Администратор вручную подтверждает оплату\n"
            "6️⃣ <b>Доставка</b> — Продавец передает товар/услугу\n"
            "7️⃣ <b>Выплата</b> — Продавец получает свои деньги\n\n"
            "🔐 <b>Ваша безопасность гарантирована</b> — никто не потеряет деньги!\n\n"
            "Выберите действие ниже:"
        ),
        "en": (
            "🛡️ <b>Big Stepa Safe</b> — Secure Escrow Service\n\n"
            "Welcome! I help you make safe deals with strangers online.\n\n"
            "<b>How it works:</b>\n"
            "1️⃣ <b>Create Deal</b> — Describe your trade in text\n"
            "2️⃣ <b>AI Parsing</b> — I extract deal details automatically\n"
            "3️⃣ <b>Confirmation</b> — Both parties accept terms\n"
            "4️⃣ <b>Payment</b> — Buyer sends funds to the bot\n"
            "5️⃣ <b>Verification</b> — Admin manually confirms payment\n"
            "6️⃣ <b>Execution</b> — Seller delivers product/service\n"
            "7️⃣ <b>Release</b> — Seller gets paid\n\n"
            "🔐 <b>Your safety is guaranteed</b> — no one loses money!\n\n"
            "Choose an action below:"
        )
    },
    "main_menu_title": {
        "ru": "🏠 <b>Главное Меню</b>\n\nВыберите действие:",
        "en": "🏠 <b>Main Menu</b>\n\nChoose an action:"
    },
    "btn_create_deal": {
        "ru": "🔐 Создать сделку",
        "en": "🔐 Create Deal"
    },
    "btn_my_deals": {
        "ru": "📋 Мои сделки",
        "en": "📋 My Deals"
    },
    "btn_how_it_works": {
        "ru": "ℹ️ Как это работает",
        "en": "ℹ️ How It Works"
    },
    "btn_support": {
        "ru": "📞 Поддержка",
        "en": "📞 Support"
    },
    "btn_settings": {
        "ru": "⚙️ Настройки",
        "en": "⚙️ Settings"
    },
    "btn_back": {
        "ru": "🔙 Назад",
        "en": "🔙 Back"
    },
    "btn_cancel": {
        "ru": "❌ Отмена",
        "en": "❌ Cancel"
    },
    "btn_main_menu": {
        "ru": "🔙 Главное меню",
        "en": "🔙 Main Menu"
    },
    "select_role_title": {
        "ru": "🔐 <b>Создание сделки</b>\n\nДля начала, кто вы в этой сделке?",
        "en": "🔐 <b>Create New Deal</b>\n\nFirst, what's your role in this deal?"
    },
    "btn_seller": {
        "ru": "🏪 Я Продавец",
        "en": "🏪 I'm the Seller"
    },
    "btn_buyer": {
        "ru": "🛒 Я Покупатель",
        "en": "🛒 I'm the Buyer"
    },
    "describe_deal_title": {
        "ru": (
            "📝 <b>Опишите вашу сделку</b>\n\n"
            "Вы выбрали: <b>{role}</b>\n\n"
            "Опишите условия простым текстом. Укажите:\n"
            "• Юзернейм второго участника через @\n"
            "• Что продается\n"
            "• Цена и валюта\n"
            "• Срок (опционально)\n\n"
            "<i>Пример: \"Продаю скрипт @username за 150 USDT, срок 24 часа\"</i>\n\n"
            "Отправьте описание:"
        ),
        "en": (
            "📝 <b>Describe Your Deal</b>\n\n"
            "You selected: <b>{role}</b>\n\n"
            "Now describe your deal in natural language. Include:\n"
            "• The other party's @username\n"
            "• What's being sold\n"
            "• Price and currency\n"
            "• Deadline (optional)\n\n"
            "<i>Example: \"Selling my parser script to @john_doe for 150 USDT, 24 hours to deliver\"</i>\n\n"
            "Send your description:"
        )
    },
    "role_seller": {"ru": "Продавец", "en": "Seller"},
    "role_buyer": {"ru": "Покупатель", "en": "Buyer"},
    "analyzing_ai": {
        "ru": "🤖 <i>Анализирую вашу сделку через AI...</i>",
        "en": "🤖 <i>Analyzing your deal with AI...</i>"
    },
    "deal_card_title": {
        "ru": "✅ <b>Сделка #{deal_id} создана</b>",
        "en": "✅ <b>Deal #{deal_id} Created</b>"
    },
    "deal_review_prompt": {
        "ru": "<b>Проверьте детали выше.</b>\nЕсли всё верно, подтвердите, чтобы отправить приглашение второму участнику.",
        "en": "<b>Review the details above.</b>\nIf correct, confirm to send invitation to the other party."
    },
    "btn_confirm_send": {
        "ru": "✅ Подтвердить и отправить",
        "en": "✅ Confirm & Send to Partner"
    },
    "btn_edit_description": {
        "ru": "📝 Изменить описание",
        "en": "📝 Edit Description"
    },
    "invitation_sent": {
        "ru": "✅ <b>Приглашение отправлено!</b>\n\nПриглашение по сделке #{deal_id} отправлено пользователю {partner}.\n\nЖдем подтверждения...\nЯ сообщу вам, когда он ответит.",
        "en": "✅ <b>Invitation Sent!</b>\n\nDeal #{deal_id} invitation sent to {partner}.\n\nWaiting for their confirmation...\nYou'll be notified when they respond."
    },
    "partner_not_registered": {
        "ru": (
            "⚠️ <b>Партнер не зарегистрирован</b>\n\n"
            "{partner} еще не пользовался ботом.\n\n"
            "Пожалуйста, попросите его:\n"
            "1. Запустить @{bot_username}\n"
            "2. Нажать /start\n\n"
            "После этого создайте сделку заново или используйте:\n"
            "<code>/join_deal {deal_id}</code>"
        ),
        "en": (
            "⚠️ <b>Partner Not Registered</b>\n\n"
            "{partner} hasn't used this bot yet.\n\n"
            "Please ask them to:\n"
            "1. Start @{bot_username}\n"
            "2. Send /start\n\n"
            "Once they're registered, recreate this deal or use:\n"
            "<code>/join_deal {deal_id}</code>"
        )
    },
    "new_deal_invitation": {
        "ru": (
            "🔔 <b>Новое приглашение к сделке!</b>\n\n"
            "@{creator} пригласил вас в сделку:\n\n"
            "📦 <b>Товар:</b> {item}\n"
            "💰 <b>Сумма:</b> {amount} {currency}\n"
            "👤 <b>Ваша роль:</b> {role}\n"
            "⏰ <b>Срок:</b> {deadline} ч.\n\n"
            "Вы принимаете эти условия?"
        ),
        "en": (
            "🔔 <b>New Deal Invitation!</b>\n\n"
            "@{creator} invited you to a deal:\n\n"
            "📦 <b>Item:</b> {item}\n"
            "💰 <b>Amount:</b> {amount} {currency}\n"
            "👤 <b>Your role:</b> {role}\n"
            "⏰ <b>Deadline:</b> {deadline} hours\n\n"
            "Do you accept these terms?"
        )
    },
    "btn_accept_terms": {
        "ru": "✅ Принять условия",
        "en": "✅ Accept Terms"
    },
    "btn_decline": {
        "ru": "❌ Отклонить",
        "en": "❌ Decline"
    },
    "btn_negotiate": {
        "ru": "💬 Обсудить",
        "en": "💬 Negotiate"
    },
    "deal_accepted_self": {
        "ru": (
            "✅ <b>Сделка #{deal_id} принята!</b>\n\n"
            "Ваша роль: {role}\n\n"
            "<b>Следующий шаг:</b>\n"
            "{next_step}\n\n"
            "📦 {item}\n"
            "💰 {amount} {currency}"
        ),
        "en": (
            "✅ <b>Deal #{deal_id} Accepted!</b>\n\n"
            "You joined as: {role}\n\n"
            "<b>Next step:</b>\n"
            "{next_step}\n\n"
            "📦 {item}\n"
            "💰 {amount} {currency}"
        )
    },
    "next_step_pay": {
        "ru": "Вы получите инструкции по оплате в ближайшее время.",
        "en": "You will receive payment instructions shortly."
    },
    "next_step_wait": {
        "ru": "Ожидайте, пока покупатель внесет оплату.",
        "en": "Wait for buyer to pay."
    },
    "payment_instructions": {
        "ru": (
            "💳 <b>Инструкции по оплате</b>\n\n"
            "Пожалуйста, отправьте <b>{amount} {currency}</b> на адрес:\n\n"
            "<code>{wallet}</code>\n\n"
            "⚠️ <b>ВАЖНО:</b> В комментарии к платежу укажите:\n"
            "<code>DEAL-{deal_id}</code>\n\n"
            "Это поможет нам быстрее идентифицировать ваш платеж.\n\n"
            "После отправки нажмите кнопку ниже и предоставьте подтверждение (скриншот или TXID)."
        ),
        "en": (
            "💳 <b>Payment Instructions</b>\n\n"
            "Please send <b>{amount} {currency}</b> to:\n\n"
            "<code>{wallet}</code>\n\n"
            "⚠️ <b>IMPORTANT:</b> Include this MEMO/comment:\n"
            "<code>DEAL-{deal_id}</code>\n\n"
            "This helps us identify your payment faster.\n\n"
            "After sending, click the button below and provide proof (screenshot or TXID)."
        )
    },
    "btn_i_paid": {
        "ru": "💸 Я оплатил - отправить подтверждение",
        "en": "💸 I've Paid - Send Proof"
    },
    "send_proof_title": {
        "ru": (
            "📤 <b>Отправьте подтверждение оплаты</b>\n\n"
            "Пожалуйста, пришлите:\n"
            "• Скриншот транзакции, ИЛИ\n"
            "• ID транзакции (TXID)\n\n"
            "Это сообщение будет переслано администратору для проверки."
        ),
        "en": (
            "📤 <b>Send Payment Proof</b>\n\n"
            "Please send:\n"
            "• Screenshot of the transaction, OR\n"
            "• Transaction ID (TXID)\n\n"
            "This will be forwarded to our admin for verification."
        )
    },
    "proof_submitted": {
        "ru": (
            "✅ <b>Подтверждение отправлено!</b>\n\n"
            "Ваше подтверждение оплаты по сделке #{deal_id} отправлено администратору.\n\n"
            "⏳ Ожидайте проверки (обычно в течение 1 часа).\n"
            "Я сообщу вам, когда оплата будет подтверждена."
        ),
        "en": (
            "✅ <b>Proof Submitted!</b>\n\n"
            "Your payment proof for Deal #{deal_id} has been sent to admin.\n\n"
            "⏳ Please wait for verification (usually within 1 hour).\n"
            "You'll be notified once confirmed."
        )
    },
    "funds_secured_seller": {
        "ru": (
            "💰 <b>Средства получены!</b>\n\n"
            "Оплата по сделке #{deal_id} подтверждена!\n\n"
            "📦 <b>Товар:</b> {item}\n"
            "💵 <b>Сумма:</b> {amount} {currency}\n"
            "⏰ <b>Срок:</b> {deadline} ч.\n\n"
            "Теперь вы можете приступать к работе.\n"
            "Сообщите покупателю, когда всё будет готово!"
        ),
        "en": (
            "💰 <b>Funds Secured!</b>\n\n"
            "Deal #{deal_id} payment has been verified!\n\n"
            "📦 <b>Item:</b> {item}\n"
            "💵 <b>Amount:</b> {amount} {currency}\n"
            "⏰ <b>Deadline:</b> {deadline} hours\n\n"
            "You can now start working on the delivery.\n"
            "Notify buyer when ready!"
        )
    },
    "payment_confirmed_buyer": {
        "ru": (
            "✅ <b>Оплата подтверждена!</b>\n\n"
            "Ваш платеж по сделке #{deal_id} успешно проверен!\n\n"
            "Продавец получил уведомление и приступает к работе.\n"
            "Вы получите уведомление о доставке в ближайшее время."
        ),
        "en": (
            "✅ <b>Payment Confirmed!</b>\n\n"
            "Your payment for Deal #{deal_id} has been verified!\n\n"
            "The seller has been notified to start working.\n"
            "You'll receive delivery notification soon."
        )
    },
    "btn_item_received": {
        "ru": "✅ Товар получен - выплатить средства",
        "en": "✅ Item Received - Release Funds"
    },
    "btn_dispute": {
        "ru": "⚠️ Проблема - открыть спор",
        "en": "⚠️ Problem - Open Dispute"
    },
    "deal_completed_buyer": {
        "ru": (
            "🎉 <b>Сделка #{deal_id} завершена!</b>\n\n"
            "Вы подтвердили получение товара.\n"
            "Продавец получит свою выплату в ближайшее время.\n\n"
            "Спасибо, что выбрали Big Stepa Safe! 🛡️"
        ),
        "en": (
            "🎉 <b>Deal #{deal_id} Completed!</b>\n\n"
            "You've confirmed receipt of the item.\n"
            "The seller will receive their payment.\n\n"
            "Thank you for using Big Stepa Safe! 🛡️"
        )
    },
    "settings_title": {
        "ru": "⚙️ <b>Настройки</b>\n\nВыберите язык интерфейса:",
        "en": "⚙️ <b>Settings</b>\n\nChoose interface language:"
    }
}


def get_text(key: str, lang: str = "ru", **kwargs) -> str:
    """Get translated text for a given key and language."""
    text = MESSAGES.get(key, {}).get(lang, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
