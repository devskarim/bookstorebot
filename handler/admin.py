import os
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.query import is_admin
from database.admin_query import add_book, get_all_books, get_book_by_id, delete_book, update_book, search_books, generate_books_pdf, generate_books_pdf_pdfkit, save_image_from_telegram, REPORTLAB_AVAILABLE, PDFKIT_AVAILABLE, get_books_paginated, create_pagination_keyboard, get_all_orders, get_order_details, update_order_status
from database.connection import get_connect
from database.query import (
    add_admin, get_all_users, get_user_by_chat_id_or_phone, get_user_by_username,
    generate_users_pdf, is_super_admin, is_regular_admin, add_admin_with_level,
    remove_admin, get_all_admins, get_monthly_stats
)
from buttons.admin import adminmenu_kb, admin_menu_kb, super_admin_kb, regular_admin_kb, admin_level_kb
from buttons.user import menu_kb
from states.book_management import BookManagement
from buttons.admin import reply_toUser
from environs import Env

admin_router = Router()

env = Env()
env.read_env()

ADMIN_CHATID = env.str("ADMIN_CHATID")

from shared import admin_reply_target

@admin_router.message(Command("admin"))
async def admin_handler(message: Message, **kwargs):
	if is_admin(message.from_user.id):
		await message.answer("Admin menyu", reply_markup=adminmenu_kb)
	else:
		await message.answer("⛔ Sizda admin huquqi yo'q.")

@admin_router.message(Command("user"))
async def get_user(message:Message, **kwargs):
	await message.answer("Foydalanuvchi rejimiga qaytildi", reply_markup=menu_kb)

@admin_router.message(F.reply_to_message, lambda m: m.from_user.id == int(ADMIN_CHATID))
async def reply_to_user(message: Message, **kwargs):
    replied = message.reply_to_message

    if replied and "UserID:" in replied.text:
        try:
            user_id = int(replied.text.split("UserID:")[1].split("\n")[0])

            await message.bot.send_message(
                user_id,
                f"📩 Admin javobi:\n\n{message.text}"
            )
            await message.answer("✅ Javob foydalanuvchiga yuborildi.")
        except Exception as e:
            await message.answer(f"⚠️ Xatolik: {e}")

@admin_router.message(F.text, lambda m: str(m.from_user.id) == ADMIN_CHATID and "reply_to" in admin_reply_target)
async def handle_admin_reply(message: Message, **kwargs):
    try:
        target_user_id = admin_reply_target["reply_to"]

        await message.bot.send_message(
            target_user_id,
            f"📩 Admin javobi:\n\n{message.text}"
        )
        await message.answer("✅ Javob foydalanuvchiga yuborildi.")
        if "reply_to" in admin_reply_target:
            del admin_reply_target["reply_to"]
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {e}")
        if "reply_to" in admin_reply_target:
            del admin_reply_target["reply_to"]

@admin_router.message(F.text  == "📋 Menu")
async def orders_handler(message: Message, **kwargs):
    await message.answer("Asosiy menyu", reply_markup=admin_menu_kb)


@admin_router.message(F.text == "⬅️ Ortga")
async def back_handler(message: Message, **kwargs):
    await message.answer("Siz allaqachon admin menudasiz.")

@admin_router.message(F.text == "📄 Barchasini korish")
async def view_all_books(message: Message, **kwargs):
    books = get_all_books()

    if not books:
        await message.answer(
            "📚 Kitoblar ro'yxati bo'sh.\n\n"
            "Admin menyu",
            reply_markup=admin_menu_kb
        )
        return

    await message.answer("📄 PDF fayl yaratilmoqda...")

    pdf_path = None

    if REPORTLAB_AVAILABLE:
        pdf_path = generate_books_pdf(books)

    if not pdf_path and PDFKIT_AVAILABLE:
        pdf_path = generate_books_pdf_pdfkit(books)

    if pdf_path and os.path.exists(pdf_path):
        try:
            await message.bot.send_document(
                chat_id=message.chat.id,
                document=FSInputFile(pdf_path),
                caption=f"📚 Barcha kitoblar ro'yxati ({len(books)} ta kitob)\n\nAdmin menyu",
                reply_markup=admin_menu_kb
            )
        except Exception as e:
            await message.answer(
                f"❌ PDF yuborishda xatolik: {e}\n\n"
                "Matn ko'rinishida ko'rish:",
                reply_markup=admin_menu_kb
            )
            await show_books_as_text(message, books)
    else:
        if not REPORTLAB_AVAILABLE and not PDFKIT_AVAILABLE:
            await message.answer(
                "❌ PDF yaratishda xatolik yuz berdi!\n\n"
                "📦 <b>Kerakli kutubxonalar o'rnatilmagan:</b>\n\n"
                "💡 <b>O'rnatish uchun:</b>\n"
                "<code>pip install reportlab</code>\n\n"
                "📝 <b>Yoki alternativ:</b>\n"
                "<code>pip install pdfkit</code>\n\n"
                "🔧 <b>Barchasini o'rnatish:</b>\n"
                "<code>pip install -r requirements.txt</code>\n\n"
                "⏳ <i>Kutubxonalar o'rnatilguncha matn ko'rinishida ko'rsatiladi</i>",
                parse_mode="HTML",
                reply_markup=admin_menu_kb
            )
        else:
            if not REPORTLAB_AVAILABLE:
                await message.answer(
                    "❌ PDF yaratishda xatolik yuz berdi!\n\n"
                    "📦 <b>ReportLab kutubxonasi o'rnatilmagan</b>\n\n"
                    "💡 <b>O'rnatish uchun:</b>\n"
                    "<code>pip install reportlab</code>\n\n"
                    "📝 <b>Yoki alternativ:</b>\n"
                    "<code>pip install pdfkit</code>\n\n"
                    "⏳ <i>Hozircha matn ko'rinishida ko'rsatiladi</i>",
                    parse_mode="HTML",
                    reply_markup=admin_menu_kb
                )
            elif not PDFKIT_AVAILABLE:
                await message.answer(
                    "❌ PDF yaratishda xatolik yuz berdi!\n\n"
                    "📦 <b>pdfkit kutubxonasi o'rnatilmagan</b>\n\n"
                    "💡 <b>O'rnatish uchun:</b>\n"
                    "<code>pip install pdfkit</code>\n\n"
                    "📝 <b>Yoki asosiy:</b>\n"
                    "<code>pip install reportlab</code>\n\n"
                    "⏳ <i>Hozircha matn ko'rinishida ko'rsatiladi</i>",
                    parse_mode="HTML",
                    reply_markup=admin_menu_kb
                )
            else:
                await message.answer(
                    "❌ PDF yaratishda noma'lum xatolik yuz berdi.\n\n"
                    "📞 <b>Admin bilan bog'laning</b>\n\n"
                    "⏳ <i>Matn ko'rinishida ko'rsatiladi</i>",
                    parse_mode="HTML",
                    reply_markup=admin_menu_kb
                )
        await show_books_as_text(message, books)

