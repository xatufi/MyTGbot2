import logging
import aiohttp
import asyncio
import time
import aiosqlite
from urllib.parse import quote
from gtts import gTTS
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes
)
from telegram.error import RetryAfter

# ==============================
# CONFIG
# ==============================

TOKEN = "8577693645:AAH6wzHj9pcgh-MGckVsmyDb4iXT0zWogJU"
TEXT_API = "https://text.pollinations.ai"
IMAGE_API = "https://image.pollinations.ai/prompt/"

MAX_MEMORY = 20
RATE_LIMIT_SECONDS = 5

# ==============================
# LOGGING
# ==============================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================
# DATABASE
# ==============================

async def init_db():
    async with aiosqlite.connect("busya.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            chat_id INTEGER,
            role TEXT,
            message TEXT
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            chat_id INTEGER PRIMARY KEY,
            personality TEXT
        )
        """)
        await db.commit()

# ==============================
# MEMORY FUNCTIONS
# ==============================

async def save_message(chat_id, role, message):
    async with aiosqlite.connect("busya.db") as db:
        await db.execute(
            "INSERT INTO memory VALUES (?, ?, ?)",
            (chat_id, role, message)
        )
        await db.commit()

async def get_memory(chat_id):
    async with aiosqlite.connect("busya.db") as db:
        async with db.execute(
            "SELECT role, message FROM memory WHERE chat_id=? ORDER BY rowid DESC LIMIT ?",
            (chat_id, MAX_MEMORY)
        ) as cursor:
            rows = await cursor.fetchall()
            return list(reversed(rows))

# ==============================
# PERSONALITY
# ==============================

PERSONALITIES = {
    "normal": "Ты Буся — умная, живая, дружелюбная девушка.",
    "sarcastic": "Ты саркастичная, язвительная, но смешная Буся.",
    "cute": "Ты милая, ласковая, эмпатичная Буся.",
    "cold": "Ты холодная, логичная, немного высокомерная Буся."
}

async def set_personality(chat_id, personality):
    async with aiosqlite.connect("busya.db") as db:
        await db.execute(
            "INSERT OR REPLACE INTO settings VALUES (?, ?)",
            (chat_id, personality)
        )
        await db.commit()

async def get_personality(chat_id):
    async with aiosqlite.connect("busya.db") as db:
        async with db.execute(
            "SELECT personality FROM settings WHERE chat_id=?",
            (chat_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else "normal"

# ==============================
# STREAM TEXT
# ==============================

async def stream_text(prompt):
    url = f"{TEXT_API}/{quote(prompt)}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()
            for i in range(0, len(text), 20):
                yield text[i:i+20]

# ==============================
# HANDLER
# ==============================

last_request_time = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text

    # ==================
    # АНТИСПАМ
    # ==================
    now = time.time()
    if user_id in last_request_time:
        if now - last_request_time[user_id] < RATE_LIMIT_SECONDS:
            return
    last_request_time[user_id] = now

    # ==================
    # IMAGE GENERATION
    # ==================
    if text.lower().startswith("нарисуй"):
        prompt = text.replace("нарисуй", "").strip()
        img_url = IMAGE_API + quote(prompt)
        await update.message.reply_photo(img_url)
        return

    # ==================
    # TEXT GENERATION
    # ==================
    personality_key = await get_personality(chat_id)
    personality = PERSONALITIES.get(personality_key, PERSONALITIES["normal"])

    memory = await get_memory(chat_id)
    context_text = "\n".join([f"{r}: {m}" for r, m in memory])

    prompt = f"""
{personality}
Вот история диалога:
{context_text}

Пользователь: {text}
Буся:
"""

    msg = await update.message.reply_text("Буся печатает...")

    full_text = ""
    last_edit = 0

    async for chunk in stream_text(prompt):
        full_text += chunk
        if time.time() - last_edit > 1:
            try:
                await msg.edit_text(full_text[:4000])
                last_edit = time.time()
            except RetryAfter as e:
                await asyncio.sleep(e.retry_after)

    await msg.edit_text(full_text[:4000])

    await save_message(chat_id, "User", text)
    await save_message(chat_id, "Буся", full_text)

# ==============================
# COMMANDS
# ==============================

async def personality_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        p = context.args[0]
        if p in PERSONALITIES:
            await set_personality(update.message.chat_id, p)
            await update.message.reply_text(f"Личность изменена на {p}")
        else:
            await update.message.reply_text("Доступно: normal, sarcastic, cute, cold")

# ==============================
# MAIN
# ==============================

async def main():
    await init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("personality", personality_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Буся PRO запущена 🚀")
    app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
