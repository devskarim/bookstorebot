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
		await message.answer("Admin menyu", reply_markup=adminmenu_kb)
	else:
		await message.answer("⛔ Sizda admin huquqi yo'q.")


@admin_router.message(Command("user")) 
async def get_user(message:Message): 
	await message.answer("Foydalanuvchi rejimiga qaytildi", reply_markup=menu_kb)


@admin_router.message(F.text, lambda m: m.from_user.id == int(Admin_ID) and "reply_to" in admin_reply_target)
async def handle_admin_reply(message: Message):
    """Handle admin reply when reply_to target is set"""
    try:
        target_user_id = admin_reply_target["reply_to"]

        await message.bot.send_message(
            target_user_id,
            f"📩 Admin javobi:\n\n{message.text}"
        )
        await message.answer("✅ Javob foydalanuvchiga yuborildi.")
        # Clean up the reply target after successful send
        if "reply_to" in admin_reply_target:
            del admin_reply_target["reply_to"]
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {e}")
        # Clean up on error too
        if "reply_to" in admin_reply_target:
            del admin_reply_target["reply_to"]


@admin_router.message(F.reply_to_message, lambda m: m.from_user.id == Admin_ID)
async def reply_to_user(message: Message):
    """Handle admin reply to forwarded user messages"""
    replied = message.reply_to_message

    if replied and "UserID:" in replied.text:
        try:
            user_id = int(replied.text.split("UserID:")[1].split("\n")[0])

            await message.bot.send_message(
                user_id,
                f"📩 Admin javobi:\n\n{message.text}"
            )
            await message.answer("✅ Javob foydalanuvchiga yuborildi.")
        except (ValueError, IndexError) as e:
            await message.answer(f"⚠️ Xatolik: Foydalanuvchi ID topilmadi. {e}")
        except Exception as e:
            await message.answer(f"⚠️ Xatolik: {e}")


@admin_router.message(F.text  == "🛒 Buyurtmalar")
async def orders_handler(message: Message): 
    await message.answer("Qurilishda...")


@admin_router.message(F.text == "📊 Boshqaruv paneli")
async def dashboard_handler(message: Message): 
     await message.answer("Qurilishda..")

@admin_router.message(F.text == "⬅️ Ortga")
async def back_handler(message: Message):
    await message.answer("Asosiy menyu", reply_markup=menu_kb)


@admin_router.message(F.text == "❌ Bekor qilish", lambda m: m.from_user.id == int(Admin_ID))
async def cancel_reply_handler(message: Message):
    """Cancel admin reply mode"""
    if "reply_to" in admin_reply_target:
        del admin_reply_target["reply_to"]
        await message.answer("✅ Javob rejimi bekor qilindi.")
    else:
        await message.answer("❌ Javob rejimi faol emas.")