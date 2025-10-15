from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
)

adminmenu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 Buyurtmalar"), KeyboardButton(text="📚 Kitoblar")],
        [KeyboardButton(text="� Boshqaruv paneli")],
        [KeyboardButton(text="⬅️ Ortga")]
    ],
    resize_keyboard=True
)


super_admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👑 Admin qo'shish"), KeyboardButton(text="👥 Foydalanuvchilarni ko'rish")],
        [KeyboardButton(text="📈 Oylik hisobot"), KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="🗑 Admin o'chirish"), KeyboardButton(text="🔧 Test PDF")],
        [KeyboardButton(text="⬅️ Orqaga")]
    ],
    resize_keyboard=True
)

regular_admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👥 Foydalanuvchilarni ko'rish"), KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="⬅️ Orqaga"), KeyboardButton(text="📋 Menu")]
    ],
    resize_keyboard=True
)


admin_level_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🏛 Oddiy Admin", callback_data="admin_level:admin")],
        [InlineKeyboardButton(text="👑 Super Admin", callback_data="admin_level:super_admin")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_level:cancel")]
    ]
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



admin_kb = ReplyKeyboardMarkup(
    keyboard= [
        [KeyboardButton(text="Admin qoshish"), KeyboardButton(text="Jami Foydalanuvchilarni korish")], 
    ]
)