from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from buttons import after_menukb, menu_kb, register_kb, re_active_inkb
from database import user_dell_acc, reActive, get_user_by_chat_id

usercall_router = Router()


def check_registration_callback(func):
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        chat_id = callback.from_user.id
        user = get_user_by_chat_id(chat_id)

        if not user:
            await callback.message.answer(
                "❌ Siz ro'yxatdan o'tmagansiz!\n"
                "Iltimos, avval ro'yxatdan o'ting.",
                reply_markup=register_kb
            )
            await callback.answer("Avval ro'yxatdan o'ting")
            return

        if user.get('is_active') == 0:
            await callback.message.answer(
                "🚫 Sizning akkauntingiz to'xtatilgan.\n"
                "Qayta faollashtirmoqchimisiz?",
                reply_markup=re_active_inkb
            )
            await callback.answer("Akkaunt faol emas")
            return

        return await func(callback, *args, **kwargs)
    return wrapper

@usercall_router.callback_query(F.data == "title")
async def get_title(callback: CallbackQuery):
    await callback.message.edit_text("titleni kiriting")
    await callback.answer()

@usercall_router.callback_query(F.data == "genre")
async def genre_handler(callback: CallbackQuery):
    await callback.message.edit_text("Genre kiriting")
    await callback.answer()

@usercall_router.callback_query(F.data == "author")
async def author_handler(callback: CallbackQuery):
    await callback.message.edit_text("Mualiffni kiriting")
    await callback.answer()

@usercall_router.callback_query(F.data == "back")
async def back_handler(callback: CallbackQuery):
    await callback.message.answer("Orqga qaytish", reply_markup=after_menukb)
    await callback.answer()

@usercall_router.callback_query(F.data == "accept")
@check_registration_callback
async def del_account (callback: CallbackQuery):
    chat_id = callback.from_user.id
    if user_dell_acc(chat_id):
        await callback.message.edit_text("Sizning akkountingiz o'chirildi.")
        await callback.message.answer("Botni qayta ishga tushirish uchun /start ni bosing", reply_markup=ReplyKeyboardRemove())
        await callback.answer()
    else:
        await callback.message.answer("Xatolik yuz berdi qayta urinib koring")
        await callback.answer()


@usercall_router.callback_query(F.data == "reActivate")
@check_registration_callback
async def reactive(callback: CallbackQuery):
    chat_id = callback.from_user.id
    if reActive(chat_id):
        await callback.message.edit_text("Sizning Akkauntingiz qayta faolashdi 🎉")
        await callback.message.answer("👋 Xush kelibsiz" ,reply_markup = menu_kb)
        await callback.answer()
    else:
        await callback.message.answer("Xatolik yuz berdi 😢")
        await callback.answer()

@usercall_router.callback_query(F.data == "not")
async def not_handler(callback:CallbackQuery):
    await callback.message.edit_text("""
Yaxshi, akkauntingiz hozircha faol holatga o‘tkazilmadi 🚫\nAgar fikringiz o‘zgarsa, istalgan payt /start ni bosing va qayta faollashtirishingiz mumkin 🙂
""")