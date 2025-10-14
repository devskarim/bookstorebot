from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import FSInputFile, CallbackQuery, InputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import logging

from buttons import REG_TEXT, GET_PHONE,ERR_NAME, SUCCES_REG,ALREADY_IN, CAPTION_BOOK, menu_kb
from buttons import register_kb, phoneNumber_kb, menu_kb, after_menukb, send_toAdminkb
from buttons import searchClickkb, all_kb, profile_kb,order_ikb, order_kb,skip_kb,phone_user_kb
from buttons.user import searchClickkb
from buttons import edit_field_kb, edit_confirm_kb, edit_back_kb, del_account_inkb, re_active_inkb
from buttons import CONTACT_ADMIN
from buttons import reply_toUser

from states import conntact_withAdmin, ContactAdmin, Register, FSMContext, EditStates
from states.book_management import BookSearch, OrderProcess, CartManagement
from filters import validate_name,validate_uz_phone
from database import save_users, is_register_byChatId, get_userInfo, update_users, user_dell_acc
from database import get_user_by_chat_id
from database.admin_query import get_books_paginated, create_pagination_keyboard, add_to_cart, get_user_cart, remove_from_cart, clear_user_cart, create_order, get_user_orders, get_order_details


def check_registration(func):
    async def wrapper(message: Message, *args, **kwargs):
        chat_id = message.from_user.id
        user = get_user_by_chat_id(chat_id)

        if not user:
            await message.answer(
                "❌ Siz ro'yxatdan o'tmagansiz!\n"
                "Iltimos, avval ro'yxatdan o'ting.",
                reply_markup=register_kb
            )
            return

        if user.get('is_active') == 0 or user.get('is_active') is False:
            await message.answer(
                "🚫 Sizning akkauntingiz to'xtatilgan.\n"
                "Qayta faollashtirmoqchimisiz?",
                reply_markup=re_active_inkb
            )
            return

        filtered_kwargs = {k: v for k, v in kwargs.items()
                          if k not in ['dispatcher', 'bot', 'event_update', 'bots']}

        return await func(message, *args, **filtered_kwargs)
    return wrapper


def check_registration_callback(func):
    """Decorator to check if user is registered and active before executing callback handler"""
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        chat_id = callback.from_user.id
        user = get_user_by_chat_id(chat_id)

        if not user:
            await callback.message.answer(
                "❌ Siz ro'yxatdan o'tmagansiz!\n"
                "Iltimos, avval ro'yxatdan o'ting.",
                reply_markup=register_kb
            )
            await callback.answer("Avval ro'yxatdan o'ting")
            return


        filtered_kwargs = {k: v for k, v in kwargs.items()
                          if k not in ['dispatcher', 'bot', 'event_update', 'bots']}

        return await func(callback, *args, **filtered_kwargs)
    return wrapper
from environs import Env


user_router = Router()
env = Env()
env.read_env()

