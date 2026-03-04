import asyncio
from aiogram import Bot, Dispatcher, types, F
from duckduckgo_search import DDGS

# Вставь свой токен от @BotFather
TOKEN = "8577693645:AAH6wzHj9pcgh-MGckVsmyDb4iXT0zWogJU"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_ai_answer(prompt):
    """Прямой запрос к ИИ через DuckDuckGo (без ключей)"""
    try:
        with DDGS() as ddgs:
            # Используем модель gpt-4o-mini (бесплатно и стабильно)
            results = ddgs.chat(f"Ты бот Буся. Отвечай кратко и дружелюбно. Запрос: {prompt}", model='gpt-4o-mini')
            return results
    except Exception as e:
        print(f"Ошибка: {e}")
        return "Буся задумалась о косточке... Попробуй еще раз! 🦴"

@dp.message(F.text.lower().contains("буся"))
async def busya_handler(message: types.Message):
    user_query = message.text.lower().replace("буся", "").strip()
    
    if not user_query:
        await message.reply("Гав! Я тут. Спроси что-нибудь!")
        return

    await bot.send_chat_action(message.chat.id, "typing")
    
    # Запускаем ИИ в отдельном потоке, чтобы бот не тормозил
    loop = asyncio.get_event_loop()
    answer = await loop.run_in_executor(None, get_ai_answer, user_query)
    
    await message.reply(answer)

async def main():
    print("Буся вышла на охоту!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
