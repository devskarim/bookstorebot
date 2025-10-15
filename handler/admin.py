from aiogram.types import Message, CallbackQuery
from aiogram import Router, F 
from aiogram.filters import Command, CommandStart 
from database import is_admin
from buttons import adminmenu_kb, menu_kb, reply_toUser
from buttons.book_admin import (
    book_management_kb, confirm_add_kb, confirm_edit_kb, confirm_delete_kb,
    book_selection_kb, edit_field_kb, book_view_kb, genre_selection_kb,
    search_options_kb, back_to_book_menu_kb
)
from environs import Env
from aiogram.fsm.context import FSMContext
from datetime import datetime
from states.book_management import BookManagement
from database.admin_query import (
    add_book, get_all_books, get_book_by_id, update_book, delete_book,
    search_books, get_books_by_genre, get_book_stats
)
from utils.pdf_generator import generate_books_pdf
import os


admin_router = Router()

env = Env()
env.read_env()

Admin_ID = env.str("ADMIN_CHATID")

from shared import admin_reply_target

@admin_router.message(Command("admin"))
async def admin_handler(message: Message):
	if is_admin(message.from_user.id) or message.from_user.id == int(Admin_ID):
		await message.answer("Admin menyu", reply_markup=adminmenu_kb)
	else:
		await message.answer("⛔ Sizda admin huquqi yo'q.")


@admin_router.message(Command("user")) 
async def get_user(message:Message): 
	await message.answer("Foydalanuvchi rejimiga qaytildi", reply_markup=menu_kb)


@admin_router.message(F.text, lambda m: m.from_user.id == int(Admin_ID) and "reply_to" in admin_reply_target)
async def handle_admin_reply(message: Message):
    """Handle admin reply when reply_to target is set"""
    try:
        target_user_id = admin_reply_target["reply_to"]

        await message.bot.send_message(
            target_user_id,
            f"📩 Admin javobi:\n\n{message.text}"
        )
        await message.answer("✅ Javob foydalanuvchiga yuborildi.")
        # Clean up the reply target after successful send
        if "reply_to" in admin_reply_target:
            del admin_reply_target["reply_to"]
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {e}")
        # Clean up on error too
        if "reply_to" in admin_reply_target:
            del admin_reply_target["reply_to"]


@admin_router.message(F.reply_to_message, lambda m: m.from_user.id == Admin_ID)
async def reply_to_user(message: Message):
    """Handle admin reply to forwarded user messages"""
    replied = message.reply_to_message

    if replied and "UserID:" in replied.text:
        try:
            user_id = int(replied.text.split("UserID:")[1].split("\n")[0])

            await message.bot.send_message(
                user_id,
                f"📩 Admin javobi:\n\n{message.text}"
            )
            await message.answer("✅ Javob foydalanuvchiga yuborildi.")
        except (ValueError, IndexError) as e:
            await message.answer(f"⚠️ Xatolik: Foydalanuvchi ID topilmadi. {e}")
        except Exception as e:
            await message.answer(f"⚠️ Xatolik: {e}")


@admin_router.message(F.text  == "🛒 Buyurtmalar")
async def orders_handler(message: Message):
    await message.answer("Qurilishda...")


@admin_router.message(F.text == "📚 Kitoblar")
async def books_handler(message: Message):
    await message.answer("📚 Kitob boshqaruvi", reply_markup=book_management_kb)


@admin_router.message(F.text == "� Boshqaruv paneli")
async def dashboard_handler(message: Message): 
     await message.answer("Qurilishda..")

@admin_router.message(F.text == "⬅️ Ortga")
async def back_handler(message: Message):
    await message.answer("Asosiy menyu", reply_markup=menu_kb)


@admin_router.message(F.text == "❌ Bekor qilish", lambda m: m.from_user.id == int(Admin_ID))
async def cancel_reply_handler(message: Message):
    """Cancel admin reply mode"""
    if "reply_to" in admin_reply_target:
        del admin_reply_target["reply_to"]
        await message.answer("✅ Javob rejimi bekor qilindi.")
    else:
        await message.answer("❌ Javob rejimi faol emas.")


# ==================== BOOK MANAGEMENT HANDLERS ====================

