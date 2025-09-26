from aiogram.types import (
	ReplyKeyboardMarkup, ReplyKeyboardRemove, 
	KeyboardButton, InlineKeyboardButton, InlineKeyboardButton
)

register_kb = ReplyKeyboardMarkup( 
	keyboard=[
		[KeyboardButton(text="Ro'yxatdan O'tish")]
	],resize_keyboard=True
)


phoneNumber_kb = ReplyKeyboardMarkup(
	keyboard=[
		KeyboardButton(text="📞 Telefon raqam ulashish",request_contact=True)
	],resize_keyboard=True
)