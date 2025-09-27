from aiogram.types import Message 
from aiogram import Router, F 
from aiogram.filters import Command, CommandStart 
from database import is_admin
from buttons import adminmenu_kb, menu_kb

admin_router = Router() 

@admin_router.message(Command("admin"))
async def admin_handler(message: Message):
	if is_admin(message.from_user.id):
		await message.answer("Admin menu", reply_markup=adminmenu_kb)
	else:
		await message.answer("⛔ Sizda admin huquqi yo‘q.")


@admin_router.message(Command("user")) 
async def get_user(message:Message): 
	await message.answer("Userga qaytdingiz", reply_markup=menu_kb)