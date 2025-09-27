from aiogram.types import (
	ReplyKeyboardMarkup, ReplyKeyboardRemove, 
	KeyboardButton, InlineKeyboardButton, InlineKeyboardButton
)

adminmenu_kb = ReplyKeyboardMarkup(
	keyboard=[
		[KeyboardButton(text="📋 Menu")],
    [KeyboardButton(text="🛒 Order")],
    [KeyboardButton(text=" 📊Dashboard")]
	],resize_keyboard=True
)