import logging
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Токен бота
TOKEN = "8577693645:AAH6wzHj9pcgh-MGckVsmyDb4iXT0zWogJU"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатываем все текстовые сообщения"""
    if not update.message or not update.message.text:
        return

    try:
        # Запрос случайной цитаты
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.quotable.io/random") as resp:
                data = await resp.json()
                text = data.get("content", "Привет! Я Буся, но API недоступен 😅")
    except Exception as e:
        logger.error(f"Ошибка при запросе к API: {e}")
        text = "Привет! Я Буся, но API недоступен 😅"

    await update.message.reply_text(text)

def main():
    # Создаём приложение бота
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчик всех текстовых сообщений (кроме команд)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Буся запущена 🚀")

    # Запуск бота (сам управляет asyncio)
    app.run_polling()

if __name__ == "__main__":
    main()