Admin_ID = env.str("ADMIN_CHATID")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@user_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    chat_id = message.from_user.id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await message.answer(REG_TEXT, reply_markup=ReplyKeyboardRemove())
        await state.set_state(Register.name)
        return

    if user.get('is_active') == 0:
        await message.answer(
            "🚫 Sizning akkauntingiz to'xtatilgan.\n"
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
async def register_handler(message: Message, state: FSMContext):
    await message.answer("Ismingizni kiriting: ", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Register.name) 

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


        
@user_router.message(F.text=="📋 Menyu")
@check_registration
async def menu_btn(message:Message, state:FSMContext, **kwargs):
    await message.answer("📋 Asosiy menyu:",reply_markup=after_menukb)
    

@user_router.message(F.text=="⬅️ Orqaga")
@check_registration
async def back_menu(message:Message, **kwargs):
    await message.answer("📋 Asosiy menyu", reply_markup=menu_kb)
    

@user_router.message(F.text=="📞 Aloqa")
@check_registration
async def contact_admin(message:Message, state: FSMContext, **kwargs):
    await state.set_state(ContactAdmin.user_waiting_massage)
    await message.answer("""📩 Savollaringiz bormi?
  Biz har doim yordam berishga tayyormiz!
  Savvolarigizni yozing va Pastagi Yuborish tugmasini bosing""", reply_markup=send_toAdminkb)


@user_router.message(ContactAdmin.user_waiting_massage, F.text == "❌ Bekor qilish")
async def cancel_contact(message:Message, state: FSMContext, **kwargs):
    await state.clear()
    await message.answer("Bosh menu", reply_markup=menu_kb)


user_messages = {}

@user_router.message(ContactAdmin.user_waiting_massage, F.text.not_in(["📤 Yuborish", "❌ Bekor qilish"]))
async def get_user_message(message: Message, **kwargs):
    user_messages[message.from_user.id] = message.text
    await message.answer("✅ Xabaringiz saqlandi. Endi 📤 Yuborish tugmasini bosing.")



@user_router.message(ContactAdmin.user_waiting_massage, F.text=="📤 Yuborish")
async def send_toAdmin(message:Message, state: FSMContext, **kwargs):
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
@check_registration
async def my_profile(message: Message, **kwargs):
    await message.answer("👤 Profil", reply_markup=profile_kb)

    

@user_router.message(F.text == "🔎 Qidirmoq")
@check_registration
async def search_btn(message:Message, **kwargs):
    await message.answer("Qidirish turi: ", reply_markup=searchClickkb)
    

@user_router.message(F.text== "📚 Barchasi")
@check_registration
async def all_handler(message: Message, **kwargs):
    await message.answer("Barcha kitoblarni ko'rish demo", reply_markup=all_kb)

@user_router.message(F.text=="💸 Chegirma")
@check_registration
async def discount_handlar(message: Message, **kwargs):
    await message.answer("Diskountdagi kitoblar: (DEMO)")

@user_router.message(F.text=="🆕 Yangiliklar")
@check_registration
async def new_hanler(message: Message, **kwargs):
    await message.answer("So'ngi kelgan kitoblar. (Demo)")

@user_router.message(F.text=="⬅️ Orqaga")
@check_registration
async def back_menu(message:Message, **kwargs):
    await message.answer("📋 Asosiy menyu", reply_markup=after_menukb)


@check_registration
@user_router.message(F.text=="⬅️ Orqaga")
async def back_menu(message:Message, **kwargs):
    await message.answer("📋 Asosiy menyu", reply_markup=menu_kb)
    

@user_router.message(F.text=="🛒 Buyurtma")
async def order_handler(message: Message, **kwargs):
    """Show order menu with cart and order history options"""
    cart_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Savatchani ko'rish"), KeyboardButton(text="📦 Mening buyurtmalarim")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )

    await message.answer("📋 Buyurtma menyusi:", reply_markup=cart_kb)

@user_router.message(F.text == "🛒 Savatchani ko'rish")
@check_registration
async def view_cart(message: Message, **kwargs):
    """View user's cart"""
    user_id = message.from_user.id
    cart_items = get_user_cart(user_id)

    if not cart_items:
        await message.answer(
            "🛒 Savatcha bo'sh\n\n"
            "Kitob qidirib, savatchaga qo'shing!",
            reply_markup=after_menukb
        )
        return

    response = "🛒 Sizning savatchangiz:\n\n"
    total_amount = 0

    for i, item in enumerate(cart_items, 1):
        item_total = item['quantity'] * item['price']
        total_amount += item_total

        response += f"{i}. 📖 {item['title']}\n"
        response += f"   👨‍🏫 {item['author']}\n"
        response += f"   💰 {item['price']} so'm × {item['quantity']} = {item_total} so'm\n\n"

    response += f"💰 Jami: {total_amount} so'm\n\n"
    response += "📋 Nima qilmoqchisiz?"

    cart_action_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Buyurtma berish"), KeyboardButton(text="🗑️ Savatchani tozalash")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )

    await message.answer(response, reply_markup=cart_action_kb)

@user_router.message(F.text == "📦 Mening buyurtmalarim")
@check_registration
async def view_orders(message: Message, **kwargs):
    """View user's order history"""
    user_id = message.from_user.id
    orders_data = get_user_orders(user_id, page=1, per_page=5)

    if not orders_data['orders']:
        await message.answer(
            "📦 Sizda buyurtmalar yo'q\n\n"
            "Birinchi buyurtmani bering!",
            reply_markup=after_menukb
        )
        return

    response = "📦 Sizning buyurtmalaringiz:\n\n"

    for i, order in enumerate(orders_data['orders'], 1):
        status_emoji = {
            'pending': '⏳',
            'approved': '✅',
            'shipped': '📦',
            'delivered': '🚚',
            'cancelled': '❌'
        }

        emoji = status_emoji.get(order['status'], '❓')
        response += f"{i}. {emoji} Buyurtma #{order['id']}\n"
        response += f"   💰 {order['total_amount']} so'm\n"
        response += f"   📅 {order['created_at'][:10]}\n"
        response += f"   📊 Holat: {order['status']}\n\n"

    response += f"📄 Sahifa {orders_data['current_page']}/{orders_data['total_pages']}"

    if orders_data['total_pages'] > 1:
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

        nav_buttons = []
        if orders_data['current_page'] > 1:
            nav_buttons.append(InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"orders_page_{orders_data['current_page'] - 1}"
            ))
        if orders_data['current_page'] < orders_data['total_pages']:
            nav_buttons.append(InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"orders_page_{orders_data['current_page'] + 1}"
            ))

        keyboard = InlineKeyboardMarkup(inline_keyboard=[nav_buttons] if nav_buttons else [])

        await message.answer(response, reply_markup=keyboard)
    else:
        await message.answer(response, reply_markup=after_menukb)