@admin_router.message(F.text == "📚 Kitob qo'shish")
async def add_book_handler(message: Message, state: FSMContext):
    """Start adding a new book"""
    await state.set_state(BookManagement.waiting_title)
    await message.answer(
        "📚 Yangi kitob qo'shish\n\nKitob sarlavhasini kiriting:",
        reply_markup=back_to_book_menu_kb
    )


@admin_router.message(BookManagement.waiting_title)
async def get_book_title(message: Message, state: FSMContext):
    """Get book title and ask for author"""
    await state.update_data(title=message.text.strip())
    await state.set_state(BookManagement.waiting_author)
    await message.answer("✍️ Muallif nomini kiriting:", reply_markup=back_to_book_menu_kb)


@admin_router.message(BookManagement.waiting_author)
async def get_book_author(message: Message, state: FSMContext):
    """Get book author and ask for price"""
    await state.update_data(author=message.text.strip())
    await state.set_state(BookManagement.waiting_price)
    await message.answer("💰 Kitob narxini kiriting (faqat raqam):", reply_markup=back_to_book_menu_kb)


@admin_router.message(BookManagement.waiting_price)
async def get_book_price(message: Message, state: FSMContext):
    """Get book price and ask for description"""
    try:
        price = int(message.text.strip())
        await state.update_data(price=price)
        await state.set_state(BookManagement.waiting_description)
        await message.answer("📝 Kitob tavsifini kiriting (ixtiyoriy, 'skip' deb yozing):", reply_markup=back_to_book_menu_kb)
    except ValueError:
        await message.answer("❌ Narx noto'g'ri formatda. Faqat raqam kiriting:", reply_markup=back_to_book_menu_kb)


@admin_router.message(BookManagement.waiting_description)
async def get_book_description(message: Message, state: FSMContext):
    """Get book description and ask for genre"""
    desc = message.text.strip()
    if desc.lower() != 'skip':
        await state.update_data(description=desc)
    await state.set_state(BookManagement.waiting_genre)
    await message.answer("🏷️ Kitob janrini tanlang:", reply_markup=genre_selection_kb)


@admin_router.message(BookManagement.waiting_genre)
async def get_book_genre(message: Message, state: FSMContext):
    """Get book genre and ask for quantity"""
    genre = message.text.strip()
    if genre in ["📚 Badiiy", "🎓 Ilmiy", "👶 Bolalar", "💼 Biznes", "📰 Publitsistika", "📖 Chet til"]:
        await state.update_data(genre=genre)
        await state.set_state(BookManagement.waiting_quantity)
        await message.answer("📦 Kitob miqdorini kiriting (faqat raqam, 0 agar mavjud emas):", reply_markup=back_to_book_menu_kb)
    elif genre == "❌ O'tkazib yuborish":
        await state.update_data(genre="unknown")
        await state.set_state(BookManagement.waiting_quantity)
        await message.answer("📦 Kitob miqdorini kiriting (faqat raqam, 0 agar mavjud emas):", reply_markup=back_to_book_menu_kb)
    else:
        await message.answer("❌ Noto'g'ri janr. Iltimos, tugmani bosing:", reply_markup=genre_selection_kb)


@admin_router.message(BookManagement.waiting_quantity)
async def get_book_quantity(message: Message, state: FSMContext):
    """Get book quantity and confirm adding"""
    try:
        quantity = int(message.text.strip())
        await state.update_data(quantity=quantity)

        # Get all book data
        book_data = await state.get_data()

        # Show confirmation
        confirmation_text = f"""
📚 Kitob qo'shishni tasdiqlang:

📖 Sarlavha: {book_data['title']}
✍️ Muallif: {book_data['author']}
💰 Narx: {book_data['price']} so'm
📝 Tavsif: {book_data.get('description', 'Kiritilmagan')}
🏷️ Janr: {book_data.get('genre', 'unknown')}
📦 Miqdor: {quantity}

Qo'shishni tasdiqlaysizmi?
        """

        await state.set_state(BookManagement.confirming_add)
        await message.answer(confirmation_text, reply_markup=confirm_add_kb)

    except ValueError:
        await message.answer("❌ Miqdor noto'g'ri formatda. Faqat raqam kiriting:", reply_markup=back_to_book_menu_kb)


