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
    try:
        user_id = int(callback.data.split("_")[-1])
        admin_reply_target["reply_to"] = user_id
        await callback.message.answer(
            f"✍️ Siz endi foydalanuvchi ({user_id}) ga javob yozishingiz mumkin.\n\n"
            f"Xabaringizni yozing va yuboring:\n\n"
            f"⚠️ Javob yuborilgandan so'ng avtomatik ravishda keyingi xabaringiz oddiy xabar sifatida yuboriladi.\n"
            f"❌ Bekor qilish - javob berishni to'xtatish"
        )
        await callback.answer("✅ Javob rejimi faollashtirildi")
    except (ValueError, IndexError) as e:
        await callback.message.answer(f"⚠️ Xatolik: Noto'g'ri foydalanuvchi ID. {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
    except Exception as e:
        await callback.message.answer(f"⚠️ Xatolik: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
