import asyncio
from aiogram import Bot, Dispatcher, types, F
from openai import AsyncOpenAI

# 1. ВСТАВЬ СВОИ ДАННЫЕ ТУТ:
BOT_TOKEN = "8577693645:AAH6wzHj9pcgh-MGckVsmyDb4iXT0zWogJU"
AI_API_KEY = "PiIFdqwXHJdgh5CAfOJeYbrePb1M9bBW"

# Настройка клиента ИИ (пример для Mistral, для DeepSeek смени base_url)
client = AsyncOpenAI(
    api_key=AI_API_KEY,
    base_url="https://api.mistral.ai" 
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def get_ai_response(text):
    try:
        response = await client.chat.completions.create(
            model="mistral-tiny", # Или "deepseek-chat"
            messages=[
                {"role": "system", "content": "Ты — веселый бот по имени Буся. Помогаешь решать задачи и просто общаешься."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка ИИ: {e}")
        return "Буся немного устала... Попробуй спросить чуть позже! 🐾"

@dp.message(F.text.lower().contains("буся"))
async def handle_busya(message: types.Message):
    # Очищаем запрос от имени "буся"
    user_prompt = message.text.lower().replace("буся", "").strip()
    
    if not user_prompt:
        await message.reply("Гав! Я тут. Что нужно решить или обсудить?")
        return

    # Эффект печатания
    await bot.send_chat_action(message.chat.id, "typing")
    
    answer = await get_ai_response(user_prompt)
    await message.reply(answer)

async def main():
    print("Буся запущена!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
