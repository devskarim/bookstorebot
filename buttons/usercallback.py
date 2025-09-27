from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from buttons import after_menukb

usercall_router = Router()

@usercall_router.callback_query(F.data == "title")
async def get_title(callback: CallbackQuery):
    await callback.message.answer("Title bo'yicha qidirish Demo.")
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
