from aiogram.types import (
	ReplyKeyboardMarkup, ReplyKeyboardRemove, 
	KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
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


send_toAdminkb = ReplyKeyboardMarkup(
	keyboard=[
		[KeyboardButton(text="Yuborish")]
	],resize_keyboard=True
)

searchClickkb = InlineKeyboardMarkup(
	inline_keyboard= [
		[InlineKeyboardButton(text="📚 Title", callback_data="title")],
        [InlineKeyboardButton(text="🎭 Genre", callback_data="genre")],
        [InlineKeyboardButton(text="✍️ Author", callback_data="author")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back")]
	]
)


all_kb = ReplyKeyboardMarkup (
	keyboard= [
		[KeyboardButton(text="⬅️ back"), KeyboardButton(text="📋 Main menu")]
	],resize_keyboard=True
)