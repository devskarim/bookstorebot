from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from buttons import REG_TEXT, GET_NAME, GET_PHONE,ERR_NAME
from buttons import register_kb, phoneNumber_kb
from states import Register, FSMContext
from filters import validate_name,validate_phone



user_router = Router()

@user_router.message(CommandStart())
async def start(message: Message):
    await message.answer(REG_TEXT, reply_markup=register_kb)


@user_router.message(F.text == "Ro'yxatdan O'tish")
async def start(message: Message, state: FSMContext):
    await state.set_state(Register.name)
    await message.answer(GET_NAME, reply_markup=ReplyKeyboardRemove())
    

@user_router.message(Register.name)
async def get_name(message: Message, state: FSMContext):
    name = message.text.strip()  
    
    if validate_name(name):
        await state.update_data(name=name)
        await state.set_state(Register.phone)
        await message.answer(GET_PHONE, reply_markup=phoneNumber_kb)
    else:
        await message.answer(ERR_NAME)


@user_router.message(Register.phone) 
async def get_phone(message:Message, state: FSMContext):
    if message.contact: 
        phone = message.contact.phone_number
    else: 
        phone = message.text.split() 
        
    if validate_phone(phone): 
        await state.update_data(phone=phone)
        await message.answer("✅ Telefon raqamingiz qabul qilindi.",reply_markup=ReplyKeyboardRemove)
    else: 
        message.answer("❌ Telefon raqam noto‘g‘ri. Iltimos, +998901234567 formatida kiriting.")