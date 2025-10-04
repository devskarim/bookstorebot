from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import FSInputFile
import logging

from buttons import REG_TEXT, GET_NAME, GET_PHONE,ERR_NAME, SUCCES_REG,ALREADY_IN, CAPTION_BOOK
from buttons import register_kb, phoneNumber_kb, menu_kb, after_menukb, send_toAdminkb
from buttons import searchClickkb, all_kb, profile_kb,order_ikb, order_kb,skip_kb,phone_user_kb
from buttons import edit_field_kb, edit_confirm_kb, edit_back_kb, del_account_inkb,re_active_inkb
from buttons import CONTACT_ADMIN
from buttons import reply_toUser

from states import conntact_withAdmin, ContactAdmin
from states import Register, FSMContext, EditStates
from filters import validate_name,validate_uz_phone
from database import save_users, is_register_byChatId, get_userInfo, update_users, user_dell_acc
from database import get_user_by_chat_id
from environs import Env


user_router = Router()
env = Env()
env.read_env()

Admin_ID = env.str("ADMIN_CHATID")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('user_edit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@user_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    chat_id = message.from_user.id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await message.answer(REG_TEXT, reply_markup=register_kb)
        await state.set_state(Register.name)
        await message.answer(GET_NAME, reply_markup=ReplyKeyboardRemove())
        return

    if user['is_active'] is False:
        await message.answer(
            "🚫 Sizning akkauntingiz to‘xtatilgan.\n"
            "Qayta faollashtirmoqchimisiz?",
            reply_markup=re_active_inkb
        )
        return

    photo_path = FSInputFile("imgs/image.png")
    await message.answer_photo(
        photo=photo_path,
        caption=ALREADY_IN,
        reply_markup=menu_kb
    )



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
async def get_phone(message: Message, state: FSMContext):
    phone_input = message.contact.phone_number if message.contact else (message.text or "")
    ok, normalized = validate_uz_phone(phone_input)

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
            "❌ Telefon raqami noto'g'ri. Iltimos, +998901234567 formatida yuboring yoki 'Telefon raqamni yuborish' tugmasidan foydalaning."
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


@user_router.message(F.text == "📄 Ma’lumotlarim")
async def about_handler(message: Message): 
    info = get_userInfo(message.from_user.id)

    if info: 
        await message.answer(
            f"👤 Ism: {info['name']}\n"
            f"📱 Telefon: {info['phone']}\n"
            f"🔗 Username: {info['username'] or 'yo‘q'}\n"
            f"✅ Aktiv: {info['is_active']}"
        )
    else: 
        await message.answer("❌ Siz royxatdan o'tmagansiz.")


@user_router.message(F.text == "✏️ Tahrirlash")
async def start_edit(message: Message, state: FSMContext):
    """Start the edit process by showing current info and field selection"""
    chat_id = message.from_user.id

    try:
        info = get_userInfo(chat_id)
        if not info:
            await message.answer("❌ Siz roʻyxatdan oʻtmagansiz yoki ma'lumot topilmadi.")
            return

        await state.update_data(
            current_info=info,
            edit_data={},
            chat_id=chat_id
        )

        text = (
            "👤 Sizning hozirgi ma'lumotlaringiz:\n\n"
            f"📝 Ism: {info['name']}\n"
            f"📞 Telefon: {info['phone']}\n"
            f"🔗 Username: @{info['username'] if info['username'] else 'yoʻq'}\n\n"
            "Qaysi maydonni tahrirlamoqchisiz? Tanlang:"
        )

        await state.set_state(EditStates.selecting_fields)
        await message.answer(text, reply_markup=edit_field_kb)

        logger.info(f"User {chat_id} started edit process")

    except Exception as e:
        logger.error(f"Error starting edit for user {chat_id}: {e}")
        await message.answer("❌ Xatolik yuz berdi. Keyinroq qayta urinib ko'ring.", reply_markup=menu_kb)

@user_router.message(EditStates.selecting_fields, F.text == "👤 Ism")
async def edit_name_field(message: Message, state: FSMContext):
    """Handle name field editing"""
    await state.set_state(EditStates.waiting_name)
    await message.answer(
        "📝 Yangi ism kiriting:\n\n"
        "⚠️ Diqqat: Ism kamida 2 ta harfdan iborat bo'lishi kerak.\n"
        "❌ Bekor qilish - o'zgarishlarni bekor qilish",
        reply_markup=edit_back_kb
    )

@user_router.message(EditStates.selecting_fields, F.text == "📱 Telefon")
async def edit_phone_field(message: Message, state: FSMContext):
    """Handle phone field editing"""
    await state.set_state(EditStates.waiting_phone)
    await message.answer(
        "📞 Yangi telefon raqam kiriting:\n\n"
        "📱 Tugmani bosing yoki +998901234567 formatida yozing\n"
        "❌ Bekor qilish - o'zgarishlarni bekor qilish",
        reply_markup=edit_back_kb
    )

@user_router.message(EditStates.selecting_fields, F.text == "🔗 Username")
async def edit_username_field(message: Message, state: FSMContext):
    """Handle username field editing"""
    await state.set_state(EditStates.waiting_username)
    await message.answer(
        "🔗 Yangi username kiriting:\n\n"
        "⚠️ Username kamida 3 ta belgidan iborat bo'lishi kerak\n"
        "@ belgisi ixtiyoriy\n"
        "❌ Bekor qilish - o'zgarishlarni bekor qilish",
        reply_markup=edit_back_kb
    )

@user_router.message(EditStates.selecting_fields, F.text == "✏️ Hammasini tahrirlash")
async def edit_all_fields(message: Message, state: FSMContext):
    """Edit all fields in sequence"""
    await state.update_data(editing_all=True)
    await state.set_state(EditStates.waiting_name)
    await message.answer(
        "📝 Barcha maydonlarni tahrirlaymiz. Yangi ism kiriting:\n\n"
        "⚠️ Ism kamida 2 ta harfdan iborat bo'lishi kerak\n"
        "⏭️ Oʻtish - ushbu maydonni o'zgartirmaslik",
        reply_markup=phone_user_kb
    )

@user_router.message(EditStates.selecting_fields, F.text == "✅ Tasdiqlash")
async def confirm_changes(message: Message, state: FSMContext):
    """Show preview and confirm changes"""
    data = await state.get_data()

    if not data.get('edit_data'):
        await message.answer("❌ Hech qanday o'zgarish kiritilmagan.", reply_markup=menu_kb)
        await state.clear()
        return

    current_info = data.get('current_info', {})
    edit_data = data.get('edit_data', {})

    comparison_text = "🔄 O'zgarishlarni tasdiqlaysizmi?\n\n"

    if 'name' in edit_data:
        current = current_info.get('name', 'boʻsh')
        new = edit_data['name'] if edit_data['name'] else 'oʻzgarishsiz'
        comparison_text += f"👤 Ism:\n  Hozirgi: {current}\n  Yangi: {new}\n\n"

    if 'phone' in edit_data:
        current = current_info.get('phone', 'boʻsh')
        new = edit_data['phone'] if edit_data['phone'] else 'oʻzgarishsiz'
        comparison_text += f"📱 Telefon:\n  Hozirgi: {current}\n  Yangi: {new}\n\n"

    if 'username' in edit_data:
        current = current_info.get('username', 'boʻsh')
        current_display = f"@{current}" if current else 'yoʻq'
        new = edit_data['username'] if edit_data['username'] else 'oʻzgarishsiz'
        new_display = f"@{new}" if new != 'oʻzgarishsiz' else new
        comparison_text += f"🔗 Username:\n  Hozirgi: {current_display}\n  Yangi: {new_display}\n\n"

    comparison_text += "✅ Ha, yangilash - o'zgarishlarni saqlash\n❌ Yo'q, bekor qilish - bekor qilish"

    await state.set_state(EditStates.confirming_changes)
    await message.answer(comparison_text, reply_markup=edit_confirm_kb)

@user_router.message(EditStates.selecting_fields, F.text == "❌ Bekor qilish")
async def cancel_edit(message: Message, state: FSMContext):
    """Cancel the entire edit process"""
    await state.clear()
    await message.answer("✖️ Tahrirlash bekor qilindi.", reply_markup=menu_kb)
    logger.info(f"User {message.from_user.id} cancelled edit process")


@user_router.message(EditStates.waiting_name)
async def process_name_edit(message: Message, state: FSMContext):
    """Process name input with validation"""
    text = message.text.strip() if message.text else ""

    if text == "❌ Bekor qilish":
        await cancel_edit(message, state)
        return

    if text == "⬅️ Orqaga":
        data = await state.get_data()
        await state.set_state(EditStates.selecting_fields)
        await message.answer("Maydon tanlang:", reply_markup=edit_field_kb)
        return

    if len(text) < 2:
        await message.answer(
            "❌ Ism juda qisqa. Iltimos, kamida 2 ta harfdan iborat ism kiriting.\n"
            "⬅️ Orqaga - maydon tanlashga qaytish",
            reply_markup=edit_back_kb
        )
        return

    if not validate_name(text):
        await message.answer(
            "❌ Ism faqat harflar va bo'shliqlardan iborat bo'lishi kerak.\n"
            "⬅️ Orqaga - maydon tanlashga qaytish",
            reply_markup=edit_back_kb
        )
        return

    await state.update_data(edit_data={'name': text})

    data = await state.get_data()
    if data.get('editing_all'):
        await state.set_state(EditStates.waiting_phone)
        await message.answer(
            "📱 Endi telefon raqam kiriting (+998901234567 formatida):\n"
            "⏭️ Oʻtish - telefonni o'zgartirmaslik\n"
            "⬅️ Orqaga - oldingi maydonga qaytish",
            reply_markup=phone_user_kb
        )
    else:
        await state.set_state(EditStates.selecting_fields)
        await message.answer("✅ Ism saqlandi. Yana qaysi maydonni tahrirlamoqchisiz?", reply_markup=edit_field_kb)

@user_router.message(EditStates.waiting_phone)
async def process_phone_edit(message: Message, state: FSMContext):
    """Process phone input with validation"""
    text = message.text.strip() if message.text else ""

    if text == "❌ Bekor qilish":
        await cancel_edit(message, state)
        return

    if text == "⬅️ Orqaga":
        data = await state.get_data()
        if data.get('editing_all'):
            await state.set_state(EditStates.waiting_name)
            await message.answer("📝 Ism kiriting:", reply_markup=phone_user_kb)
        else:
            await state.set_state(EditStates.selecting_fields)
            await message.answer("Maydon tanlang:", reply_markup=edit_field_kb)
        return

    if text == "⏭️ Oʻtish":
        phone_value = None
    else:
        phone_input = message.contact.phone_number if message.contact else text
        ok, normalized = validate_uz_phone(str(phone_input))
        if not ok:
            await message.answer(
                "❌ Telefon raqami noto'g'ri. Iltimos, +998901234567 formatida yuboring.\n"
                "⬅️ Orqaga - maydon tanlashga qaytish",
                reply_markup=edit_back_kb
            )
            return
        phone_value = normalized

    current_data = await state.get_data()
    edit_data = current_data.get('edit_data', {})
    edit_data['phone'] = phone_value
    await state.update_data(edit_data=edit_data)

    if current_data.get('editing_all'):
        await state.set_state(EditStates.waiting_username)
        await message.answer(
            "🔗 Endi username kiriting (@ belgisi ixtiyoriy):\n"
            "⏭️ Oʻtish - username o'zgartirmaslik\n"
            "⬅️ Orqaga - oldingi maydonga qaytish",
            reply_markup=skip_kb
        )
    else:
        await state.set_state(EditStates.selecting_fields)
        await message.answer("✅ Telefon saqlandi. Yana qaysi maydonni tahrirlamoqchisiz?", reply_markup=edit_field_kb)

@user_router.message(EditStates.waiting_username)
async def process_username_edit(message: Message, state: FSMContext):
    """Process username input with validation"""
    text = message.text.strip() if message.text else ""

    if text == "❌ Bekor qilish":
        await cancel_edit(message, state)
        return

    if text == "⬅️ Orqaga":
        await state.set_state(EditStates.waiting_phone)
        await message.answer("📱 Telefon raqam kiriting:", reply_markup=phone_user_kb)
        return

    if text == "⏭️ Oʻtish" or text == "":
        username_value = None
    else:
        username = text.lstrip("@")
        if len(username) < 3:
            await message.answer(
                "❌ Username juda qisqa. Iltimos, kamida 3 ta belgidan iborat username kiriting.\n"
                "⬅️ Orqaga - oldingi maydonga qaytish",
                reply_markup=edit_back_kb
            )
            return
        username_value = username

    current_data = await state.get_data()
    edit_data = current_data.get('edit_data', {})
    edit_data['username'] = username_value
    await state.update_data(edit_data=edit_data)

    if current_data.get('editing_all'):
        await confirm_changes(message, state)
    else:
        await state.set_state(EditStates.selecting_fields)
        await message.answer("✅ Username saqlandi. Yana qaysi maydonni tahrirlamoqchisiz?", reply_markup=edit_field_kb)

@user_router.message(EditStates.confirming_changes, F.text == "✅ Ha, yangilash")
async def execute_update(message: Message, state: FSMContext):
    """Execute the actual database update"""
    data = await state.get_data()
    chat_id = data.get('chat_id')
    edit_data = data.get('edit_data', {})

    if not edit_data:
        await message.answer("❌ Hech qanday o'zgarish topilmadi.", reply_markup=menu_kb)
        await state.clear()
        return

    try:
        logger.info(f"Updating user {chat_id} with data: {edit_data}")

        success = update_users(
            chat_id,
            name=edit_data.get('name'),
            phone=edit_data.get('phone'),
            username=edit_data.get('username')
        )

        if success:
            await message.answer(
                "✅ Ma'lumotlar muvaffaqiyatli yangilandi!\n\n"
                "📋 Menyuga qaytish uchun '📋 Menu' ni bosing.",
                reply_markup=menu_kb
            )
            logger.info(f"Successfully updated user {chat_id}")
        else:
            await message.answer(
                "❌ Yangilashda xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.",
                reply_markup=menu_kb
            )
            logger.error(f"Failed to update user {chat_id}")

    except Exception as e:
        logger.error(f"Error updating user {chat_id}: {e}")
        await message.answer(
            "❌ Texnik xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.",
            reply_markup=menu_kb
        )
    finally:
        await state.clear()

@user_router.message(EditStates.confirming_changes, F.text == "❌ Yo'q, bekor qilish")
async def cancel_update(message: Message, state: FSMContext):
    """Cancel the update after confirmation"""
    await state.clear()
    await message.answer("✖️ O'zgarishlar bekor qilindi.", reply_markup=menu_kb)
    logger.info(f"User {message.from_user.id} cancelled update after confirmation")

@user_router.message(EditStates.confirming_changes, F.text == "⬅️ Orqaga")
async def back_to_field_selection(message: Message, state: FSMContext):
    """Go back to field selection from confirmation"""
    await state.set_state(EditStates.selecting_fields)
    await message.answer("Maydon tanlang:", reply_markup=edit_field_kb)

@user_router.message(F.text == "❌ Accountni o‘chirish")
async def delate_user(message: Message): 
    await message.answer("Rostdan ham o'chirmoqchimisz", reply_markup=del_account_inkb) 
