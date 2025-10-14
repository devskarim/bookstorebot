from aiogram import Bot, Dispatcher
from environs import Env
from buttons.usercallback import usercall_router
import logging
import asyncio
import os

from handler.user import user_router
from handler.admin import admin_router
from database.query import setup_super_admin

dp = Dispatcher()


async def main():
    env = Env()
    env.read_env()

    super_admin_chat_id = env.str("ADMIN_CHATID")
    print(f"Setting up super admin with chat_id: {super_admin_chat_id}")
    setup_super_admin(super_admin_chat_id)

    bot_token = env.str("TOKEN") if env.str("TOKEN") != "None" else "7342211516:AAFG6yUhbxLh0StthZhp0XvnAGSxsP-4zlY"
    bot = Bot(token=bot_token)
    print(f"Bot started with token: {bot_token[:20]}...")

    dp.include_router(usercall_router)
    dp.include_router(user_router)
    dp.include_router(admin_router)

    print("Starting bot polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())