@user_router.message(F.text == "✅ Buyurtma berish")
@check_registration
async def process_cart_order(message: Message, state: FSMContext):
    """Process order from cart"""
    user_id = message.from_user.id
    cart_items = get_user_cart(user_id)

    if not cart_items:
        await message.answer("❌ Savatcha bo'sh")
        return

    # Calculate total amount with validation
    total_amount = 0
    for item in cart_items:
        if item.get('quantity', 0) > 0 and item.get('price', 0) > 0:
            total_amount += item['quantity'] * item['price']

    if total_amount <= 0:
        await message.answer("❌ Savatcha summasi noto'g'ri") 
        return

    await state.set_state(OrderProcess.entering_delivery_info)
    await state.update_data(cart_order=True, total_amount=total_amount)

    await message.answer(
        "📍 Yetkazish manzilini kiriting:\n\n"
        "Misol: Toshkent shahri, Yunusobod tumani, Abdulla Qodiriy ko'chasi 12-uy",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⬅️ Orqaga")],
                [KeyboardButton(text="❌ Bekor qilish")]
            ],
            resize_keyboard=True
        )
    )

@user_router.message(OrderProcess.entering_delivery_info, F.text.not_in(["⬅️ Orqaga", "❌ Bekor qilish"]))
@check_registration
async def get_delivery_info_for_cart(message: Message, state: FSMContext, **kwargs):
    """Get delivery address for cart order and proceed to payment"""
    delivery_address = message.text.strip()

    if not delivery_address or len(delivery_address) < 10:
        await message.answer("❌ Yetkazish manzili to'liq emas. Iltimos, batafsil yozing (kamida 10 ta belgi):")
        return

    await state.update_data(delivery_address=delivery_address)

    payment_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Karta orqali to'lash", callback_data="payment_card_cart")],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_delivery")]
        ]
    )

    await state.set_state(OrderProcess.selecting_payment)
    await message.answer(
        "💳 To'lov turini tanlang:\n\n"
        "⚠️ Faqat karta orqali to'lash mavjud",
        reply_markup=payment_kb
    )

@user_router.message(F.text == "🗑️ Savatchani tozalash")
@check_registration
async def clear_cart(message: Message, **kwargs):
    """Clear user's cart"""
    user_id = message.from_user.id

    clear_user_cart(user_id)

    await message.answer(
        "🗑️ Savatcha tozalandi",
        reply_markup=after_menukb
    )


@user_router.message(F.text == "📄 Ma’lumotlarim")
@check_registration
async def about_handler(message: Message, **kwargs):
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
@check_registration
async def start_edit(message: Message, state: FSMContext, **kwargs):
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
@check_registration
async def delate_user(message: Message, **kwargs):
    await message.answer("Rostdan ham o'chirmoqchimisz", reply_markup=del_account_inkb)


@check_registration_callback
@user_router.callback_query(F.data == "title")
async def search_by_title(callback: CallbackQuery, state: FSMContext):
    await state.update_data(search_type="title")
    await callback.message.edit_text("📚 Qaysi sarlavha bo'yicha qidirmoqchisiz?")
    await state.set_state(BookSearch.waiting_for_search_query)
    await callback.answer()

@check_registration_callback
@user_router.callback_query(F.data == "genre")
async def search_by_genre(callback: CallbackQuery, state: FSMContext):
    await state.update_data(search_type="genre")
    await callback.message.edit_text("🎭 Qaysi janr bo'yicha qidirmoqchisiz?")
    await state.set_state(BookSearch.waiting_for_search_query)
    await callback.answer()

@check_registration_callback
@user_router.callback_query(F.data == "author")
async def search_by_author(callback: CallbackQuery, state: FSMContext):
    await state.update_data(search_type="author")
    await callback.message.edit_text("✍️ Qaysi muallif bo'yicha qidirmoqchisiz?")
    await state.set_state(BookSearch.waiting_for_search_query)
    await callback.answer()

