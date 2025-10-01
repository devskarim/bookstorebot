from aiogram.types import (
    ReplyKeyboardMarkup, ReplyKeyboardRemove,
    KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
)

adminmenu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Menu")],
        [KeyboardButton(text="🛒 Order")],
        [KeyboardButton(text="📊 Dashboard")]
    ],
    resize_keyboard=True
)


def reply_toUser(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✍️ Javob berish", callback_data=f"reply_{user_id}")]
        ]
    )


