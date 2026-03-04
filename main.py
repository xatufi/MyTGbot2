import asyncio
from aiogram import Bot, Dispatcher, types, F
from g4f.client import Client

# Токен получи у @BotFather
TOKEN = "8577693645:AAH6wzHj9pcgh-MGckVsmyDb4iXT0zWogJU"

bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Client()

async def get_ai_answer(prompt):
    """Запрос к бесплатному ИИ"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Можно менять на gpt-3.5-turbo
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Ой, что-то в мозгах заклинило... Попробуй еще раз!"

@dp.message(F.text.lower().contains("буся"))
async def busya_handler(message: types.Message):
    # Убираем слово "буся" из запроса, чтобы ИИ отвечал чище
    user_query = message.text.lower().replace("буся", "").strip()
    
    if not user_query:
        await message.reply("Гав? Я тут! Что нужно?")
        return

    # Показываем, что Буся "печатает"
    await bot.send_chat_action(message.chat.id, "typing")
    
    answer = await get_ai_answer(user_query)
    await message.reply(answer)

async def main():
    print("Буся запущена и готова к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
