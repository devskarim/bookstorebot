from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
)

adminmenu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 Buyurtmalar"), KeyboardButton(text="📊 Boshqaruv paneli")],
        [KeyboardButton(text="⬅️ Ortga")]
    ],
    resize_keyboard=True
)




def reply_toUser(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✍️ Javob berish", callback_data=f"reply_{user_id}")]
        ]
    )

