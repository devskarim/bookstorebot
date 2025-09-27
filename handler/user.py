from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Router, F
from aiogram.filters import Command, CommandStart

from buttons import REG_TEXT, GET_NAME, GET_PHONE,ERR_NAME, SUCCES_REG,ALREADY_IN	
from buttons import register_kb, phoneNumber_kb, menu_kb, after_menukb, send_toAdminkb
from buttons import searchClickkb, all_kb
from buttons import CONTACT_ADMIN

from states import Register, FSMContext
from filters import validate_name,validate_phone
from database import save_users, is_register_byChatId 
user_router = Router()

@user_router.message(CommandStart())
async def start(message: Message):
    if is_register_byChatId(message.from_user.id): 
        await message.answer(ALREADY_IN, reply_markup = menu_kb)
        
    else:
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
        data =  await state.get_data()
        
        save_users(
            message.from_user.id,
           	data['name'], 
          	data['phone'], 
            message.from_user.username or None
                        )
        await message.answer(SUCCES_REG, reply_markup=menu_kb)
        await state.clear()
    else: 
        message.answer("❌ Telefon raqam noto‘g‘ri. Iltimos, +998901234567 formatida kiriting.")
        

        
@user_router.message(F.text=="📋 Menu")
async def menu_btn(message:Message, state:FSMContext): 
    await message.answer("📋 Asosiy menyu:",reply_markup=after_menukb)
    

@user_router.message(F.text=="⬅️ Back") 
async def back_menu(message:Message):
    await message.answer("📋 Main menu", reply_markup=menu_kb)
    

@user_router.message(F.text=="📞 Contact") 
async def contact_admin(message:Message): 
    await message.answer("""📩 Savollaringiz bormi?
  Biz har doim yordam berishga tayyormiz!
  Savvolarigizni yozing va Pastagi Yuborish tugmasini bosing""", reply_markup=send_toAdminkb)
  

@user_router.message(F.text=="Yuborish") 
async def send_admin(message:Message): 
    await message.answer(CONTACT_ADMIN, reply_markup=menu_kb)
    

@user_router.message(F.text == "🔎 Search") 
async def search_btn(message:Message): 
    await message.answer("Search By: ", reply_markup=searchClickkb)
    

@user_router.message(F.text== "📚 All") 
async def all_handler(message: Message):
    await message.answer("Barcha kitoblarni ko'rish demo", reply_markup=all_kb) 
    
@user_router.message(F.text=="💸 Discount")
async def discount_handlar(message: Message):
    await message.answer("Diskountdagi kitoblar: (DEMO)") 
    
@user_router.message(F.text=="🆕 New")
async def new_hanler(message: Message): 
    await message.answer("So'ngi kelgan kitoblar. (Demo)") 

@user_router.message(F.text=="⬅️ back") 
async def back_menu(message:Message):
    await message.answer("📋 Main menu", reply_markup=after_menukb)
    