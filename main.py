
import os
import json
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message, ChatJoinRequest, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN")
CHANNEL_JOIN_LINK = "https://t.me/+A4rB9KxcO8k4MTZi"
PRICE = 15000
APPROVED_FILE = "approved_users.json"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

def start_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Kod bilan kirish", callback_data="enter_code")],
        [InlineKeyboardButton(text="💳 To‘lov orqali kirish", callback_data="pay_method")]
    ])
    return keyboard

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "Kanalga kirish uchun quyidagilardan birini tanlang:",
        reply_markup=start_menu()
    )

@dp.callback_query(lambda c: c.data == "enter_code")
async def ask_code(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Iltimos, kirish kodini yuboring:")
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "pay_method")
async def send_invoice(callback_query: types.CallbackQuery):
    await bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title="Master 6000 Flashcards",
        description="Kanalga kirish uchun to‘lov",
        payload="flashcard_access",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="UZS",
        prices=[LabeledPrice(label="Kirish narxi", amount=PRICE * 100)],
        start_parameter="access-flashcard",
    )
    await callback_query.answer()

@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@dp.message(lambda message: message.successful_payment is not None)
async def successful_payment(message: Message):
    user_id = str(message.from_user.id)
    await message.answer("✅ To‘lov qabul qilindi!/nQuyidagi link orqali kanalga kirish uchun so‘rov yuboring:")
    await message.answer(f"[Kanalga kirish]({CHANNEL_JOIN_LINK})", disable_web_page_preview=True)

    try:
        with open(APPROVED_FILE, "r") as f:
            approved = json.load(f)
    except FileNotFoundError:
        approved = {}

    approved[user_id] = True
    with open(APPROVED_FILE, "w") as f:
        json.dump(approved, f, indent=2)

@dp.message()
async def handle_code(message: Message):
    user_code = message.text.strip()
    user_id = str(message.from_user.id)

    try:
        with open("codes.json", "r") as f:
            codes = json.load(f)
    except FileNotFoundError:
        await message.answer("❌ Kodlar bazasi topilmadi.")
        return

    if user_code in codes:
        if not codes[user_code]["used"]:
            codes[user_code]["used"] = True
            with open("codes.json", "w") as f:
                json.dump(codes, f, indent=2)

            try:
                with open(APPROVED_FILE, "r") as f:
                    approved = json.load(f)
            except FileNotFoundError:
                approved = {}

            approved[user_id] = True
            with open(APPROVED_FILE, "w") as f:
                json.dump(approved, f, indent=2)

            await message.answer("✅ Kod tasdiqlandi!/nQuyidagi link orqali kanalga kirish uchun so‘rov yuboring:")
            await message.answer(f"[Kanalga kirish]({CHANNEL_JOIN_LINK})", disable_web_page_preview=True)
        else:
            await message.answer("❌ Bu kod allaqachon ishlatilgan.")
    else:
        await message.answer("❌ Noto‘g‘ri kod.")

@dp.chat_join_request()
async def handle_join_request(update: ChatJoinRequest):
    user_id = str(update.from_user.id)

    try:
        with open(APPROVED_FILE, "r") as f:
            approved = json.load(f)
    except FileNotFoundError:
        approved = {}

    if approved.get(user_id):
        await update.approve()
        await bot.send_message(user_id, "✅ Kanalga kirishingiz tasdiqlandi!")
    else:
        await update.decline()
        await bot.send_message(user_id, "❌ Siz ruxsat etilganlar ro‘yxatida emassiz. Iltimos, kod kiriting yoki to‘lov qiling.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