@check_registration
@user_router.message(BookSearch.waiting_for_search_query)
async def process_search_query(message: Message, state: FSMContext):
    search_query = message.text.strip()

    if not search_query:
        await message.answer("❌ Qidiruv so'rovi bo'sh bo'lishi mumkin emas!\n\nQaytadan qidiruv so'zini kiriting:")
        return

    data = await state.get_data()
    search_type = data.get('search_type')

    if not search_type:
        await message.answer("❌ Qidirish turi aniqlanmadi. Qaytadan boshlang.")
        await state.clear()
        return

    pagination_data = get_books_paginated(page=1, per_page=10, search_query=search_query, search_type=search_type)

    if not pagination_data['books']:
        await message.answer(
            f"❌ <b>{search_type.title()} bo'yicha</b> \"{search_query}\" <b>qidiruvi bo'yicha hech narsa topilmadi</b>\n\n"
            "Boshqa so'z bilan qidiring yoki qidirish turini o'zgartiring.",
            parse_mode="HTML",
            reply_markup=searchClickkb
        )
        await state.clear()
        return

    response = f"📚 <b>{search_type.title()} bo'yicha qidiruv natijalari:</b> \"{search_query}\"\n\n"

    for i, book in enumerate(pagination_data['books'], 1):
        response += f"{i}. 📖 {book['title']}\n"

    response += f"\n📄 Sahifa {pagination_data['current_page']}/{pagination_data['total_pages']}"
    response += f"\n📊 Jami {pagination_data['total_count']} ta kitob topildi"
    response += f"\n\n🔢 Kitobni tanlash uchun raqamni bosing:"

    pagination_keyboard = create_pagination_keyboard(
        pagination_data['current_page'],
        pagination_data['total_pages'],
        search_type,
        search_query,
        pagination_data['books']
    )

    await message.answer(response, reply_markup=pagination_keyboard, parse_mode="HTML")
    await state.update_data(
        search_query=search_query,
        search_type=search_type,
        current_page=1,
        total_pages=pagination_data['total_pages']
    )
    await state.set_state(BookSearch.pagination)

@check_registration_callback
@user_router.callback_query(F.data.startswith("page_"))
async def handle_page_navigation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    search_query = data.get('search_query')
    search_type = data.get('search_type')

    try:
        parts = callback.data.split('_')
        new_page = int(parts[1])
        search_type = parts[2] if len(parts) > 2 else search_type
        search_query = '_'.join(parts[3:]) if len(parts) > 3 else search_query

        pagination_data = get_books_paginated(
            page=new_page,
            per_page=10,
            search_query=search_query,
            search_type=search_type
        )

        if not pagination_data['books']:
            await callback.answer("❌ Bu sahifada kitoblar yo'q")
            return

        response = f"📚 <b>{search_type.title()} bo'yicha qidiruv natijalari:</b> \"{search_query}\"\n\n"

        for i, book in enumerate(pagination_data['books'], 1):
            response += f"{i}. 📖 {book['title']}\n"

        response += f"\n📄 Sahifa {pagination_data['current_page']}/{pagination_data['total_pages']}"
        response += f"\n📊 Jami {pagination_data['total_count']} ta kitob topildi"
        response += f"\n\n🔢 Kitobni tanlash uchun raqamni bosing:"

        pagination_keyboard = create_pagination_keyboard(
            pagination_data['current_page'],
            pagination_data['total_pages'],
            search_type,
            search_query,
            pagination_data['books']
        )

        await callback.message.edit_text(response, reply_markup=pagination_keyboard, parse_mode="HTML")
        await state.update_data(current_page=new_page)
        await callback.answer()

    except (ValueError, IndexError) as e:
        await callback.answer("❌ Sahifa raqami noto'g'ri")
    except Exception as e:
        await callback.answer("❌ Xatolik yuz berdi")

@check_registration_callback
@user_router.callback_query(F.data.startswith("prev_"))
async def handle_prev_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get('current_page', 1)
    search_query = data.get('search_query')
    search_type = data.get('search_type')

    if current_page <= 1:
        await callback.answer("❌ Bu birinchi sahifa")
        return

    new_page = current_page - 1

    pagination_data = get_books_paginated(
        page=new_page,
        per_page=10,
        search_query=search_query,
        search_type=search_type
    )

    response = f"📚 <b>{search_type.title()} bo'yicha qidiruv natijalari:</b> \"{search_query}\"\n\n"

    for i, book in enumerate(pagination_data['books'], 1):
        response += f"{i}. 📖 {book['title']}\n"

    response += f"\n📄 Sahifa {pagination_data['current_page']}/{pagination_data['total_pages']}"
    response += f"\n📊 Jami {pagination_data['total_count']} ta kitob topildi"
    response += f"\n\n🔢 Kitobni tanlash uchun raqamni bosing:"

    pagination_keyboard = create_pagination_keyboard(
        pagination_data['current_page'],
        pagination_data['total_pages'],
        search_type,
        search_query,
        pagination_data['books']
    )

    await callback.message.edit_text(response, reply_markup=pagination_keyboard, parse_mode="HTML")
    await state.update_data(current_page=new_page)
    await callback.answer()

