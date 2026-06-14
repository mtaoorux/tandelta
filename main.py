import os
import time
import secrets
import hmac
import hashlib
import logging
import asyncio

asyncio.set_event_loop(asyncio.new_event_loop())

from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

# Load environment variables
load_dotenv()

API_HASH = os.environ.get("API_HASH")
API_ID = os.environ.get("API_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Secret key for HMAC signature
SECRET_KEY = b"qW4sd2kOk6"

# Time window (3 minutes)
WINDOW = 180

# Initialize bot
app = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def generate_key() -> str:
    """
    Generates a 12-character key.

    Format:
    [4-digit time slot][4-digit checksum][4-digit random]
    """
    time_slot = int(time.time() // WINDOW)
    time_str = f"{time_slot % 10000:04d}"

    sig = hmac.new(
        SECRET_KEY,
        time_str.encode(),
        hashlib.sha256,
    ).digest()

    checksum = int.from_bytes(sig, "big") % 10000
    random_suffix = secrets.randbelow(10000)

    return (
        time_str
        + f"{checksum:04d}"
        + f"{random_suffix:04d}"
    )


@app.on_message(filters.command("start") & filters.private)
async def handle_start(client, message):
    welcome_text = (
        "👋 Hey there!\n\n"
        "Welcome to **Apna Coder Key** bot.\n\n"
        "Click the button below to generate your key."
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔑 Generate Key",
                    callback_data="generate_key",
                )
            ]
        ]
    )

    await message.reply(
        welcome_text,
        reply_markup=keyboard,
    )

    logger.info(
        f"User {message.from_user.id} started the bot"
    )


@app.on_callback_query(filters.regex("^generate_key$"))
async def handle_generate_key(
    client,
    callback_query: CallbackQuery,
):
    await callback_query.answer(
        "Generating your key...",
        show_alert=False,
    )

    key = generate_key()

    text = (
        "✅ Your key has been generated!\n\n"
        f"🔐 `{key}`\n\n"
        "📋 Tap to copy."
    )

    await callback_query.message.reply(text)

    logger.info(
        f"Generated key {key} for user "
        f"{callback_query.from_user.id}"
    )


@app.on_message(
    filters.private & ~filters.command("start")
)
async def handle_any_message(client, message):
    await message.reply(
        "👆 Use /start to generate a key."
    )


if __name__ == "__main__":
    print("🚀 MTAIIRUS KEY Bot is starting...")
    app.run()
