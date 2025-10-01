from aiogram import Bot, Dispatcher 
from database import env 
from handler import start
from buttons import usercall_router, admin_callback
import logging
import asyncio

from handler import user_router, admin_router

dp = Dispatcher() 


async def main():
    bot = Bot(token=env.str("TOKEN"))
    dp.include_router(usercall_router)
    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.include_router(admin_callback.admin_router)
    await dp.start_polling(bot)

if __name__ == "__main__": 
    logging.basicConfig(level=logging.INFO) 
    asyncio.run(main()) 
