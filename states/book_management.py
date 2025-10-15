from aiogram.fsm.state import State, StatesGroup

class BookManagement(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_author = State()
    waiting_for_price = State()
    waiting_for_genre = State()
    waiting_for_quantity = State()
    waiting_for_image = State()
    waiting_for_book_id = State()
    viewing_books = State()

class BookSearch(StatesGroup):
    waiting_for_search_query = State()
    viewing_search_results = State()
    pagination = State()

class OrderProcess(StatesGroup):
    selecting_book = State()
    adjusting_quantity = State()
    confirming_order = State()
    entering_delivery_info = State()
    selecting_payment = State()
    order_sent = State()

class CartManagement(StatesGroup):
    viewing_cart = State()
    cart_pagination = State()