import asyncio
from aiogram import Bot, Dispatcher, types, F

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# =======================
TELEGRAM_TOKEN = "8577693645:AAH6wzHj9pcgh-MGckVsmyDb4iXT0zWogJU"
# =======================

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

print("ЗАГРУЖАЕМ МОДЕЛЬ... ПОДОЖДИ 🐾")

model_name = "gpt2-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

print("МОДЕЛЬ ГОТОВА! Буся мурчит 🐱")

def get_ai_answer(prompt: str) -> str:
    input_text = f"Ты — кошка Буся. Отвечай дружелюбно и коротко:\n{prompt}"
    inputs = tokenizer.encode(input_text, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=150,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.9
        )

    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text[len(input_text):].strip()

@dp.message(F.text.lower().contains("буся"))
async def busya_handler(message: types.Message):
    user_text = message.text.lower().replace("буся", "").strip()

    if not user_text:
        await message.reply("Мяу! Спросить что-нибудь? 🐾")
        return

    await bot.send_chat_action(message.chat.id, "typing")

    loop = asyncio.get_event_loop()
    answer = await loop.run_in_executor(None, get_ai_answer, user_text)

    await message.reply(answer)

async def main():
    print("БУСЯ ОТКРЫЛА ТЕЛЕГРАМ 🐱")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
