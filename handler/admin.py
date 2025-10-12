from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from database import is_admin
from buttons import adminmenu_kb, menu_kb, reply_toUser
from environs import Env


admin_router = Router()

env = Env()
env.read_env()

Admin_ID = env.str("ADMIN_CHATID")

from shared import admin_reply_target

@admin_router.message(Command("admin"))
async def admin_handler(message: Message, **kwargs):
	if is_admin(message.from_user.id):
		await message.answer("Admin menyu", reply_markup=adminmenu_kb)
	else:
		await message.answer("⛔ Sizda admin huquqi yo'q.")


@admin_router.message(Command("user"))
async def get_user(message:Message, **kwargs):
	await message.answer("Foydalanuvchi rejimiga qaytildi", reply_markup=menu_kb)


@admin_router.message(F.reply_to_message, lambda m: m.from_user.id == Admin_ID)
async def reply_to_user(message: Message, **kwargs):
    replied = message.reply_to_message

    if replied and "UserID:" in replied.text:
        try:
            user_id = int(replied.text.split("UserID:")[1].split("\n")[0])

            await message.bot.send_message(
                user_id,
                f"📩 Admin javobi:\n\n{message.text}"
            )
            await message.answer("✅ Javob foydalanuvchiga yuborildi.")
        except Exception as e:
            await message.answer(f"⚠️ Xatolik: {e}")


@admin_router.message(F.text, lambda m: m.from_user.id == int(Admin_ID) and "reply_to" in admin_reply_target)
async def handle_admin_reply(message: Message, **kwargs):
    try:
        target_user_id = admin_reply_target["reply_to"]

        await message.bot.send_message(
            target_user_id,
            f"📩 Admin javobi:\n\n{message.text}"
        )
        await message.answer("✅ Javob foydalanuvchiga yuborildi.")
        if "reply_to" in admin_reply_target:
            del admin_reply_target["reply_to"]
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {e}")
        if "reply_to" in admin_reply_target:
            del admin_reply_target["reply_to"]

@admin_router.message(F.text  == "🛒 Buyurtmalar")
async def orders_handler(message: Message, **kwargs):
    await message.answer("Qurilishda...")


@admin_router.message(F.text == "📊 Boshqaruv paneli")
async def dashboard_handler(message: Message, **kwargs):
      await message.answer("Qurilishda..")


@admin_router.message(F.text == "⬅️ Ortga")
async def back_handler(message: Message, **kwargs):
    await message.answer("Asosiy menyu", reply_markup=menu_kb)


@admin_router.callback_query(F.data.startswith("reply_"))
async def admin_reply_start(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    admin_reply_target["reply_to"] = user_id
    await callback.message.answer(
        f"✍️ Siz endi foydalanuvchi ({user_id}) ga javob yozishingiz mumkin.\n\nXabaringizni yozing:"
    )
    await callback.answer()