@check_registration_callback
@user_router.callback_query(F.data.startswith("next_"))
async def handle_next_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get('current_page', 1)
    total_pages = data.get('total_pages', 1)
    search_query = data.get('search_query')
    search_type = data.get('search_type')

    if current_page >= total_pages:
        await callback.answer("❌ Bu oxirgi sahifa")
        return

    new_page = current_page + 1

    pagination_data = get_books_paginated(
        page=new_page,
        per_page=10,
        search_query=search_query,
        search_type=search_type
    )

    response = f"📚 <b>{search_type.title()} bo'yicha qidiruv natijalari:</b> \"{search_query}\"\n\n"

    for i, book in enumerate(pagination_data['books'], 1):
        response += f"{i}. 📖 {book['title']}\n"

    response += f"\n📄 Sahifa {pagination_data['current_page']}/{pagination_data['total_pages']}"
    response += f"\n📊 Jami {pagination_data['total_count']} ta kitob topildi"
    response += f"\n\n🔢 Kitobni tanlash uchun raqamni bosing:"

    response += f"\n📄 Sahifa {pagination_data['current_page']}/{pagination_data['total_pages']}"
    response += f"\n📊 Jami {pagination_data['total_count']} ta kitob topildi"

    pagination_keyboard = create_pagination_keyboard(
        pagination_data['current_page'],
        pagination_data['total_pages'],
        search_type,
        search_query,
        pagination_data['books']
    )

    await callback.message.edit_text(response, reply_markup=pagination_keyboard, parse_mode="HTML")
    await state.update_data(current_page=new_page)
    await callback.answer()

@check_registration_callback
@user_router.callback_query(F.data.startswith("select_book_"))
async def handle_book_selection(callback: CallbackQuery, state: FSMContext):
    try:
       
        parts = callback.data.split('_')
        book_num = int(parts[2])
        current_page = int(parts[3])
        search_type = parts[4] if len(parts) > 4 else None
        search_query = '_'.join(parts[5:]) if len(parts) > 5 else None

        data = await state.get_data()
        user_search_query = data.get('search_query')
        user_search_type = data.get('search_type')

        final_search_query = search_query or user_search_query
        final_search_type = search_type or user_search_type

        if not final_search_query or not final_search_type:
            await callback.answer("❌ Qidirish ma'lumotlari topilmadi")
            return

        pagination_data = get_books_paginated(
            page=current_page,
            per_page=10,
            search_query=final_search_query,
            search_type=final_search_type
        )

        if not pagination_data['books'] or book_num > len(pagination_data['books']):
            await callback.answer("❌ Kitob topilmadi")
            return

        selected_book = pagination_data['books'][book_num - 1]

        if selected_book.get('image_path') and selected_book['image_path'] != 'None':
            try:
              
                photo_path = FSInputFile(selected_book['image_path'])
                caption = f"📖 <b>{selected_book['title']}</b>\n\n"
                caption += f"👨‍🏫 Muallif: {selected_book['author']}\n"
                caption += f"🎭 Janr: {selected_book['genre']}\n"
                caption += f"💰 Narx: {selected_book['price']} so'm\n"
                caption += f"📦 Miqdor: {selected_book['quantity']}\n"
                if selected_book.get('description'):
                    caption += f"📝 Tavsif: {selected_book['description']}\n"
                caption += f"🆔 ID: {selected_book['id']}\n\n"
                caption += "📋 Bu kitobni nima qilmoqchisiz?"

                await callback.message.answer_photo(photo_path, caption=caption, reply_markup=order_ikb, parse_mode="HTML")
            except Exception as e:
                
                response = f"📖 <b>{selected_book['title']}</b>\n\n"
                response += f"👨‍🏫 Muallif: {selected_book['author']}\n"
                response += f"🎭 Janr: {selected_book['genre']}\n"
                response += f"💰 Narx: {selected_book['price']} so'm\n"
                response += f"📦 Miqdor: {selected_book['quantity']}\n"
                if selected_book.get('description'):
                    response += f"📝 Tavsif: {selected_book['description']}\n"
                response += f"🆔 ID: {selected_book['id']}\n\n"
                response += "📋 Bu kitobni nima qilmoqchisiz?"

                await callback.message.edit_text(response, reply_markup=order_ikb, parse_mode="HTML")
        else:
            #
            response = f"📖 <b>{selected_book['title']}</b>\n\n"
            response += f"👨‍🏫 Muallif: {selected_book['author']}\n"
            response += f"🎭 Janr: {selected_book['genre']}\n"
            response += f"💰 Narx: {selected_book['price']} so'm\n"
            response += f"📦 Miqdor: {selected_book['quantity']}\n"
            if selected_book.get('description'):
                response += f"📝 Tavsif: {selected_book['description']}\n"
            response += f"🆔 ID: {selected_book['id']}\n\n"
            response += "📋 Bu kitobni nima qilmoqchisiz?"

            await callback.message.edit_text(response, reply_markup=order_ikb, parse_mode="HTML")
        await state.update_data(selected_book=selected_book)
        await callback.answer()

    except (ValueError, IndexError) as e:
        await callback.answer("❌ Kitob raqami noto'g'ri")
    except Exception as e:
        await callback.answer("❌ Xatolik yuz berdi")

@check_registration_callback
@user_router.callback_query(F.data == "back_to_search")
async def back_to_search_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Qidirish turi:", reply_markup=searchClickkb)
    await callback.answer()


