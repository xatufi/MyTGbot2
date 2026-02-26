import asyncio
from aiogram import Bot, Dispatcher, types, F
from openai import AsyncOpenAI

# --- НАСТРОЙКИ ---
TELEGRAM_TOKEN = "ВАШ_ТГ_ТОКЕН"
OPENAI_API_KEY = "ВАШ_OPENAI_КЛЮЧ"
BOT_NAME = "дружбан"  # Имя, на которое будет отзываться бот

# Инициализация
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def ask_gpt(prompt):
    """Запрос к GPT для общения"""
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo", # или gpt-4
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

async def generate_image(prompt):
    """Генерация картинки через DALL-E"""
    response = await client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response.data[0].url

@dp.message(F.text)
async def handle_message(message: types.Message):
    text = message.text.lower()
    
    # Проверяем, упомянуто ли имя бота
    if BOT_NAME in text:
        # Если в тексте есть просьба нарисовать
        if any(word in text for word in ["нарисуй", "картинка", "изобрази"]):
            await message.reply("Рисую, подожди немного... 🎨")
            try:
                image_url = await generate_image(message.text)
                await message.answer_photo(photo=image_url)
            except Exception as e:
                await message.reply(f"Ошибка при рисовании: {e}")
        
        # Обычный ответ на вопрос
        else:
            try:
                answer = await ask_gpt(message.text)
                await message.reply(answer)
            except Exception as e:
                await message.reply(f"Не смог ответить: {e}")

async def main():
    print(f"Бот {BOT_NAME} запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
