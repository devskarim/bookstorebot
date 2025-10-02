from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from environs import Env

admin_router = Router()

from shared import admin_reply_target

env = Env()
env.read_env()
Admin_ID = env.str("ADMIN_CHATID")

@admin_router.callback_query(F.data.startswith("reply_"))
async def admin_reply_start(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    admin_reply_target["reply_to"] = user_id
    await callback.message.answer(
        f"✍️ Siz endi foydalanuvchi ({user_id}) ga javob yozishingiz mumkin.\n\nXabaringizni yozing:"
    )