def format_book_display_message(book, quantity, total_price, show_description=True):
    """Helper function to format book display message consistently"""
    response = f"📖 <b>{book['title']}</b>\n\n"
    response += f"👨‍🏫 Muallif: {book['author']}\n"
    response += f"🎭 Janr: {book['genre']}\n"
    response += f"💰 Narx: {total_price} so'm\n"
    response += f"📦 Miqdor: {quantity}\n"
    if show_description and book.get('description'):
        response += f"📝 Tavsif: {book['description'][:100]}...\n"
    response += f"🆔 ID: {book['id']}\n\n"
    response += "📋 Bu kitobni nima qilmoqchisiz?"
    return response

@check_registration_callback
@user_router.callback_query(F.data == "decrease_quantity")
async def decrease_quantity(callback: CallbackQuery, state: FSMContext):
    """Decrease book quantity in order"""
    data = await state.get_data()
    current_quantity = data.get('order_quantity', 1)
    book = data.get('selected_book')

    if not book:
        await callback.answer("❌ Kitob topilmadi")
        return

    if current_quantity > 1:
        new_quantity = current_quantity - 1
        total_price = book['price'] * new_quantity

        await state.update_data(order_quantity=new_quantity)

        
        new_caption = format_book_display_message(book, new_quantity, total_price)

        try:
            
            if book.get('image_path') and book['image_path'] != 'None':
                current_caption = getattr(callback.message, 'caption', "") or ""
                if current_caption != new_caption:
                    await callback.message.edit_caption(new_caption, reply_markup=order_ikb, parse_mode="HTML")
            else:
               
                current_text = getattr(callback.message, 'text', "") or ""
                if current_text != new_caption:
                    await callback.message.edit_text(new_caption, reply_markup=order_ikb, parse_mode="HTML")
        except Exception as e:
            
            try:
                if book.get('image_path') and book['image_path'] != 'None':
                    photo_path = FSInputFile(book['image_path'])
                    await callback.message.answer_photo(photo_path, caption=new_caption, reply_markup=order_ikb, parse_mode="HTML")
                else:
                    await callback.message.answer(new_caption, reply_markup=order_ikb, parse_mode="HTML")
            except Exception as e2:
                logger.error(f"Failed to send fallback message: {e2}")

        await callback.answer(f"Miqdor: {new_quantity}")
    else:
        await callback.answer("❌ Minimal miqdor: 1")

@check_registration_callback
@user_router.callback_query(F.data == "increase_quantity")
async def increase_quantity(callback: CallbackQuery, state: FSMContext):
    """Increase book quantity in order"""
    data = await state.get_data()
    current_quantity = data.get('order_quantity', 1)
    book = data.get('selected_book')

    if not book:
        await callback.answer("❌ Kitob topilmadi")
        return

    max_quantity = book.get('quantity', 0)
    if max_quantity > 0 and current_quantity >= max_quantity:
        await callback.answer(f"❌ Maksimal miqdor: {max_quantity}")
        return

    new_quantity = current_quantity + 1
    total_price = book['price'] * new_quantity

    await state.update_data(order_quantity=new_quantity)

    
    new_caption = format_book_display_message(book, new_quantity, total_price)

    try:
       
        if book.get('image_path') and book['image_path'] != 'None':
            current_caption = getattr(callback.message, 'caption', "") or ""
            if current_caption != new_caption:
                await callback.message.edit_caption(new_caption, reply_markup=order_ikb, parse_mode="HTML")
        else:
           
            current_text = getattr(callback.message, 'text', "") or ""
            if current_text != new_caption:
                await callback.message.edit_text(new_caption, reply_markup=order_ikb, parse_mode="HTML")
    except Exception as e:
        #
        try:
            if book.get('image_path') and book['image_path'] != 'None':
                photo_path = FSInputFile(book['image_path'])
                await callback.message.answer_photo(photo_path, caption=new_caption, reply_markup=order_ikb, parse_mode="HTML")
            else:
                await callback.message.answer(new_caption, reply_markup=order_ikb, parse_mode="HTML")
        except Exception as e2:
            logger.error(f"Failed to send fallback message: {e2}")

    await callback.answer(f"Miqdor: {new_quantity}")

@check_registration_callback
@user_router.callback_query(F.data == "quantity_display")
async def show_quantity_info(callback: CallbackQuery, state: FSMContext):
    """Show current quantity information"""
    data = await state.get_data()
    current_quantity = data.get('order_quantity', 1)
    book = data.get('selected_book')

    if not book:
        await callback.answer("❌ Kitob topilmadi")
        return

    total_price = book['price'] * current_quantity
    await callback.answer(f"📦 Hozirgi miqdor: {current_quantity}\n💰 Jami narx: {total_price} so'm")

