# Big Stepa Safe — Telegram Escrow Bot

🛡️ A hybrid escrow service where AI parses deals and humans verify payments.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Big Stepa Safe                           │
├─────────────────────────────────────────────────────────────┤
│  User ──► /start ──► Create Deal ──► AI Parses ──► Card    │
│                                                              │
│  Partner ◄── Notification ◄── Confirm ──► Both Accept      │
│                                                              │
│  Buyer ──► Pays ──► Proof ──► Admin Verifies ──► ✅        │
│                                                              │
│  Seller ──► Delivers ──► Buyer Confirms ──► Funds Released  │
└─────────────────────────────────────────────────────────────┘
```

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
BOT_TOKEN=123456:ABC...        # From @BotFather
ANTHROPIC_API_KEY=sk-ant-...   # From console.anthropic.com
ADMIN_ID=987654321             # Your Telegram user ID
WALLET_ADDRESS=TRC20...        # Your crypto wallet
```

**Get your Telegram ID:** Send `/start` to @userinfobot

### 3. Run the Bot

```bash
python main.py
```

## File Structure

```
botsafedeal/
├── main.py              # Entry point
├── config.py            # Environment loader
├── prompts.py           # Claude AI prompts
├── requirements.txt     # Dependencies
├── .env                 # Your secrets (gitignored)
├── .env.example         # Template
│
├── database/
│   ├── __init__.py
│   └── db_methods.py    # SQLite operations
│
├── services/
│   ├── __init__.py
│   └── ai_service.py    # Claude API integration
│
├── handlers/
│   ├── __init__.py
│   ├── user_commands.py # /start, /help, menu
│   ├── deal_flow.py     # Deal creation & lifecycle
│   └── admin_panel.py   # Payment verification
│
└── keyboards/
    ├── __init__.py
    └── inline.py        # All inline buttons
```

## Deal Flow

### 1. Deal Creation
- User clicks "Create Deal"
- Selects role (Seller/Buyer)
- Describes deal in natural language
- AI extracts: parties, amount, item, deadline

### 2. Confirmation
- Deal card shown to creator
- Invitation sent to partner
- Both parties must confirm terms

### 3. Payment
- Bot shows wallet address to buyer
- Buyer sends payment + proof (screenshot/TXID)
- Admin manually verifies payment

### 4. Execution
- Seller notified: "Funds secured, start working"
- Seller delivers product/service
- Buyer clicks "Item Received"

### 5. Release
- Admin releases funds to seller
- Deal completed! 🎉

## Admin Commands

- `/admin` — Open admin panel
- View pending verifications
- Verify or reject payments
- Release funds

## Deal Statuses

| Status | Description |
|--------|-------------|
| `draft` | AI parsed, awaiting confirmation |
| `pending_buyer` | Waiting for buyer to confirm |
| `pending_seller` | Waiting for seller to confirm |
| `confirmed` | Both parties agreed |
| `payment_pending` | Waiting for buyer payment |
| `payment_sent` | Buyer claims paid, needs verification |
| `payment_verified` | Admin confirmed payment |
| `in_progress` | Seller working on delivery |
| `delivered` | Item sent |
| `completed` | Buyer confirmed receipt, funds released |
| `disputed` | Issue raised |
| `cancelled` | Deal cancelled |

## Security Notes

- **Never share your `.env` file**
- Admin ID prevents unauthorized verification
- All payment verifications require human approval
- Use unique wallet addresses per deal (advanced)

## Tech Stack

- **Python 3.10+**
- **aiogram 3.x** — Telegram Bot API
- **aiosqlite** — Async SQLite
- **anthropic** — Claude AI API
- **pydantic** — Data validation

## Production Recommendations

1. Replace `MemoryStorage` with `RedisStorage` for FSM persistence
2. Add rate limiting to prevent abuse
3. Implement deal fee collection
4. Add dispute resolution workflow
5. Use unique wallet addresses per deal
6. Add automated deadline reminders
7. Implement logging to file/Sentry

## License

MIT

---

Built with 🛡️ by Big Stepa
