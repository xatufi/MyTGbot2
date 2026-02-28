import logging
import aiohttp
import asyncio
from urllib.parse import quote
from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ===== SETTINGS =====
TELEGRAM_TOKEN = "8577693645:AAH6wzHj9pcgh-MGckVsmyDb4iXT0zWogJU"
PIXAZO_API_KEY = "f071b54ed6584cebb9b361b3994edffd"

POLLINATIONS_TEXT_URL = "https://text.pollinations.ai"
PIXAZO_IMAGE_URL = "https://api.pixazo.ai/v1/text2image"

# ===== LOGGING =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== CONTEXT MEMORY =====
chat_memory = {}  # {chat_id: [messages...]}

# ===== HELPERS =====

async def generate_text(prompt: str) -> str:
    url = f"{POLLINATIONS_TEXT_URL}/{quote(prompt)}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=30) as resp:
            if resp.status == 200:
                return await resp.text()
            return "Не удалось получить ответ 😢"

async def generate_image(prompt: str) -> str:
    headers = {"Authorization": f"Bearer {PIXAZO_API_KEY}"}
    payload = {"prompt": prompt, "size": "1024x1024"}
    async with aiohttp.ClientSession() as session:
        async with session.post(PIXAZO_IMAGE_URL, json=payload, headers=headers, timeout=60) as resp:
            data = await resp.json()
            if resp.status == 200 and "url" in data:
                return data["url"]
            return ""

# ===== HANDLER =====

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text: return
    if "буся" not in text.lower(): return

    chat_id = update.message.chat_id
    user_msg = text.replace("Буся", "").strip()

    # save memory
    mem = chat_memory.get(chat_id, [])
    mem.append(f"User: {user_msg}")
    if len(mem) > 10: mem.pop(0)
    chat_memory[chat_id] = mem

    # image request
    if "нарисуй" in user_msg:
        prompt = user_msg.replace("нарисуй", "").strip()
        msg = await update.message.reply_text("Буся генерирует изображение... 🎨")
        img_url = await generate_image(prompt)
        if img_url:
            await update.message.reply_photo(photo=img_url)
        else:
            await update.message.reply_text("Ошибка генерации 😿")
        return

    # text stream + typing effect
    prompt_text = "\n".join(mem + [f"Буся:"])
    stream_msg = await update.message.reply_text("Буся печатает...")

    response_text = await generate_text(prompt_text)

    # typing effect
    typed = ""
    for ch in response_text:
        typed += ch
        try:
            await stream_msg.edit_text(typed)
        except:
            pass
        await asyncio.sleep(0.02)

    # save Buся response
    mem.append(f"Буся: {response_text}")
    chat_memory[chat_id] = mem

# ===== RUN =====

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
