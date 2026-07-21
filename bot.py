import os
import random
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# تنظیمات
TOKEN = os.getenv("BOT_TOKEN")
ARCHIVE_CHANNEL = -1004459815440          # کانال آرشیو
FORCE_JOIN = "@spark_news_tel"           # کانال اجباری

# ۵۱ پست اولیه
EXISTING_POSTS = [
    165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151,
    150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136,
    135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121,
    120, 119, 118, 117, 116, 1
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()
new_posts = []

# ---------- ابزار ----------
async def is_member(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(FORCE_JOIN, user_id)
        return member.status not in ["left", "kicked"]
    except Exception as e:
        logger.error(f"چک عضویت ناموفق: {e}")
        return False

def get_two_random():
    all_posts = EXISTING_POSTS + new_posts
    if len(all_posts) < 2:
        return []
    return random.sample(all_posts, 2)

def join_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 عضویت در کانال", url="https://t.me/spark_news_tel")],
        [InlineKeyboardButton(text="🔄 تأیید عضویت", callback_data="check_join")]
    ])

async def send_posts(chat_id: int):
    ids = get_two_random()
    if not ids:
        await bot.send_message(chat_id, "هنوز پست کافی نیست 🙁")
        return
    for msg_id in ids:
        try:
            await bot.forward_message(chat_id=chat_id, from_chat_id=ARCHIVE_CHANNEL, message_id=msg_id)
        except Exception as e:
            logger.error(f"فوروارد خطا: {e}")
            await bot.send_message(chat_id, f"خطا در ارسال پست {msg_id}.")

# ---------- دستورات ----------
@dp.message(CommandStart())
async def start(message: types.Message):
    if not await is_member(message.from_user.id):
        await message.answer(
            "🔒 برای دریافت پست‌ها، لطفاً ابتدا در کانال زیر عضو شوید:",
            reply_markup=join_keyboard()
        )
        return
    await send_posts(message.chat.id)

@dp.callback_query(lambda c: c.data == "check_join")
async def check_join(call: types.CallbackQuery):
    if not await is_member(call.from_user.id):
        await call.answer("❌ هنوز عضو نشده‌اید!", show_alert=True)
        return

    await call.answer("✅ عضویت تأیید شد. در حال دریافت پست‌ها...")
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        pass
    await send_posts(call.message.chat.id)

# ذخیره پست‌های جدید کانال (ربات باید ادمین کانال آرشیو باشه)
@dp.channel_post()
async def new_channel_post(message: types.Message):
    new_posts.append(message.message_id)
    logger.info(f"پست جدید: {message.message_id}")

# ---------- اجرا ----------
async def main():
    logger.info("🚀 ربات با aiogram روشن شد.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
