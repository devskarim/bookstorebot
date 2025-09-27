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
		[KeyboardButton(text="📞 Telefon raqam ulashish",request_contact=True)]
	],resize_keyboard=True
)

menu_kb = ReplyKeyboardMarkup(
	keyboard=[
		[KeyboardButton(text="📋 Menu")],
    [KeyboardButton(text="🛒 Order")],
    [KeyboardButton(text="📞 Contact")]
	],resize_keyboard=True
)


after_menukb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔎 Search"), KeyboardButton(text="📚 All")],
        [KeyboardButton(text="💸 Discount"), KeyboardButton(text="🆕 New")],
        [KeyboardButton(text="⬅️ Back")]
    ],
    resize_keyboard=True
)