@admin_router.callback_query(F.data == "confirm_add_book", BookManagement.confirming_add)
async def confirm_add_book_handler(callback: CallbackQuery, state: FSMContext):
    """Confirm and add the book"""
    book_data = await state.get_data()

    # Add book to database
    book_id = add_book(
        title=book_data['title'],
        author=book_data['author'],
        price=book_data['price'],
        description=book_data.get('description'),
        genre=book_data.get('genre', 'unknown'),
        quantity=book_data['quantity']
    )

    if book_id:
        await callback.message.edit_text(f"✅ Kitob muvaffaqiyatli qo'shildi! (ID: {book_id})")
        await state.clear()
    else:
        await callback.message.edit_text("❌ Kitob qo'shishda xatolik yuz berdi.")

    await callback.answer()


@admin_router.callback_query(F.data == "cancel_add_book")
async def cancel_add_book_handler(callback: CallbackQuery, state: FSMContext):
    """Cancel adding book"""
    await state.clear()
    await callback.message.edit_text("❌ Kitob qo'shish bekor qilindi.")
    await callback.answer()


@admin_router.message(F.text == "📖 Kitoblarni ko'rish")
async def view_books_handler(message: Message, state: FSMContext):
    """View all books in PDF format"""
    await message.answer("📄 PDF fayl yaratilmoqda...")

    books = get_all_books()

    if not books:
        await message.answer("📚 Hozircha kitoblar yo'q.")
        return

    try:
        # Generate PDF
        filename = f"books_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = generate_books_pdf(books, filename)

        if pdf_path and os.path.exists(pdf_path):
            # Send PDF file
            from aiogram.types import FSInputFile
            pdf_file = FSInputFile(pdf_path)

            await message.answer_document(
                pdf_file,
                caption=f"📚 Jami {len(books)} ta kitob"
            )

            # Clean up - delete the temporary file
            try:
                os.remove(pdf_path)
            except:
                pass
        else:
            await message.answer("❌ PDF yaratishda xatolik yuz berdi.")

    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

    await state.clear()


@admin_router.message(F.text == "✏️ Kitob tahrirlash")
async def edit_book_handler(message: Message, state: FSMContext):
    """Start editing a book"""
    books = get_all_books()

    if not books:
        await message.answer("❌ Tahrirlanadigan kitoblar topilmadi.")
        return

    await state.set_state(BookManagement.selecting_book)
    await message.answer("✏️ Qaysi kitobni tahrirlamoqchisiz?", reply_markup=book_selection_kb(books, "edit"))


@admin_router.callback_query(F.data.startswith("edit_book_"), BookManagement.selecting_book)
async def select_edit_book_handler(callback: CallbackQuery, state: FSMContext):
    """Select book to edit"""
    try:
        book_id = int(callback.data.split("_")[2])
        book = get_book_by_id(book_id)

        if book:
            await state.update_data(edit_book_id=book_id)
            await state.set_state(BookManagement.selecting_field)

            book_info = f"""
📖 Tahrirlanayotgan kitob:

📚 {book['title']}
✍️ {book['author']}
💰 {book['price']} so'm
📝 {book['description'] or 'Tavsif yo\'q'}
🏷️ {book['genre']}
📦 {book['quantity']} dona

Qaysi maydonni tahrirlamoqchisiz?
            """

            await callback.message.edit_text(book_info, reply_markup=edit_field_kb)
        else:
            await callback.message.edit_text("❌ Kitob topilmadi.")
    except (ValueError, IndexError):
        await callback.message.edit_text("❌ Noto'g'ri kitob ID.")

    await callback.answer()


@admin_router.callback_query(F.data.startswith("edit_"), BookManagement.selecting_field)
async def edit_field_handler(callback: CallbackQuery, state: FSMContext):
    """Handle field selection for editing"""
    field = callback.data.replace("edit_", "")

    field_names = {
        "title": "sarlavha",
        "author": "muallif",
        "price": "narx",
        "description": "tavsif",
        "genre": "janr",
        "quantity": "miqdor"
    }

    field_uz = field_names.get(field, field)
    await state.update_data(edit_field=field)
    await state.set_state(BookManagement.waiting_edit_title)

    await callback.message.edit_text(f"📝 Yangi {field_uz}ni kiriting:")
    await callback.answer()