async def show_books_as_text(message: Message, books):
    response = "📚 Barcha kitoblar:\n\n"

    for book in books:
        response += (
            f"ID: {book['id']}\n"
            f"📖 Nomi: {book['title']}\n"
            f"✍️ Muallifi: {book['author']}\n"
            f"💰 Narxi: {book['price']}\n"
            f"📂 Janri: {book['genre']}\n"
            f"📦 Miqdori: {book['quantity']}\n"
        )

        if book.get('image_path'):
            response += f"🖼 Rasm: Bor\n"

        if book.get('description'):
            desc = book['description'][:100] + "..." if len(book['description']) > 100 else book['description']
            response += f"📝 Tavsif: {desc}\n"

        response += "\n" + "─" * 30 + "\n"

    if len(response) > 4096:
        chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for chunk in chunks:
            await message.answer(chunk)
    else:
        await message.answer(response)

@admin_router.message(F.text == "➖ Kitob o'chirish")
async def delete_books(message: Message, state: FSMContext):
    books = get_all_books()

    if not books:
        await message.answer(
            "❌ O'chirish uchun kitoblar yo'q.\n\n"
            "Admin menyu",
            reply_markup=admin_menu_kb
        )
        return

    response = "🗑 Kitob o'chirish\n\nQuyidagi kitoblardan birini tanlang:\n\n"

    for book in books[:20]:
        response += f"🆔 {book['id']}: {book['title']} - {book['author']}\n"

    response += "\nKitob ID sini kiriting (faqat raqam):\n"
    response += "❌ Bekor qilish: /cancel"

    await message.answer(response)
    await state.set_state(BookManagement.waiting_for_book_id)

@admin_router.message(BookManagement.waiting_for_book_id)
async def process_book_deletion(message: Message, state: FSMContext):
    if message.text and message.text.lower() == '/cancel':
        await state.clear()
        await message.answer(
            "❌ <b>Kitob o'chirish bekor qilindi</b>\n\n"
            "📚 Hech narsa o'chirilmadi.\n\n"
            "Admin menyu",
            parse_mode="HTML",
            reply_markup=admin_menu_kb
        )
        return

    try:
        book_id = int(message.text)

        book = get_book_by_id(book_id)

        if not book:
            await message.answer(
                f"❌ ID {book_id} topilmadi. Qaytadan urinib ko'ring.\n\n"
                "Kitob ID sini kiriting:\n"
                "❌ Bekor qilish: /cancel"
            )
            return

        if delete_book(book_id):
            await message.answer(
                f"✅ Kitob o'chirildi!\n\n"
                f"📖 Nomi: {book['title']}\n"
                f"✍️ Muallifi: {book['author']}\n\n"
                f"Admin menyu",
                reply_markup=admin_menu_kb
            )
        else:
            await message.answer(
                "❌ Kitob o'chirishda xatolik yuz berdi.\n\n"
                "Admin menyu",
                reply_markup=admin_menu_kb
            )

        await state.clear()

    except ValueError:
        await message.answer(
            "❌ Kitob ID sini faqat raqam bilan kiriting. Qaytadan urinib ko'ring:\n"
            "❌ Bekor qilish: /cancel"
        )

@admin_router.message(F.text == "⬅️ orqa")
async def back_handler(message: Message, **kwargs):
    await message.answer("Admin menu", reply_markup=adminmenu_kb)


