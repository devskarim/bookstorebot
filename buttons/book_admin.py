from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

book_management_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Kitob qo'shish"), KeyboardButton(text="📖 Kitoblarni ko'rish")],
        [KeyboardButton(text="✏️ Kitob tahrirlash"), KeyboardButton(text="🗑️ Kitob o'chirish")],
        [KeyboardButton(text="🔍 Kitob qidirish"), KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="⬅️ Ortga")]
    ],
    resize_keyboard=True
)

confirm_add_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, qo'shish", callback_data="confirm_add_book")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_add_book")]
    ]
)

confirm_edit_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, yangilash", callback_data="confirm_edit_book")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_edit_book")]
    ]
)

confirm_delete_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🗑️ Ha, o'chirish", callback_data="confirm_delete_book")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_delete_book")]
    ]
)

# Back to book management menu
back_to_book_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Kitob boshqaruviga qaytish", callback_data="back_to_book_management")]
    ]
)

# Book selection for editing/deleting
def book_selection_kb(books, action="edit"):
    """Create keyboard with book selection buttons"""
    keyboard = []

    for book in books[:10]:  # Limit to 10 books per page
        callback_data = f"{action}_book_{book['id']}"
        text = f"📖 {book['title']} - {book['author']}"
        keyboard.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    # Add navigation buttons if needed
    nav_buttons = [InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_to_book_management")]

    if len(books) > 10:
        nav_buttons.insert(0, InlineKeyboardButton(text="▶️ Keyingi", callback_data="next_books_page"))

    keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Book field selection for editing
edit_field_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📝 Sarlavha", callback_data="edit_title")],
        [InlineKeyboardButton(text="👨‍💼 Muallif", callback_data="edit_author")],
        [InlineKeyboardButton(text="💰 Narx", callback_data="edit_price")],
        [InlineKeyboardButton(text="📄 Tavsif", callback_data="edit_description")],
        [InlineKeyboardButton(text="🏷️ Janr", callback_data="edit_genre")],
        [InlineKeyboardButton(text="📦 Miqdor", callback_data="edit_quantity")],
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_to_book_management")]
    ]
)

# Skip/Cancel options
skip_cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏭️ O'tkazib yuborish"), KeyboardButton(text="❌ Bekor qilish")],
        [KeyboardButton(text="⬅️ Ortga")]
    ],
    resize_keyboard=True
)

# Book viewing options
book_view_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Tahrirlash", callback_data="edit_this_book")],
        [InlineKeyboardButton(text="🗑️ O'chirish", callback_data="delete_this_book")],
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_to_books_list")]
    ]
)

# Genre selection (common genres)
genre_selection_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Badiiy"), KeyboardButton(text="🎓 Ilmiy")],
        [KeyboardButton(text="👶 Bolalar"), KeyboardButton(text="💼 Biznes")],
        [KeyboardButton(text="📰 Publitsistika"), KeyboardButton(text="📖 Chet til")],
        [KeyboardButton(text="❌ O'tkazib yuborish"), KeyboardButton(text="⬅️ Ortga")]
    ],
    resize_keyboard=True
)

# Book search options
search_options_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Sarlavha bo'yicha"), KeyboardButton(text="👤 Muallif bo'yicha")],
        [KeyboardButton(text="🏷️ Janr bo'yicha"), KeyboardButton(text="💰 Narx oralig'i")],
        [KeyboardButton(text="⬅️ Ortga")]
    ],
    resize_keyboard=True
)