@admin_router.message(BookManagement.waiting_edit_title)
async def get_edit_value_handler(message: Message, state: FSMContext):
    """Get the new value for the field being edited"""
    user_data = await state.get_data()
    field = user_data.get('edit_field')
    book_id = user_data.get('edit_book_id')

    # Update the book
    update_data = {}
    if field == "title":
        update_data['title'] = message.text.strip()
    elif field == "author":
        update_data['author'] = message.text.strip()
    elif field == "price":
        try:
            update_data['price'] = int(message.text.strip())
        except ValueError:
            await message.answer("❌ Narx noto'g'ri formatda. Faqat raqam kiriting:", reply_markup=back_to_book_menu_kb)
            return
    elif field == "description":
        update_data['description'] = message.text.strip()
    elif field == "genre":
        update_data['genre'] = message.text.strip()
    elif field == "quantity":
        try:
            update_data['quantity'] = int(message.text.strip())
        except ValueError:
            await message.answer("❌ Miqdor noto'g'ri formatda. Faqat raqam kiriting:", reply_markup=back_to_book_menu_kb)
            return

    # Update in database
    if update_book(book_id, **update_data):
        await state.set_state(BookManagement.confirming_edit)
        await message.answer("✅ Kitob muvaffaqiyatli yangilandi!", reply_markup=confirm_edit_kb)
    else:
        await message.answer("❌ Yangilanishda xatolik yuz berdi.", reply_markup=back_to_book_menu_kb)


@admin_router.callback_query(F.data == "confirm_edit_book")
async def confirm_edit_book_handler(callback: CallbackQuery, state: FSMContext):
    """Confirm edit completion"""
    await state.clear()
    await callback.message.edit_text("✏️ Tahrirlanish yakunlandi.")
    await callback.answer()


@admin_router.callback_query(F.data == "cancel_edit_book")
async def cancel_edit_book_handler(callback: CallbackQuery, state: FSMContext):
    """Cancel edit operation"""
    await state.clear()
    await callback.message.edit_text("❌ Tahrirlanish bekor qilindi.")
    await callback.answer()


@admin_router.message(F.text == "🗑️ Kitob o'chirish")
async def delete_book_handler(message: Message, state: FSMContext):
    """Start deleting a book"""
    books = get_all_books()

    if not books:
        await message.answer("❌ O'chiriladigan kitoblar topilmadi.")
        return

    await state.set_state(BookManagement.deleting_book)
    await message.answer("🗑️ Qaysi kitobni o'chirmoqchisiz?", reply_markup=book_selection_kb(books, "delete"))


@admin_router.callback_query(F.data.startswith("delete_book_"), BookManagement.deleting_book)
async def select_delete_book_handler(callback: CallbackQuery, state: FSMContext):
    """Select book to delete"""
    try:
        book_id = int(callback.data.split("_")[2])
        book = get_book_by_id(book_id)

        if book:
            await state.update_data(delete_book_id=book_id)
            await state.set_state(BookManagement.confirming_delete)

            confirmation_text = f"""
🗑️ Kitob o'chirishni tasdiqlang:

📖 {book['title']}
✍️ {book['author']}
💰 {book['price']} so'm

Bu amalni ortga qaytarib bo'lmaydi!
            """

            await callback.message.edit_text(confirmation_text, reply_markup=confirm_delete_kb)
        else:
            await callback.message.edit_text("❌ Kitob topilmadi.")
    except (ValueError, IndexError):
        await callback.message.edit_text("❌ Noto'g'ri kitob ID.")

    await callback.answer()


@admin_router.callback_query(F.data == "confirm_delete_book", BookManagement.confirming_delete)
async def confirm_delete_book_handler(callback: CallbackQuery, state: FSMContext):
    """Confirm and delete the book"""
    user_data = await state.get_data()
    book_id = user_data.get('delete_book_id')

    if delete_book(book_id):
        await callback.message.edit_text("🗑️ Kitob muvaffaqiyatli o'chirildi.")
    else:
        await callback.message.edit_text("❌ Kitob o'chirishda xatolik yuz berdi.")

    await state.clear()
    await callback.answer()


@admin_router.callback_query(F.data == "cancel_delete_book")
async def cancel_delete_book_handler(callback: CallbackQuery, state: FSMContext):
    """Cancel delete operation"""
    await state.clear()
    await callback.message.edit_text("❌ O'chirish bekor qilindi.")
    await callback.answer()


@admin_router.message(F.text == "🔍 Kitob qidirish")
async def search_books_handler(message: Message, state: FSMContext):
    """Start book search"""
    await state.set_state(BookManagement.waiting_search)
    await message.answer("🔍 Qidiruv turini tanlang:", reply_markup=search_options_kb)


