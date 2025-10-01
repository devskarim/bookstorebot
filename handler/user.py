from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import FSInputFile

from buttons import REG_TEXT, GET_NAME, GET_PHONE,ERR_NAME, SUCCES_REG,ALREADY_IN, CAPTION_BOOK
from buttons import register_kb, phoneNumber_kb, menu_kb, after_menukb, send_toAdminkb
from buttons import searchClickkb, all_kb, profile_kb,order_ikb, order_kb
from buttons import CONTACT_ADMIN
from buttons import reply_toUser

from states import conntact_withAdmin, ContactAdmin
from states import Register, FSMContext
from filters import validate_name,validate_uz_phone
from database import save_users, is_register_byChatId
from environs import Env 


user_router = Router()
env = Env()
env.read_env()

Admin_ID = env.str("ADMIN_CHATID")

@user_router.message(CommandStart())
async def start(message: Message):
    if is_register_byChatId(message.from_user.id): 
        photo_path  = FSInputFile("imgs/image.png")
        await message.answer_photo(photo=photo_path, caption=ALREADY_IN, reply_markup=menu_kb)        
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
    phone = message.contact.phone_number  
    ok, normalized = validate_uz_phone(phone)

    if ok:
        await state.update_data(phone=normalized)
        data = await state.get_data()

        save_users(
            message.from_user.id,
            data['name'],
            data['phone'],
            message.from_user.username or None
        )
        await message.answer(SUCCES_REG, reply_markup=menu_kb)
        await state.clear()
    else:
        await message.answer(
            "❌ Telefon raqami noto'g'ri. Iltimos, +998901234567 formatida yuboring."
        )
        

        
@user_router.message(F.text=="📋 Menu")
async def menu_btn(message:Message, state:FSMContext): 
    await message.answer("📋 Asosiy menyu:",reply_markup=after_menukb)
    

@user_router.message(F.text=="⬅️ Back")
async def back_menu(message:Message):
    await message.answer("📋 Asosiy menyu", reply_markup=menu_kb)
    

@user_router.message(F.text=="📞 Contact")
async def contact_admin(message:Message, state: FSMContext):
    await state.set_state(ContactAdmin.user_waiting_massage)
    await message.answer("""📩 Savollaringiz bormi?
  Biz har doim yordam berishga tayyormiz!
  Savvolarigizni yozing va Pastagi Yuborish tugmasini bosing""", reply_markup=send_toAdminkb)


@user_router.message(ContactAdmin.user_waiting_massage, F.text == "❌ Bekor qilish")
async def cancel_contact(message:Message, state: FSMContext):
    await state.clear()
    await message.answer("Bosh menu", reply_markup=menu_kb)


user_messages = {}

@user_router.message(ContactAdmin.user_waiting_massage, F.text.not_in(["📤 Yuborish", "❌ Bekor qilish"]))
async def get_user_message(message: Message):
    user_messages[message.from_user.id] = message.text
    await message.answer("✅ Xabaringiz saqlandi. Endi 📤 Yuborish tugmasini bosing.")



@user_router.message(ContactAdmin.user_waiting_massage, F.text=="📤 Yuborish")
async def send_toAdmin(message:Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_messages:
        text = user_messages[user_id]
        await message.bot.send_message(
            Admin_ID,
            f"Yangi Xabar\n\n👤 User: {message.from_user.full_name}(@{message.from_user.username})\nUserID: {user_id}\n\n ✉️ Xabar:\n{text}",
            reply_markup=reply_toUser(user_id)
        )
        await message.answer("✅ Xabaringiz adminga yuborildi.", reply_markup=menu_kb)
        del user_messages[user_id]
        await state.clear()
    else:
        await message.answer("⚠️ Avval xabar yozing.")


@user_router.message(F.text == "👤 Profil") 
async def my_profile(message: Message): 
    await message.answer("👤 Profil", reply_markup=profile_kb)

    

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
    await message.answer("📋 Asosiy menyu", reply_markup=after_menukb)
    

@user_router.message(F.text=="🛒 Order")
async def order_handler(message:Message):
    photo_path = FSInputFile("imgs/image2.png")
    await message.answer("Sizning burutmalaringiz yuklanmoqda...", reply_markup=order_kb)
    await message.answer_photo(photo=photo_path, caption=CAPTION_BOOK, reply_markup=order_ikb)