@check_registration_callback
@user_router.callback_query(F.data == "Add_toCard")
async def add_to_cart_handler(callback: CallbackQuery, state: FSMContext):
    """Add book to cart"""
    data = await state.get_data()
    book = data.get('selected_book')
    quantity = data.get('order_quantity', 1)

    if not book:
        await callback.answer("❌ Kitob topilmadi")
        return

    user_id = callback.from_user.id
    total_price = book['price'] * quantity

    if add_to_cart(user_id, book['id'], quantity, book['price']):
        await callback.answer(f"✅ {quantity} ta kitob savatchaga qo'shildi!")
        await state.clear()
    else:
        await callback.answer("❌ Savatchaga qo'shishda xatolik yuz berdi")

@check_registration_callback
@user_router.callback_query(F.data == "sendItem")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    """Cancel current order"""
    await state.clear()
    await callback.message.answer("📋 Asosiy menyu", reply_markup=menu_kb)
    await callback.answer("✅ Bekor qilindi")

@check_registration_callback
@user_router.callback_query(F.data == "Cancel_item")
async def send_order(callback: CallbackQuery, state: FSMContext):
    """Send order to admin"""
    data = await state.get_data()
    book = data.get('selected_book')
    quantity = data.get('order_quantity', 1)

    if not book:
        await callback.answer("❌ Kitob topilmadi")
        return

    user_id = callback.from_user.id
    total_price = book['price'] * quantity

    await state.update_data(
        order_book_id=book['id'],
        order_quantity=quantity,
        order_price=total_price,
        selected_book=book  
    )

    await state.set_state(OrderProcess.entering_delivery_info)
    await callback.message.answer(
        "📍 Yetkazish manzilini kiriting:\n\n"
        "Misol: Toshkent shahri, Yunusobod tumani, Abdulla Qodiriy ko'chasi 12-uy",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⬅️ Orqaga")],
                [KeyboardButton(text="❌ Bekor qilish")]
            ],
            resize_keyboard=True
        )
    )
    await callback.answer()

@user_router.message(OrderProcess.entering_delivery_info, F.text == "⬅️ Orqaga")
async def back_from_delivery(message: Message, state: FSMContext, **kwargs):
    """Go back to book selection"""
    data = await state.get_data()
    book = data.get('selected_book')

    if book and book.get('image_path') and book['image_path'] != 'None':
        try:
            photo_path = FSInputFile(book['image_path'])
            caption = f"📖 <b>{book['title']}</b>\n\n"
            caption += f"💰 Narx: {book['price'] * data.get('order_quantity', 1)} so'm\n"
            caption += f"📦 Miqdor: {data.get('order_quantity', 1)}\n\n"
            caption += "📋 Bu kitobni nima qilmoqchisiz?"

            await message.answer_photo(photo_path, caption=caption, reply_markup=order_ikb)
        except:
            response = f"📖 <b>{book['title']}</b>\n\n"
            response += f"💰 Narx: {book['price'] * data.get('order_quantity', 1)} so'm\n"
            response += f"📦 Miqdor: {data.get('order_quantity', 1)}\n\n"
            response += "📋 Bu kitobni nima qilmoqchisiz?"
            await message.answer(response, reply_markup=order_ikb)
    else:
        response = f"📖 <b>{book['title']}</b>\n\n"
        response += f"💰 Narx: {book['price'] * data.get('order_quantity', 1)} so'm\n"
        response += f"📦 Miqdor: {data.get('order_quantity', 1)}\n\n"
        response += "📋 Bu kitobni nima qilmoqchisiz?"
        await message.answer(response, reply_markup=order_ikb)

@user_router.message(OrderProcess.entering_delivery_info, F.text == "❌ Bekor qilish")
async def cancel_order_process(message: Message, state: FSMContext, **kwargs):
    await state.clear()
    await message.answer("✅ Buyurtma bekor qilindi", reply_markup=menu_kb)

@user_router.message(OrderProcess.entering_delivery_info, F.text.not_in(["⬅️ Orqaga", "❌ Bekor qilish"]))
async def get_delivery_info(message: Message, state: FSMContext, **kwargs):
    """Get delivery address and proceed to payment"""
    delivery_address = message.text.strip()

    if not delivery_address or len(delivery_address) < 10:
        await message.answer("❌ Yetkazish manzili to'liq emas. Iltimos, batafsil yozing (kamida 10 ta belgi):")
        return

    await state.update_data(delivery_address=delivery_address)

    payment_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Karta orqali to'lash", callback_data="payment_card")],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_delivery")]
        ]
    )

    await state.set_state(OrderProcess.selecting_payment)
    await message.answer(
        "💳 To'lov turini tanlang:\n\n"
        "⚠️ Faqat karta orqali to'lash mavjud",
        reply_markup=payment_kb
    )

