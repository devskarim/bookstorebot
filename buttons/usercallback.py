from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from buttons import after_menukb, menu_kb, register_kb
from database import user_dell_acc, reActive

usercall_router = Router()

@usercall_router.callback_query(F.data == "title")
async def get_title(callback: CallbackQuery):
    await callback.message.edit_text("title bo'yicha")
    await callback.answer()

@usercall_router.callback_query(F.data == "genre")
async def genre_handler(callback: CallbackQuery):
    await callback.message.answer("Genre bo'yicha qidirish Demo.")
    await callback.answer()

@usercall_router.callback_query(F.data == "author")
async def author_handler(callback: CallbackQuery):
    await callback.message.answer("Author bo'yicha qidirish Demo.")
    await callback.answer()

@usercall_router.callback_query(F.data == "back")
async def back_handler(callback: CallbackQuery):
    await callback.message.answer("Orqga qaytish", reply_markup=after_menukb)
    await callback.answer()

@usercall_router.callback_query(F.data == "accept")
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
async def reactive(callback: CallbackQuery):
    chat_id = callback.from_user.id
    if reActive(chat_id): 
        await callback.message.edit_text("Sizning Akkauntingiz qayta faolashdi 🎉")
        await callback.message.answer("👋 Xush kelibsiz" ,reply_markup= menu_kb)
        await callback.answer() 
    else: 
        await callback.message.answer("Xatolik yuz berdi 😢")
        await callback.answer() 

@usercall_router.callback_query(F.data == "not")
async def not_handler(callback:CallbackQuery):
    await callback.message.edit_text("""
Yaxshi, akkauntingiz hozircha faol holatga o‘tkazilmadi 🚫\nAgar fikringiz o‘zgarsa, istalgan payt /start ni bosing va qayta faollashtirishingiz mumkin 🙂
""")