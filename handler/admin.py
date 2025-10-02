from aiogram.types import Message 
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
async def admin_handler(message: Message):
	if is_admin(message.from_user.id):
		await message.answer("Admin menu", reply_markup=adminmenu_kb)
	else:
		await message.answer("⛔ Sizda admin huquqi yo'q.")


@admin_router.message(Command("user")) 
async def get_user(message:Message): 
	await message.answer("Foydalanuvchiga qaytdingiz", reply_markup=menu_kb)


@admin_router.message(F.reply_to_message, lambda m: m.from_user.id == Admin_ID)
async def reply_to_user(message: Message):
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
async def handle_admin_reply(message: Message):
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
