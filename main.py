import logging
import aiohttp
import asyncio
import time
import aiosqlite
from urllib.parse import quote
from telegram import Update
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

MAX_MEMORY = 15
RATE_LIMIT_SECONDS = 4

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
# MEMORY
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
    "normal": "Ты Буся — умная, дружелюбная девушка.",
    "sarcastic": "Ты саркастичная и язвительная, но смешная Буся.",
    "cute": "Ты милая, ласковая и заботливая Буся.",
    "cold": "Ты холодная, логичная и немного высокомерная Буся."
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
# TEXT GENERATION
# ==============================

async def generate_text(prompt):
    url = f"{TEXT_API}/{quote(prompt)}"
    timeout = aiohttp.ClientTimeout(total=60)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return "Ошибка генерации текста."
            return await resp.text()

# ==============================
# RATE LIMIT
# ==============================

last_request_time = {}

def is_rate_limited(user_id):
    now = time.time()
    if user_id in last_request_time:
        if now - last_request_time[user_id] < RATE_LIMIT_SECONDS:
            return True
    last_request_time[user_id] = now
    return False

# ==============================
# MESSAGE HANDLER
# ==============================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Антиспам
    if is_rate_limited(user_id):
        return

    # Генерация изображения
    if text.lower().startswith("нарисуй"):
        prompt = text.replace("нарисуй", "").strip()
        img_url = IMAGE_API + quote(prompt)

        try:
            await update.message.reply_photo(img_url)
        except Exception:
            await update.message.reply_text("Ошибка генерации изображения.")
        return

    # Генерация текста
    personality_key = await get_personality(chat_id)
    personality = PERSONALITIES.get(personality_key, PERSONALITIES["normal"])

    memory = await get_memory(chat_id)
    context_text = "\n".join([f"{r}: {m}" for r, m in memory])

    prompt = f"""
{personality}

История диалога:
{context_text}

Пользователь: {text}
Буся:
"""

    try:
        await update.message.chat.send_action("typing")
    except:
        pass

    try:
        response = await generate_text(prompt)
        response = response[:4000]

        await update.message.reply_text(response)

        await save_message(chat_id, "User", text)
        await save_message(chat_id, "Буся", response)

    except RetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await update.message.reply_text("Слишком много запросов, подожди немного.")

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Произошла ошибка 😔")

# ==============================
# COMMANDS
# ==============================

async def personality_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if context.args:
        p = context.args[0]
        if p in PERSONALITIES:
            await set_personality(chat_id, p)
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

    logger.info("Буся запущена 🚀")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
