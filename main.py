from aiogram import Bot, Dispatcher
from environs import Env
from handler import start
from buttons.usercallback import usercall_router
from buttons.admin_callback import admin_router as admin_callback_router
import logging
import asyncio

from handler import user_router
from handler.admin import admin_router

dp = Dispatcher()


async def main():
    env = Env()
    env.read_env()
    # bot = Bot(token=env.str("TOKEN"))
    bot = Bot(token="7806379930:AAF1zGcDihe5WoOn47NpNAvtFmp54Abx_DU")
    dp.include_router(usercall_router)
    dp.include_router(user_router)
    dp.include_router(admin_callback_router)
    dp.include_router(admin_router)
    await dp.start_polling(bot)

if __name__ == "__main__": 
    logging.basicConfig(level=logging.INFO) 
    asyncio.run(main()) 



# this is best part for doing anything else now i'm gonna do admin panel 