from aiogram.types import Message
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command, CommandStart
from buttons import REG_TEXT, GET_NAME
from buttons import user


class Register(StatesGroup):
    name = State()
    phone = State()
    location = State()


user_router = Router()


@user_router.message(CommandStart())
async def start(message: Message):
    await message.answer(REG_TEXT, reply_markup=user.register_kb)


@user_router.message(F.text == "Ro'yxatdan O'tish")
async def get_name(message: Message, state: FSMContext):
    await message.answer(GET_NAME, reply_markup=user.ReplyKeyboardRemove())

@user_router.message(Register.name)
async def get_name(message:Message, state:FSMContext)
		await state.set_data()