@admin_router.callback_query(F.data.startswith("reply_"))
async def admin_reply_start(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    admin_reply_target["reply_to"] = user_id
    await callback.message.answer(
        f"✍️ Siz endi foydalanuvchi ({user_id}) ga javob yozishingiz mumkin.\n\nXabaringizni yozing:"
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin_level:"))
async def handle_admin_level_selection(callback: CallbackQuery, state: FSMContext):
    """Handle admin level selection"""
    data = callback.data.split(":")[1]

    if data == "cancel":
        await state.clear()
        await callback.message.answer(
            "❌ <b>Admin qo'shish bekor qilindi</b>\n\n"
            "📊 Boshqaruv paneli",
            parse_mode="HTML",
            reply_markup=super_admin_kb
        )
        await callback.answer()
        return

    state_data = await state.get_data()
    user = state_data.get('selected_user')

    if not user:
        await callback.message.answer(
            "❌ <b>Xatolik: Foydalanuvchi ma'lumotlari topilmadi</b>\n\n"
            "Qaytadan boshlang.",
            reply_markup=super_admin_kb
        )
        await state.clear()
        await callback.answer()
        return

    success, result_message = add_admin_with_level(user['chat_id'], data)

    level_text = "Super Admin" if data == 'super_admin' else "Admin"

    if success:
        await callback.message.answer(
            f"✅ <b>{level_text} muvaffaqiyatli qo'shildi!</b>\n\n"
            f"👤 {user['name']}\n"
            f"📱 {user['phone']}\n"
            f"👤 @{user['username']}\n"
            f"🆔 {user['chat_id']}\n\n"
            f"📊 Boshqaruv paneli",
            reply_markup=super_admin_kb
        )
    else:
        await callback.message.answer(
            f"❌ <b>Xatolik:</b> {result_message}\n\n"
            "📊 Boshqaruv paneli",
            reply_markup=super_admin_kb
        )

    await state.clear()
    await callback.answer()


@admin_router.message(F.text == "➕ Kitob qo'shish")
async def add_books(message: Message, state: FSMContext):
    await state.clear()

    await state.update_data(book_data={})

    await message.answer(
        "📚 <b>Kitob qo'shish</b>\n\n"
        "Kitob nomini kiriting:\n\n"
        "⚠️ <i>Eslatma: Barcha maydonlarni to'g'ri to'ldiring</i>\n"
        "❌ Bekor qilish uchun: /cancel",
        parse_mode="HTML"
    )
    await state.set_state(BookManagement.waiting_for_title)

@admin_router.message(Command("cancel"))
async def cancel_operation(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state and current_state.startswith("BookManagement"):
        await state.clear()
        await message.answer(
            "❌ <b>Operatsiya bekor qilindi</b>\n\n"
            "📚 Amal to'xtatildi.\n\n"
            "Admin menyu",
            parse_mode="HTML",
            reply_markup=admin_menu_kb
        )
    else:
        await message.answer("❌ Hozirda bekor qilinadigan operatsiya yo'q.")


@admin_router.message(F.text == "📦 Buyurtmalarni boshqarish")
async def manage_orders(message: Message, **kwargs):
    """Show order management menu"""
    orders_data = get_all_orders(page=1, per_page=5)

    if not orders_data['orders']:
        await message.answer(
            "📦 Hozircha buyurtmalar yo'q\n\n"
            "Yangi buyurtmalar kelganda bu yerda ko'rinadi.",
            reply_markup=admin_menu_kb
        )
        return

    response = "📦 Buyurtmalarni boshqarish:\n\n"

    for i, order in enumerate(orders_data['orders'], 1):
        status_emoji = {
            'pending': '⏳',
            'approved': '✅',
            'shipped': '📦',
            'delivered': '🚚',
            'cancelled': '❌'
        }

        emoji = status_emoji.get(order['status'], '❓')
        response += f"{i}. {emoji} Buyurtma #{order['id']}\n"
        response += f"   👤 {order['name']} ({order['phone']})\n"
        response += f"   💰 {order['total_amount']} so'm\n"
        response += f"   📍 {order['delivery_address'][:50]}...\n"
        response += f"   💳 {order['payment_type']}\n"
        response += f"   📅 {order['created_at'][:10]}\n\n"

    response += f"📄 Sahifa {orders_data['current_page']}/{orders_data['total_pages']}"

    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    nav_buttons = []
    if orders_data['current_page'] > 1:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Oldingi",
            callback_data=f"admin_orders_page_{orders_data['current_page'] - 1}"
        ))
    if orders_data['current_page'] < orders_data['total_pages']:
        nav_buttons.append(InlineKeyboardButton(
            text="Keyingi ➡️",
            callback_data=f"admin_orders_page_{orders_data['current_page'] + 1}"
        ))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[nav_buttons] if nav_buttons else [])

    await message.answer(response, reply_markup=keyboard)

