from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
)

adminmenu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Menu"), KeyboardButton(text="📊 Boshqaruv paneli")],
        [KeyboardButton(text="🛍 Buyurtmalar"), KeyboardButton(text="🙍‍♂️ Foydalanuvchi qismiga otish")]
    ],
    resize_keyboard=True
)




def reply_toUser(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✍️ Javob berish", callback_data=f"reply_{user_id}")]
        ]
    )

admin_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Kitob qo'shish"), KeyboardButton(text="📄 Barchasini korish")], 
        [KeyboardButton(text="➖ Kitob o'chirish"), KeyboardButton(text="⬅️ orqa")]
    ],resize_keyboard=True
)
