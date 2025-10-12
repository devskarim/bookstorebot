from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from buttons import after_menukb, menu_kb, register_kb, re_active_inkb, profile_kb
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
        return await func(callback, *args, **kwargs)
    return wrapper

@usercall_router.callback_query(F.data == "title")
async def get_title(callback: CallbackQuery, **kwargs):
    await callback.message.edit_text("Sarlavha kiriting")
    await callback.answer()

@usercall_router.callback_query(F.data == "genre")
async def genre_handler(callback: CallbackQuery, **kwargs):
    await callback.message.edit_text("Janr kiriting")
    await callback.answer()

@usercall_router.callback_query(F.data == "author")
async def author_handler(callback: CallbackQuery, **kwargs):
    await callback.message.edit_text("Muallif kiriting")
    await callback.answer()

@usercall_router.callback_query(F.data == "back")
async def back_handler(callback: CallbackQuery, **kwargs):
    await callback.message.answer("Asosiy menyu", reply_markup=after_menukb)
    await callback.answer()

@usercall_router.callback_query(F.data == "accept")
@check_registration_callback
async def del_account (callback: CallbackQuery, **kwargs):
    chat_id = callback.from_user.id
    if user_dell_acc(chat_id):
        await callback.message.edit_text("✅ Sizning akkauntingiz to'xtatildi.")
        await callback.message.answer("Botni qayta ishga tushirish uchun /start ni bosing", reply_markup=ReplyKeyboardRemove())
        await callback.answer()
    else:
        await callback.message.answer("❌ Xatolik yuz berdi qayta urinib koring")
        await callback.answer()


@usercall_router.callback_query(F.data == "ignore")
async def cancel_del_account(callback: CallbackQuery, **kwargs):
   await callback.message.edit_text("✅ Account o'chirish bekor qilindi.")
   await callback.message.answer("👤 Profil", reply_markup=profile_kb)
   await callback.answer()


@usercall_router.callback_query(F.data == "reActivate")
@check_registration_callback
async def reactive(callback: CallbackQuery, **kwargs):
    chat_id = callback.from_user.id
    if reActive(chat_id):
        await callback.message.edit_text("Sizning Akkauntingiz qayta faolashdi 🎉")
        await callback.message.answer("👋 Xush kelibsiz" ,reply_markup = menu_kb)
        await callback.answer()
    else:
        await callback.message.answer("Xatolik yuz berdi 😢")
        await callback.answer()

@usercall_router.callback_query(F.data == "not")
async def not_handler(callback:CallbackQuery, **kwargs):
    await callback.message.edit_text("""
Yaxshi, akkauntingiz hozircha faol holatga o'tkazilmadi 🚫\nAgar fikringiz o'zgarsa, istalgan payt /start ni bosing va qayta faollashtirishingiz mumkin 🙂
""")

