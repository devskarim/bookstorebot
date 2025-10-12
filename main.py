from aiogram import Bot, Dispatcher
from environs import Env
from handler import start
from buttons.usercallback import usercall_router
from buttons.admin_callback import admin_router
import logging
import asyncio

from handler import user_router, admin_router

dp = Dispatcher()


async def main():
    env = Env()
    env.read_env()
    bot = Bot(token=env.str("TOKEN"))
    dp.include_router(usercall_router)
    dp.include_router(user_router)
    dp.include_router(admin_router)
    await dp.start_polling(bot)

if __name__ == "__main__": 
    logging.basicConfig(level=logging.INFO) 
    asyncio.run(main()) 