@admin_router.message(F.text.in_(["🔍 Sarlavha bo'yicha", "👤 Muallif bo'yicha", "🏷️ Janr bo'yicha", "💰 Narx oralig'i"]))
async def get_search_type_handler(message: Message, state: FSMContext):
    """Get search type and ask for search term"""
    search_type = message.text
    await state.update_data(search_type=search_type)
    await state.set_state(BookManagement.searching_books)

    if search_type == "💰 Narx oralig'i":
        await message.answer("💰 Qidiruv uchun narx oralig'ini kiriting (masalan: 50000-100000):")
    else:
        search_prompts = {
            "🔍 Sarlavha bo'yicha": "📖 Kitob sarlavhasini kiriting:",
            "👤 Muallif bo'yicha": "✍️ Muallif nomini kiriting:",
            "🏷️ Janr bo'yicha": "🏷️ Janr nomini kiriting:"
        }
        await message.answer(search_prompts[search_type])


@admin_router.message(BookManagement.searching_books)
async def perform_search_handler(message: Message, state: FSMContext):
    """Perform the search"""
    user_data = await state.get_data()
    search_type = user_data.get('search_type')
    search_term = message.text.strip()

    books = []

    if search_type == "💰 Narx oralig'i":
        try:
            min_price, max_price = search_term.split('-')
            # This would need a custom query for price range
            books = []  # Placeholder for price range search
        except ValueError:
            await message.answer("❌ Narx oralig'i noto'g'ri formatda. Masalan: 50000-100000", reply_markup=back_to_book_menu_kb)
            return
    else:
        books = search_books(search_term)

    if books:
        books_text = f"🔍 '{search_term}' bo'yicha topilgan kitoblar:\n\n"
        for i, book in enumerate(books[:10], 1):
            books_text += f"{i}. 📖 {book['title']}\n   ✍️ {book['author']}\n   💰 {book['price']} so'm\n\n"

        await message.answer(books_text, reply_markup=back_to_book_menu_kb)
    else:
        await message.answer(f"❌ '{search_term}' bo'yicha hech narsa topilmadi.", reply_markup=back_to_book_menu_kb)

    await state.clear()


@admin_router.message(F.text == "📊 Statistika")
async def book_stats_handler(message: Message):
    """Show book statistics"""
    stats = get_book_stats()

    if stats:
        stats_text = f"""
📊 Kitob statistikasi:

📚 Jami kitoblar: {stats['total_books']}
📦 Jami miqdor: {stats['total_quantity']}
💰 O'rtacha narx: {stats['average_price']} so'm
🏷️ Noyob janrlar: {stats['unique_genres']}
        """
        await message.answer(stats_text)
    else:
        await message.answer("❌ Statistika olishda xatolik yuz berdi.")


@admin_router.message(F.text == "⬅️ Ortga")
async def back_to_main_menu_handler(message: Message, state: FSMContext):
    """Go back to main admin menu"""
    await state.clear()
    await message.answer("Asosiy menyu", reply_markup=adminmenu_kb)


@admin_router.message(F.text == "❌ Bekor qilish")
async def cancel_book_operation_handler(message: Message, state: FSMContext):
    """Cancel any book operation"""
    current_state = await state.get_state()
    if current_state and "book_management" in current_state:
        await state.clear()
        await message.answer("✅ Bekor qilindi. Kitob boshqaruviga qaytildi.", reply_markup=book_management_kb)
    else:
        await message.answer("❌ Bekor qilish uchun hech narsa yo'q.")


@admin_router.message(F.text == "❌ O'tkazib yuborish", BookManagement.waiting_genre)
async def skip_genre_handler(message: Message, state: FSMContext):
    """Skip genre selection"""
    await state.update_data(genre="unknown")
    await state.set_state(BookManagement.waiting_quantity)
    await message.answer("📦 Kitob miqdorini kiriting (faqat raqam, 0 agar mavjud emas):", reply_markup=back_to_book_menu_kb)


@admin_router.callback_query(F.data == "back_to_book_management")
async def back_to_book_management_handler(callback: CallbackQuery, state: FSMContext):
    """Go back to book management menu"""
    await state.clear()
    await callback.message.edit_text("📚 Kitob boshqaruvi", reply_markup=book_management_kb)
    await callback.answer()