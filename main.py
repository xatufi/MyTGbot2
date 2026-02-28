import logging
import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8577693645:AAH6wzHj9pcgh-MGckVsmyDb4iXT0zWogJU"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.quotable.io/random") as resp:
            data = await resp.json()
            text = data.get("content", "Привет! Я Буся, но API недоступен 😅")
            await update.message.reply_text(text)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Буся без токена запущена 🚀")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
