from aiogram import Bot, Dispatcher,F
from aiogram.types import Message, ReplyKeyboardRemove
from environs import Env
from buttons.usercallback import usercall_router
from buttons.admin_callback import admin_router as admin_callback_router
import logging
import asyncio
import os

from handler import user_router
from handler.admin import admin_router

dp = Dispatcher()


UNDER_UPGRADE = True


@dp.message(F.text)
async def always_reply_upgrade(message: Message):
    if UNDER_UPGRADE:
        await message.answer("🔧 Bot is under upgrade. Please restart again later.", reply_markup=ReplyKeyboardRemove())
        return

    await message.answer("Bot normal ishlayapti.")

async def main():
    env = Env()
    env.read_env()
    bot = Bot(token=env.str("TOKEN"))
    dp.include_router(usercall_router)
    dp.include_router(user_router)
    dp.include_router(admin_callback_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())