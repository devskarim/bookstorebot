from aiogram.types import (
    ReplyKeyboardMarkup,
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
		[KeyboardButton(text="📋 Menyu"), KeyboardButton(text="🛒 Buyurtma")],
     [KeyboardButton(text="📞 Aloqa"), KeyboardButton(text="👤 Profil")],
	],resize_keyboard=True
)

profile_kb = ReplyKeyboardMarkup(
	keyboard=[
         [KeyboardButton(text="✏️ Tahrirlash"), KeyboardButton(text="⭐ Sevimlilar")],
         [KeyboardButton(text="📄 Ma'lumotlarim"), KeyboardButton(text="❌ Accountni o'chirish")],
 				[KeyboardButton(text="⬅️ Orqaga")]
 	],resize_keyboard=True
)


after_menukb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔎 Qidirmoq"), KeyboardButton(text="📚 Barchasi")],
        [KeyboardButton(text="💸 Chegirma"), KeyboardButton(text="🆕 Yangiliklar")],
        [KeyboardButton(text="⬅️ Orqaga")]
    ],
    resize_keyboard=True
)


send_toAdminkb = ReplyKeyboardMarkup(
	keyboard=[
		[KeyboardButton(text="📤 Yuborish"), KeyboardButton(text="❌ Bekor qilish")]
	],resize_keyboard=True
)

searchClickkb = InlineKeyboardMarkup(
	inline_keyboard= [
		[InlineKeyboardButton(text="📚 Sarlavha", callback_data="title")],
         [InlineKeyboardButton(text="🎭 Janr", callback_data="genre")],
         [InlineKeyboardButton(text="✍️ Muallif", callback_data="author")],
         [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back")]
 	]
)


all_kb = ReplyKeyboardMarkup (
	keyboard= [
		[KeyboardButton(text="⬅️ Orqaga"), KeyboardButton(text="📋 Asosiy menyu")]
	],resize_keyboard=True
)


order_ikb = InlineKeyboardMarkup(
	inline_keyboard=[
		[
			InlineKeyboardButton(text="➖", callback_data="add_one"),
			InlineKeyboardButton(text="1", callback_data="add"),
			InlineKeyboardButton(text="➕", callback_data="minusOne")
		],
		[
			InlineKeyboardButton(text="❌ Bekor qilish", callback_data="sendItem"),
			InlineKeyboardButton(text="🛒 Savatchaga qo'shish", callback_data="Add_toCard"),
			InlineKeyboardButton(text="✅ Yuborish", callback_data="Cancel_item")
		]
	]
)

order_kb = ReplyKeyboardMarkup(
	keyboard= [
		[KeyboardButton(text="⭐️ Sevimlilarga qo'shish"), KeyboardButton(text="⬅️ Orqaga")]
	],resize_keyboard=True
)

skip_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏭️ Oʻtish")],
        [KeyboardButton(text="❌ Bekor qilish")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


phone_user_kb = ReplyKeyboardMarkup(
         keyboard=[
             [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)],
             [KeyboardButton(text="⏭️ Oʻtish")],
             [KeyboardButton(text="❌ Bekor qilish")]
         ],
         resize_keyboard=True,
         one_time_keyboard=True
     )

edit_field_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Ism"), KeyboardButton(text="📱 Telefon")],
        [KeyboardButton(text="🔗 Username"), KeyboardButton(text="✏️ Hammasini tahrirlash")],
        [KeyboardButton(text="✅ Tasdiqlash"), KeyboardButton(text="❌ Bekor qilish")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

edit_confirm_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Ha, yangilash"), KeyboardButton(text="❌ Yo'q, bekor qilish")],
        [KeyboardButton(text="⬅️ Orqaga")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

edit_back_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️ Orqaga")],
        [KeyboardButton(text="❌ Bekor qilish")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

del_account_inkb = InlineKeyboardMarkup(
	inline_keyboard =  [
		[InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="accept"), InlineKeyboardButton(text="❌ Qaytish", callback_data="ignore")]
    ]
)

re_active_inkb = InlineKeyboardMarkup(
	inline_keyboard= [
		[InlineKeyboardButton(text="♻️ Qayta Faolashtirish", callback_data="reActivate"), InlineKeyboardButton(text="Yo'q ❌", callback_data="not")] 
    ]
)