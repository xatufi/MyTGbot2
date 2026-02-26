import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BOT_NAME = os.getenv("BOT_NAME", "буся").lower()

# Инициализация
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# ================================
# GPT ОТВЕТ
# ================================
async def ask_gpt(user_text: str):
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Ты дружелюбная кошка по имени Буся. Отвечай мило, но информативно."
            },
            {"role": "user", "content": user_text}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content


# ================================
# ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЯ
# ================================
async def generate_image(prompt: str):
    response = await client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )
    return response.data[0].url


# ================================
# ОБРАБОТКА СООБЩЕНИЙ
# ================================
@dp.message(F.text)
async def handle_message(message: types.Message):

    if not message.text:
        return

    text_lower = message.text.lower()

    # Бот реагирует только если упомянули имя
    if BOT_NAME not in text_lower:
        return

    # Убираем имя из текста
    cleaned_text = text_lower.replace(BOT_NAME, "").strip()

    # Если просят нарисовать
    if any(word in text_lower for word in ["нарисуй", "картинка", "изобрази", "создай изображение"]):

        await message.reply("Мяу... сейчас нарисую 🎨")

        try:
            image_url = await generate_image(cleaned_text)

            # Скачиваем изображение
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        photo = await resp.read()
                        await message.answer_photo(photo=photo)

        except Exception as e:
            await message.reply(f"Мяу... ошибка при рисовании 😿\n{e}")

    else:
        # Обычный ответ GPT
        try:
            answer = await ask_gpt(cleaned_text)
            await message.reply(answer)
        except Exception as e:
            await message.reply(f"Мяу... я запуталась 😿\n{e}")


# ================================
# ЗАПУСК
# ================================
async def main():
    print(f"🐾 Буся запущена и готова общаться!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())    # Проверяем, упомянуто ли имя бота
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