@admin_router.callback_query(F.data.startswith("admin_orders_page_"))
async def handle_admin_orders_pagination(callback: CallbackQuery):
    """Handle admin order pagination"""
    try:
        page = int(callback.data.split('_')[3])

        orders_data = get_all_orders(page=page, per_page=5)

        if not orders_data['orders']:
            await callback.answer("❌ Bu sahifada buyurtmalar yo'q")
            return

        response = "📦 Buyurtmalarni boshqarish:\n\n"

        for i, order in enumerate(orders_data['orders'], 1):
            status_emoji = {
                'pending': '⏳',
                'approved': '✅',
                'shipped': '📦',
                'delivered': '🚚',
                'cancelled': '❌'
            }

            emoji = status_emoji.get(order['status'], '❓')
            response += f"{i}. {emoji} Buyurtma #{order['id']}\n"
            response += f"   👤 {order['name']} ({order['phone']})\n"
            response += f"   💰 {order['total_amount']} so'm\n"
            response += f"   📍 {order['delivery_address'][:50]}...\n"
            response += f"   💳 {order['payment_type']}\n"
            response += f"   📅 {order['created_at'][:10]}\n\n"

        response += f"📄 Sahifa {orders_data['current_page']}/{orders_data['total_pages']}"

        nav_buttons = []
        if orders_data['current_page'] > 1:
            nav_buttons.append(InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"admin_orders_page_{orders_data['current_page'] - 1}"
            ))
        if orders_data['current_page'] < orders_data['total_pages']:
            nav_buttons.append(InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"admin_orders_page_{orders_data['current_page'] + 1}"
            ))

        keyboard = InlineKeyboardMarkup(inline_keyboard=[nav_buttons] if nav_buttons else [])

        await callback.message.edit_text(response, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()

    except (ValueError, IndexError) as e:
        await callback.answer("❌ Sahifa raqami noto'g'ri")

@admin_router.message(F.text == "✅ Buyurtmani tasdiqlash")
async def approve_order_handler(message: Message, **kwargs):
    """Approve pending order"""
    orders_data = get_all_orders(page=1, per_page=10)

    pending_orders = [order for order in orders_data['orders'] if order['status'] == 'pending']

    if not pending_orders:
        await message.answer(
            "⏳ Tasdiqlash uchun kutayotgan buyurtmalar yo'q",
            reply_markup=admin_menu_kb
        )
        return

    response = "⏳ Tasdiqlash uchun kutayotgan buyurtmalar:\n\n"

    for i, order in enumerate(pending_orders[:10], 1):
        response += f"{i}. 📦 Buyurtma #{order['id']}\n"
        response += f"   👤 {order['name']} ({order['phone']})\n"
        response += f"   💰 {order['total_amount']} so'm\n"
        response += f"   📍 {order['delivery_address'][:30]}...\n\n"

    response += "Buyurtma ID sini kiriting (faqat raqam):"

    await message.answer(response)

@admin_router.message(F.text == "📦 Buyurtmani jo'natish")
async def ship_order_handler(message: Message, **kwargs):
    """Mark order as shipped"""
    orders_data = get_all_orders(page=1, per_page=10)

    approved_orders = [order for order in orders_data['orders'] if order['status'] == 'approved']

    if not approved_orders:
        await message.answer(
            "✅ Jo'natish uchun tasdiqlangan buyurtmalar yo'q",
            reply_markup=admin_menu_kb
        )
        return

    response = "✅ Jo'natish uchun tayyor buyurtmalar:\n\n"

    for i, order in enumerate(approved_orders[:10], 1):
        response += f"{i}. 📦 Buyurtma #{order['id']}\n"
        response += f"   👤 {order['name']} ({order['phone']})\n"
        response += f"   💰 {order['total_amount']} so'm\n"
        response += f"   📍 {order['delivery_address'][:30]}...\n\n"

    response += "Jo'natilgan buyurtma ID sini kiriting (faqat raqam):"

    await message.answer(response)

@admin_router.message(BookManagement.waiting_for_title)
async def process_book_title(message: Message, state: FSMContext):
    title = message.text.strip()

    if not title or len(title) < 2:
        await message.answer(
            "❌ Kitob nomi kamida 2 ta harfdan iborat bo'lishi kerak!\n\n"
            "Qaytadan kitob nomini kiriting:\n"
            "❌ Bekor qilish: /cancel"
        )
        return

    if len(title) > 100:
        await message.answer(
            "❌ Kitob nomi 100 ta harfdan oshmasligi kerak!\n\n"
            "Qaytadan kitob nomini kiriting:\n"
            "❌ Bekor qilish: /cancel"
        )
        return

    data = await state.get_data()
    book_data = data.get('book_data', {})
    book_data['title'] = title
    await state.update_data(book_data=book_data)

    await message.answer(
        "📝 Kitob tavsifini kiriting (ixtiyoriy):\n\n"
        "Agar tavsif yo'q bo'lsa <b>'skip'</b> deb yozing\n"
        "Maksimal 500 ta harf\n"
        "❌ Bekor qilish: /cancel", parse_mode="HTML"
    )
    await state.set_state(BookManagement.waiting_for_description)

@admin_router.message(F.text == "🙍‍♂️ Foydalanuvchi qismiga otish")
async def go_user(message: Message):
    await message.answer("Userga qaytdingiz adminga qaytish uchun /admin deb yozing", reply_markup=menu_kb)


@admin_router.message(BookManagement.waiting_for_description)
async def process_book_description(message: Message, state: FSMContext):
    description = message.text.strip()

    if description.lower() == 'skip':
        description = None
    elif description and len(description) > 500:
        await message.answer(
            "❌ Tavsif 500 ta harfdan oshmasligi kerak!\n\n"
            "Qaytadan tavsifni kiriting yoki 'skip' deb yozing:\n"
            "❌ Bekor qilish: /cancel"
        )
        return

    data = await state.get_data()
    book_data = data.get('book_data', {})
    book_data['description'] = description
    await state.update_data(book_data=book_data)

    await message.answer("✍️ Muallif nomini kiriting:\n❌ Bekor qilish: /cancel")
    await state.set_state(BookManagement.waiting_for_author)

@admin_router.message(BookManagement.waiting_for_author)
async def process_book_author(message: Message, state: FSMContext):
    author = message.text.strip()

    if not author or len(author) < 2:
        await message.answer(
            "❌ Muallif nomi kamida 2 ta harfdan iborat bo'lishi kerak!\n\n"
            "Qaytadan muallif nomini kiriting:\n"
            "❌ Bekor qilish: /cancel"
        )
        return

    if len(author) > 100:
        await message.answer(
            "❌ Muallif nomi 100 ta harfdan oshmasligi kerak!\n\n"
            "Qaytadan muallif nomini kiriting:\n"
            "❌ Bekor qilish: /cancel"
        )
        return

    data = await state.get_data()
    book_data = data.get('book_data', {})
    book_data['author'] = author
    await state.update_data(book_data=book_data)

    await message.answer("💰 Kitob narxini kiriting (faqat raqam, so'mda):\n❌ Bekor qilish: /cancel")
    await state.set_state(BookManagement.waiting_for_price)

@admin_router.message(BookManagement.waiting_for_price)
async def process_book_price(message: Message, state: FSMContext):
    try:
        price_text = message.text.strip()
        price = int(price_text)

        if price <= 0:
            await message.answer(
                "❌ Narx 0 dan katta bo'lishi kerak!\n\n"
                "Qaytadan narxni kiriting:\n"
                "❌ Bekor qilish: /cancel"
            )
            return

        if price > 100000000:  
            await message.answer(
                "❌ Narx juda katta! Maksimal 100,000,000 so'm\n\n"
                "Qaytadan narxni kiriting:\n"
                "❌ Bekor qilish: /cancel"
            )
            return

    except ValueError:
        await message.answer(
            "❌ Narxni faqat raqam bilan kiriting!\n\n"
            "Masalan: 50000\n\n"
            "Qaytadan narxni kiriting:\n"
            "❌ Bekor qilish: /cancel"
        )
        return

    data = await state.get_data()
    book_data = data.get('book_data', {})
    book_data['price'] = price
    await state.update_data(book_data=book_data)

    await message.answer("📂 Kitob janrini kiriting (masalan: Badiiy, Ilmiy, Darslik):\n❌ Bekor qilish: /cancel")
    await state.set_state(BookManagement.waiting_for_genre)

@admin_router.message(BookManagement.waiting_for_genre)
async def process_book_genre(message: Message, state: FSMContext):
    genre = message.text.strip()

    if not genre or len(genre) < 2:
        await message.answer(
            "❌ Janr nomi kamida 2 ta harfdan iborat bo'lishi kerak!\n\n"
            "Qaytadan janrni kiriting:\n"
            "❌ Bekor qilish: /cancel"
        )
        return

    if len(genre) > 50:
        await message.answer(
            "❌ Janr nomi 50 ta harfdan oshmasligi kerak!\n\n"
            "Qaytadan janrni kiriting:\n"
            "❌ Bekor qilish: /cancel"
        )
        return

    data = await state.get_data()
    book_data = data.get('book_data', {})
    book_data['genre'] = genre
    await state.update_data(book_data=book_data)

    await message.answer("📦 Kitob miqdorini kiriting (faqat raqam):\n❌ Bekor qilish: /cancel")
    await state.set_state(BookManagement.waiting_for_quantity)

@admin_router.message(BookManagement.waiting_for_quantity)
async def process_book_quantity(message: Message, state: FSMContext):
    try:
        quantity_text = message.text.strip()
        quantity = int(quantity_text)

        if quantity <= 0:
            await message.answer(
                "❌ Miqdor 0 dan katta bo'lishi kerak!\n\n"
                "Qaytadan miqdorni kiriting:\n"
                "❌ Bekor qilish: /cancel"
            )
            return

        if quantity > 10000:
            await message.answer(
                "❌ Miqdor juda katta! Maksimal 10,000 ta\n\n"
                "Qaytadan miqdorni kiriting:\n"
                "❌ Bekor qilish: /cancel"
            )
            return

    except ValueError:
        await message.answer(
            "❌ Miqdorni faqat raqam bilan kiriting!\n\n"
            "Masalan: 10\n\n"
            "Qaytadan miqdorni kiriting:\n"
            "❌ Bekor qilish: /cancel"
        )
        return

    data = await state.get_data()
    book_data = data.get('book_data', {})
    book_data['quantity'] = quantity
    await state.update_data(book_data=book_data)

    await message.answer(
        "🖼 <b>Kitob rasmini yuboring</b> (ixtiyoriy):\n\n"
        "📋 <b>Rasm yuborish usullari:</b>\n"
        "• Rasmni albomdan tanlang\n"
        "• Fayl sifatida yuboring\n"
        "• Yoki <b>'skip'</b> deb yozing\n\n"
        "<i>Rasm kitob haqida ko'proq ma'lumot beradi</i>\n"
        "❌ Bekor qilish: /cancel",
        parse_mode="HTML"
    )
    await state.set_state(BookManagement.waiting_for_image)

@admin_router.message(BookManagement.waiting_for_image)
async def process_book_image(message: Message, state: FSMContext):
    image_path = None

    try:
        if message.photo:
            await message.answer("📥 Rasm yuklanmoqda...")

            photo = message.photo[-1]

            image_path = await save_image_from_telegram(message.bot, photo.file_id)

            if image_path and os.path.exists(image_path):
                await message.answer("✅ Rasm muvaffaqiyatli saqlandi!")
            else:
                await message.answer("⚠️ Rasm saqlanmadi, lekin kitob qo'shiladi...")

        elif message.text and message.text.lower() == 'skip':
            await message.answer("ℹ️ Rasm qo'shilmasdan davom etilmoqda...")
        else:
            await message.answer(
                "❌ Iltimos, rasm yuboring yoki <b>'skip'</b> deb yozing:\n\n"
                "📝 <i>Maslahat: Rasm yuborish uchun:</i>\n"
                "1. Qog'oz samolyoqcha belgisini bosing\n"
                "2. Rasmni tanlang\n"
                "3. Yuborish tugmasini bosing\n\n"
                "❌ Bekor qilish: /cancel",
                parse_mode="HTML"
            )
            return

    except Exception as e:
        await message.answer(f"⚠️ Rasm bilan muammo yuz berdi: {e}")
        image_path = None

    data = await state.get_data()
    book_data = data.get('book_data', {})
    book_data['image_path'] = image_path
    await state.update_data(book_data=book_data)

    data = await state.get_data()
    book_data = data.get('book_data', {})

    required_fields = ['title', 'author', 'price', 'genre', 'quantity']
    missing_fields = []

    for field in required_fields:
        if field not in book_data or book_data[field] is None:
            missing_fields.append(field)

    if missing_fields:
        await message.answer(
            f"❌ <b>Ba'zi majburiy maydonlar to'ldirilmagan:</b> {', '.join(missing_fields)}\n\n"
            "Iltimos, /admin buyrug'i bilan qaytadan boshlang.\n\n"
            "Yoki /cancel buyrug'i bilan operatsiyani to'xtating.",
            parse_mode="HTML"
        )
        await state.clear()
        return

    await message.answer("💾 Kitob ma'lumotlar bazasiga saqlanmoqda...")

    try:
        book_id = add_book(
            title=book_data['title'],
            description=book_data.get('description'),
            author=book_data['author'],
            price=book_data['price'],
            genre=book_data['genre'],
            quantity=book_data['quantity'],
            image_path=book_data.get('image_path')
        )

        if book_id:
            response = "✅ <b>Kitob muvaffaqiyatli qo'shildi!</b>\n\n"
            response += "📋 <b>Kitob ma'lumotlari:</b>\n"
            response += f"📖 Nomi: {book_data['title']}\n"
            response += f"✍️ Muallifi: {book_data['author']}\n"
            response += f"💰 Narxi: {book_data['price']:,} so'm\n"
            response += f"📂 Janri: {book_data['genre']}\n"
            response += f"📦 Miqdori: {book_data['quantity']}\n"

            if book_data.get('description'):
                desc = book_data['description'][:50] + "..." if len(book_data['description']) > 50 else book_data['description']
                response += f"📝 Tavsif: {desc}\n"

            if image_path:
                response += "🖼 Rasm: ✅ Yuklandi\n"
            else:
                response += "🖼 Rasm: ❌ Yo'q\n"
            response += f"🆔 ID: <code>{book_id}</code>\n\n"
            response += "🎉 Kitob qo'shish yakunlandi!"
    
            await message.answer(response, parse_mode="HTML", reply_markup=admin_menu_kb)
        else:
            await message.answer(
                "❌ <b>Kitob qo'shishda xatolik yuz berdi!</b>\n\n"
                "Ma'lumotlar bazasi bilan muammo bo'lishi mumkin.\n\n"
                "Iltimos, keyinroq qaytadan urinib ko'ring.\n\n"
                "Yoki /admin buyrug'i bilan qaytadan boshlang.",
                parse_mode="HTML",
                reply_markup=admin_menu_kb
            )
    
    except Exception as e:
        await message.answer(
            f"❌ <b>Xatolik yuz berdi:</b> {e}\n\n"
            "Iltimos, /admin buyrug'i bilan qaytadan boshlang.\n\n"
            "Yoki /cancel buyrug'i bilan operatsiyani to'xtating.",
            parse_mode="HTML",
            reply_markup=admin_menu_kb
        )

    await state.clear()




@admin_router.message(F.text == "📊 Boshqaruv paneli")
async def dashboard_handler(message: Message):
    """Show dashboard with admin management options based on admin level"""
    users_data = get_all_users(page=1, per_page=1000000)
    total_users = users_data['total_count']

    user_id = message.from_user.id

    if is_super_admin(user_id):
        admin_type = "Super Admin"
        keyboard = super_admin_kb
    elif is_regular_admin(user_id):
        admin_type = "Admin"
        keyboard = regular_admin_kb
    else:
        await message.answer("⛔ Sizda admin huquqi yo'q.")
        return

    await message.answer(
        f"📊 <b>Boshqaruv paneli</b>\n"
        f"🏷 <b>Siz:</b> {admin_type}\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {total_users}\n\n"
        f"📋 <b>Kerakli amalni tanlang:</b>",
        reply_markup=keyboard
    )


@admin_router.message(F.text == "⬅️ Orqaga")
async def back_to_dashboard_handler(message: Message):
    """Go back to dashboard"""
    users_data = get_all_users(page=1, per_page=1000000)
    total_users = users_data['total_count']

    user_id = message.from_user.id

    if is_super_admin(user_id):
        admin_type = "Super Admin"
        keyboard = super_admin_kb
    elif is_regular_admin(user_id):
        admin_type = "Admin"
        keyboard = regular_admin_kb
    else:
        await message.answer("⛔ Sizda admin huquqi yo'q.")
        return

    await message.answer(
        f"📊 <b>Boshqaruv paneli</b>\n"
        f"🏷 <b>Siz:</b> {admin_type}\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {total_users}\n\n"
        f"📋 <b>Kerakli amalni tanlang:</b>",
        reply_markup=keyboard
    )


class AdminManagement(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_phone = State()
    waiting_for_admin_level = State()
    waiting_for_admin_removal = State()


@admin_router.message(F.text == "👑 Admin qo'shish")
async def add_admin_handler(message: Message, state: FSMContext):
    """Handle adding new admin (Super Admin only)"""
    user_id = message.from_user.id

    if not is_super_admin(user_id):
        await message.answer(
            "⛔ <b>Bu funksiya faqat Super Admin uchun!</b>\n\n"
            "Siz oddiy admin sifatida yangi admin qo'sha olmaysiz.\n\n"
            "📊 Boshqaruv paneli",
            reply_markup=super_admin_kb if is_super_admin(user_id) else regular_admin_kb
        )
        return

    await state.clear()

    await message.answer(
        "👑 <b>Admin qo'shish (Super Admin)</b>\n\n"
        "🔍 <b>Foydalanuvchi nomini yuboring:</b>\n\n"
        "📝 <i>Namuna: @username yoki username</i>\n\n"
        "⚠️ <i>Foydalanuvchi avval botda ro'yxatdan o'tgan bo'lishi kerak</i>\n"
        "❌ Bekor qilish: /cancel",
        parse_mode="HTML"
    )
    await state.set_state(AdminManagement.waiting_for_user_id)


@admin_router.message(AdminManagement.waiting_for_user_id)
async def process_admin_addition(message: Message, state: FSMContext):
    """Process admin addition request"""
    if message.text and message.text.lower() == '/cancel':
        await state.clear()
        keyboard = super_admin_kb if is_super_admin(message.from_user.id) else regular_admin_kb
        await message.answer(
            "❌ <b>Admin qo'shish bekor qilindi</b>\n\n"
            "📊 Boshqaruv paneli",
            reply_markup=keyboard
        )
        return

    username = message.text.strip()

    if username.startswith('@'):
        username = username[1:]

    user = get_user_by_username(username)

    if not user:
        keyboard = super_admin_kb if is_super_admin(message.from_user.id) else regular_admin_kb
        await message.answer(
            "❌ <b>Foydalanuvchi topilmadi!</b>\n\n"
            "🔍 <b>Qidiruv usullari:</b>\n"
            "• @username\n"
            "• username (faqat nomi)\n\n"
            "📝 <i>Eslatma: Foydalanuvchi avval botda ro'yxatdan o'tgan bo'lishi kerak</i>\n\n"
            "Qaytadan urinib ko'ring yoki /cancel",
            reply_markup=keyboard
        )
        return

    if user.get('is_admin'):
        keyboard = super_admin_kb if is_super_admin(message.from_user.id) else regular_admin_kb
        await message.answer(
            f"⚠️ <b>Foydalanuvchi allaqachon admin!</b>\n\n"
            f"👤 {user['name']}\n"
            f"📱 {user['phone']}\n"
            f"👤 @{user['username']}\n"
            f"🆔 {user['chat_id']}\n\n"
            "📊 Boshqaruv paneli",
            reply_markup=keyboard
        )
        await state.clear()
        return

    await state.update_data(selected_user=user)

    await message.answer(
        f"✅ <b>Foydalanuvchi topildi!</b>\n\n"
        f"👤 {user['name']}\n"
        f"📱 {user['phone']}\n"
        f"👤 @{user['username']}\n"
        f"🆔 {user['chat_id']}\n\n"
        "🏷 <b>Admin darajasini tanlang:</b>",
        parse_mode="HTML",
        reply_markup=admin_level_kb
    )
    await state.set_state(AdminManagement.waiting_for_admin_level)

    await state.clear()


@admin_router.message(F.text == "👥 Foydalanuvchilarni ko'rish")
async def view_all_users_handler(message: Message, **kwargs):
    """Handle viewing all users as PDF"""
    await message.answer("📄 <b>PDF fayl yaratilmoqda...</b>", parse_mode="HTML")

    users_data = get_all_users(page=1, per_page=1000000)

    if not users_data['users']:
        keyboard = super_admin_kb if is_super_admin(message.from_user.id) else regular_admin_kb
        await message.answer(
            "📝 <b>Foydalanuvchilar ro'yxati bo'sh</b>\n\n"
            "Hozircha hech kim ro'yxatdan o'tmagan.\n\n"
            "📊 Boshqaruv paneli",
            reply_markup=keyboard
        )
        return

    print(f"Debug handler: users_data keys: {list(users_data.keys())}")
    if users_data['users']:
        print(f"Debug handler: first user: {users_data['users'][0]}")
        print(f"Debug handler: user keys: {list(users_data['users'][0].keys())}")

    pdf_path = generate_users_pdf(users_data['users'])

    if pdf_path and os.path.exists(pdf_path):
        try:
            keyboard = super_admin_kb if is_super_admin(message.from_user.id) else regular_admin_kb
            await message.bot.send_document(
                chat_id=message.chat.id,
                document=FSInputFile(pdf_path),
                caption=f"👥 Barcha foydalanuvchilar ro'yxati ({users_data['total_count']} ta foydalanuvchi)\n\n📊 Boshqaruv paneli",
                reply_markup=keyboard
            )
        except Exception as e:
            keyboard = super_admin_kb if is_super_admin(message.from_user.id) else regular_admin_kb
            await message.answer(
                f"❌ PDF yuborishda xatolik: {e}\n\n"
                "📊 Boshqaruv paneli",
                reply_markup=keyboard
            )
    else:
        keyboard = super_admin_kb if is_super_admin(message.from_user.id) else regular_admin_kb

        # More detailed error message
        if not REPORTLAB_AVAILABLE:
            await message.answer(
                "❌ <b>PDF yaratishda xatolik yuz berdi!</b>\n\n"
                "📦 <b>Kerakli kutubxona o'rnatilmagan:</b>\n"
                "<code>pip install reportlab</code>\n\n"
                "💡 <b>O'rnatishni tekshiring:</b>\n"
                "<code>python -c 'import reportlab; print(\"ReportLab OK\")'</code>\n\n"
                "📊 Boshqaruv paneli",
                reply_markup=keyboard
            )
        else:
            await message.answer(
                "❌ <b>PDF yaratishda xatolik yuz berdi!</b>\n\n"
                "📝 <b>Muammo:</b> ReportLab kutubxonasi o'rnatilgan lekin PDF yaratib bo'lmadi.\n\n"
                "💡 <b>Admin bilan bog'laning</b>\n\n"
                "📊 Boshqaruv paneli",
                reply_markup=keyboard
            )


@admin_router.message(F.text == "📈 Statistika")
async def statistics_handler(message: Message):
    """Show system statistics"""
    users_data = get_all_users(page=1, per_page=1000000)
    total_users = users_data['total_count']
    active_users = sum(1 for user in users_data['users'] if user['is_active'] == 1)
    admin_users = sum(1 for user in users_data['users'] if user['is_admin'] == 1)

    keyboard = super_admin_kb if is_super_admin(message.from_user.id) else regular_admin_kb

    await message.answer(
        "📈 <b>Sistema statistikasi</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {total_users}\n"
        f"✅ <b>Faol foydalanuvchilar:</b> {active_users}\n"
        f"👑 <b>Admin foydalanuvchilar:</b> {admin_users}\n"
        f"❌ <b>Nofaol foydalanuvchilar:</b> {total_users - active_users}\n\n"
        "📊 Boshqaruv paneli",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@admin_router.message(F.text == "🗑 Admin o'chirish")
async def remove_admin_handler(message: Message, state: FSMContext):
    """Handle removing admin (Super Admin only)"""
    user_id = message.from_user.id

    if not is_super_admin(user_id):
        await message.answer(
            "⛔ <b>Bu funksiya faqat Super Admin uchun!</b>\n\n"
            "Siz oddiy admin sifatida admin o'chira olmaysiz.\n\n"
            "📊 Boshqaruv paneli",
            reply_markup=regular_admin_kb
        )
        return

    await state.clear()

    # Show all admins
    admins = get_all_admins()

    if not admins:
        await message.answer(
            "📝 <b>Adminlar ro'yxati bo'sh</b>\n\n"
            "Hozircha adminlar yo'q.\n\n"
            "📊 Boshqaruv paneli",
            reply_markup=super_admin_kb
        )
        return

    response = "🗑 <b>Admin o'chirish (Super Admin)</b>\n\n"
    response += "Quyidagi adminlardan birini tanlang:\n\n"

    for i, admin in enumerate(admins, 1):
        level_emoji = "👑" if admin['admin_level'] == 'super_admin' else "🏛"
        response += f"{i}. {level_emoji} {admin['name']}\n"
        response += f"   📱 {admin['phone']}\n"
        if admin.get('username') and admin['username'] != 'unknown':
            response += f"   👤 @{admin['username']}\n"
        response += f"   🆔 {admin['chat_id']}\n\n"

    response += "Admin username yoki chat ID sini kiriting:\n"
    response += "❌ Bekor qilish: /cancel"

    await message.answer(response)
    await state.set_state(AdminManagement.waiting_for_admin_removal)


@admin_router.message(AdminManagement.waiting_for_admin_removal)
async def process_admin_removal(message: Message, state: FSMContext):
    """Process admin removal request"""
    if message.text and message.text.lower() == '/cancel':
        await state.clear()
        await message.answer(
            "❌ <b>Admin o'chirish bekor qilindi</b>\n\n"
            "📊 Boshqaruv paneli",
            reply_markup=super_admin_kb
        )
        return

    user_input = message.text.strip()

    # Remove @ symbol if present
    if user_input.startswith('@'):
        user_input = user_input[1:]

    # Try to find admin by username or chat_id
    admin = None
    if user_input.isdigit():
        # Search by chat_id
        admins = get_all_admins()
        admin = next((a for a in admins if str(a['chat_id']) == user_input), None)
    else:
        # Search by username
        admins = get_all_admins()
        admin = next((a for a in admins if a.get('username') == user_input), None)

    if not admin:
        await message.answer(
            "❌ <b>Admin topilmadi!</b>\n\n"
            "Admin username yoki chat ID sini tekshiring.\n\n"
            "Qaytadan urinib ko'ring yoki /cancel"
        )
        return

    if admin['chat_id'] == message.from_user.id:
        await message.answer(
            "❌ <b>O'zingizni admin huquqini olib tashlay olmaysiz!</b>\n\n"
            "📊 Boshqaruv paneli",
            reply_markup=super_admin_kb
        )
        await state.clear()
        return

    success, result_message = remove_admin(admin['chat_id'])

    if success:
        await message.answer(
            f"✅ <b>Admin huquqlari olib tashlandi!</b>\n\n"
            f"👤 {admin['name']}\n"
            f"📱 {admin['phone']}\n"
            f"👤 @{admin['username']}\n"
            f"🆔 {admin['chat_id']}\n\n"
            f"📊 Boshqaruv paneli",
            reply_markup=super_admin_kb
        )
    else:
        await message.answer(
            f"❌ <b>Xatolik:</b> {result_message}\n\n"
            "📊 Boshqaruv paneli",
            reply_markup=super_admin_kb
        )

    await state.clear()


@admin_router.message(F.text == "📈 Oylik hisobot")
async def monthly_report_handler(message: Message):
    """Handle monthly report generation (Super Admin only)"""
    user_id = message.from_user.id

    if not is_super_admin(user_id):
        await message.answer(
            "⛔ <b>Bu funksiya faqat Super Admin uchun!</b>\n\n"
            "Siz oddiy admin sifatida oylik hisobotni kora olmaysiz.\n\n"
            "📊 Boshqaruv paneli",
            reply_markup=regular_admin_kb
        )
        return

    await message.answer("📊 <b>Oylik hisobot tuzilmoqda...</b>", parse_mode="HTML")

    stats = get_monthly_stats()

    if not stats:
        await message.answer(
            "📝 <b>Bu oy uchun ma'lumotlar yo'q</b>\n\n"
            "Hozircha buyurtmalar yo'q.\n\n"
            "📊 Boshqaruv paneli",
            reply_markup=super_admin_kb
        )
        return

    from datetime import datetime
    current_month = datetime.now().strftime("%B %Y")

    response = f"📈 <b>{current_month} oylik hisoboti</b>\n\n"
    response += f"📦 <b>Jami buyurtmalar:</b> {stats['total_orders']}\n"
    response += f"👥 <b>Unikal mijozlar:</b> {stats['unique_customers']}\n"
    response += f"💰 <b>Jami daromad:</b> {stats['total_revenue']:,.0f} so'm\n"
    response += f"📚 <b>Sotilgan kitoblar:</b> {stats['total_items_sold']}\n\n"

    if stats['total_orders'] > 0:
        avg_order = stats['total_revenue'] / stats['total_orders']
        response += f"📊 <b>O'rtacha buyurtma:</b> {avg_order:,.0f} so'm\n"

    response += "📊 Boshqaruv paneli"

    await message.answer(response, parse_mode="HTML", reply_markup=super_admin_kb)


@admin_router.message(F.text == "🔧 Test PDF")
async def test_pdf_handler(message: Message):
    """Test PDF generation (Super Admin only)"""
    user_id = message.from_user.id

    if not is_super_admin(user_id):
        await message.answer(
            "⛔ <b>Bu funksiya faqat Super Admin uchun!</b>",
            reply_markup=regular_admin_kb
        )
        return

    await message.answer("🔧 <b>PDF testini boshlayapman...</b>", parse_mode="HTML")

    try:
        test_users = [
            {
                'id': 1,
                'name': 'Test User',
                'phone': '+998901234567',
                'username': 'testuser',
                'is_active': 1,
                'is_admin': 1,
                'chat_id': 123456789
            }
        ]

        pdf_path = generate_users_pdf(test_users, "test_users.pdf")

        if pdf_path and os.path.exists(pdf_path):
            await message.bot.send_document(
                chat_id=message.chat.id,
                document=FSInputFile(pdf_path),
                caption="✅ PDF test muvaffaqiyatli!"
            )
        else:
            await message.answer(
                "❌ <b>PDF testida xatolik!</b>\n\n"
                "🔍 <b>Tavsiyalar:</b>\n"
                "1. Virtual environment ni aktivlashtiring\n"
                "2. <code>pip install -r requirements.txt</code>\n"
                "3. <code>python -c 'import reportlab; print(\"OK\")'</code>\n\n"
                "📊 Boshqaruv paneli",
                parse_mode="HTML",
                reply_markup=super_admin_kb
            )
    except Exception as e:
        await message.answer(
            f"❌ <b>Test xatoligi:</b> {e}\n\n"
            "📊 Boshqaruv paneli",
            reply_markup=super_admin_kb
        )