@check_registration_callback
@user_router.callback_query(F.data == "payment_card_cart")
async def confirm_cart_payment(callback: CallbackQuery, state: FSMContext):
    """Confirm card payment for cart order and create order"""
    data = await state.get_data()
    delivery_address = data.get('delivery_address')
    total_amount = data.get('total_amount', 0)

    if not all([delivery_address, total_amount]):
        await callback.answer("❌ Buyurtma ma'lumotlari to'liq emas")
        return

    if total_amount <= 0:
        await callback.answer("❌ Buyurtma summasi noto'g'ri")
        return

    user_id = callback.from_user.id

   
    try:
        order_id = create_order(
            user_id=user_id,
            delivery_address=delivery_address,
            payment_type="card",
            total_amount=total_amount
        )

        if order_id:
            from buttons import reply_toUser
            await callback.bot.send_message(
                Admin_ID,
                f"🆕 Yangi buyurtma (savatchadan)!\n\n"
                f"👤 User ID: {user_id}\n"
                f"📦 Buyurtma ID: {order_id}\n"
                f"💰 Summa: {total_amount} so'm\n"
                f"📍 Manzil: {delivery_address}\n"
                f"💳 To'lov: Karta",
                reply_markup=reply_toUser(user_id)
            )

            await state.clear()
            await callback.message.answer(
                "✅ Buyurtma yuborildi!\n\n"
                "📋 Buyurtmalaringizni ko'rish uchun:\n"
                "🛒 Buyurtma → 📦 Mening buyurtmalarim",
                reply_markup=menu_kb
            )
        else:
            logger.error(f"Failed to create order for user {user_id}")
            await callback.answer("❌ Buyurtma yaratishda xatolik yuz berdi")
    except Exception as e:
        logger.error(f"Error creating cart order for user {user_id}: {e}")
        await callback.answer("❌ Buyurtma yaratishda texnik xatolik yuz berdi")

    await callback.answer()

@check_registration_callback
@user_router.callback_query(F.data == "payment_card")
async def confirm_card_payment(callback: CallbackQuery, state: FSMContext):
    """Confirm card payment and create order"""
    data = await state.get_data()
    delivery_address = data.get('delivery_address')
    book_id = data.get('order_book_id')
    quantity = data.get('order_quantity', 1)
    price = data.get('order_price', 0)
    selected_book = data.get('selected_book')


    if not delivery_address:
        await callback.answer("❌ Yetkazish manzili ko'rsatilmagan")
        return

    if not book_id and not selected_book:
        await callback.answer("❌ Kitob ma'lumotlari topilmadi")
        return


    final_book_id = book_id or (selected_book.get('id') if selected_book else None)
    final_quantity = quantity or 1
    final_price = price or (selected_book.get('price', 0) * final_quantity if selected_book else 0)

    if not final_book_id or final_price <= 0:
        debug_info = f"Debug: delivery_address={bool(delivery_address)}, book_id={book_id}, selected_book={bool(selected_book)}, price={final_price}"
        logger.warning(f"Order validation failed for user {callback.from_user.id}: {debug_info}")
        await callback.answer("❌ Buyurtma ma'lumotlari to'liq emas")
        return

    user_id = callback.from_user.id

    try:
        order_id = create_order(
            user_id=user_id,
            delivery_address=delivery_address,
            payment_type="card",
            total_amount=final_price,
            book_id=final_book_id,
            quantity=final_quantity,
            price=selected_book.get('price', 0) if selected_book else 0
        )

        if order_id:
            from buttons import reply_toUser
            await callback.bot.send_message(
                Admin_ID,
                f"🆕 Yangi buyurtma!\n\n"
                f"👤 User ID: {user_id}\n"
                f"📦 Buyurtma ID: {order_id}\n"
                f"💰 Summa: {final_price} so'm\n"
                f"📍 Manzil: {delivery_address}\n"
                f"💳 To'lov: Karta",
                reply_markup=reply_toUser(user_id)
            )

            await state.clear()
            await callback.message.answer(
                "✅ Buyurtma yuborildi!\n\n"
                "📋 Buyurtmalaringizni ko'rish uchun:\n"
                "🛒 Buyurtma → 📦 Mening buyurtmalarim",
                reply_markup=menu_kb
            )
        else:
            logger.error(f"Failed to create order for user {user_id}")
            await callback.answer("❌ Buyurtma yaratishda xatolik yuz berdi")
    except Exception as e:
        logger.error(f"Error creating single book order for user {user_id}: {e}")
        await callback.answer("❌ Buyurtma yaratishda texnik xatolik yuz berdi")

    await callback.answer()

@check_registration_callback
@user_router.callback_query(F.data == "back_to_delivery")
async def back_to_delivery_info(callback: CallbackQuery, state: FSMContext):
    """Go back to delivery info input"""
    await state.set_state(OrderProcess.entering_delivery_info)
    await callback.message.answer(
        "📍 Yetkazish manzilini kiriting:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⬅️ Orqaga")],
                [KeyboardButton(text="❌ Bekor qilish")]
            ],
            resize_keyboard=True
        )
    )
    await callback.answer()