from aiogram.types import Message
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from buttons import REG_TEXT, GET_NAME, GET_PHONE
from buttons import user

from states import Register, FSMContext
from filters import validate_name,validate_phone



user_router = Router()

@user_router.message(CommandStart())
async def start(message: Message):
    await message.answer(REG_TEXT, reply_markup=user.register_kb)


@user_router.message(F.text == "Ro'yxatdan O'tish")
async def start(message: Message, state: FSMContext):
    await state.set_state(Register.name)
    await message.answer(GET_NAME, reply_markup=user.ReplyKeyboardRemove())


@user_router.message(Register.name) 
async def get_name(message:Message, state:FSMContext):
		if validate_name(message.text): 
				await state.update_data(name = message.text) 
				await state.set_state(Register.phone)
        
				await message.text(GET_PHONE, reply_markup = user.phoneNumber_kb)