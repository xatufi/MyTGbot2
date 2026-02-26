import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from openai import AsyncOpenAI

# =======================
# ВСТАВЬ СЮДА СВОИ КЛЮЧИ
# =======================
TELEGRAM_TOKEN = "8707608068:AAH2z1zsDcxhqz7CscUBZOd8HY3FX4VRrqQ"
OPENAI_API_KEY = "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"
BOT_NAME = "буся"  # имя, на которое реагирует бот
# =======================

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

BOT_NAME = BOT_NAME.lower()


# ========= GPT =========
async def ask_gpt(user_text: str):
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Ты милая кошка по имени Буся. Отвечай дружелюбно, но информативно."
            },
            {
                "role": "user",
                "content": user_text
            }
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content


# ======== IMAGE ========
async def generate_image(prompt: str):
    response = await client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )
    return response.data[0].url


# ======== HANDLER ========
@dp.message(F.text)
async def handle_message(message: types.Message):

    if not message.text:
        return

    text_lower = message.text.lower()

    # Бот реагирует только если упомянули имя
    if BOT_NAME not in text_lower:
        return

    cleaned_text = text_lower.replace(BOT_NAME, "").strip()

    # Проверка на генерацию картинки
    if any(word in text_lower for word in ["нарисуй", "картинка", "изобрази", "создай"]):

        await message.reply("Мяу... рисую 🎨")

        try:
            image_url = await generate_image(cleaned_text)

            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        photo = await resp.read()
                        await message.answer_photo(photo=photo)

        except Exception as e:
            await message.reply(f"Ошибка при рисовании 😿\n{e}")

    else:
        try:
            answer = await ask_gpt(cleaned_text)
            await message.reply(answer)
        except Exception as e:
            await message.reply(f"Ошибка 😿\n{e}")


# ======== START ========
async def main():
    print("🐾 Буся запущена!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
