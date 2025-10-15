<<<<<<< HEAD
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class BookManagement(StatesGroup):
    main_menu = State()

    adding_book = State()
    waiting_title = State()
    waiting_author = State()
    waiting_price = State()
    waiting_description = State()
    waiting_genre = State()
    waiting_quantity = State()
    confirming_add = State()

    editing_book = State()
    selecting_book = State()
    selecting_field = State()
    waiting_edit_title = State()
    waiting_edit_author = State()
    waiting_edit_price = State()
    waiting_edit_description = State()
    waiting_edit_genre = State()
    waiting_edit_quantity = State()
    confirming_edit = State()

    deleting_book = State()
    confirming_delete = State()

    # View/search books states
    viewing_books = State()
    searching_books = State()
    waiting_search = State()

    # Book details view
    viewing_book_details = State()
=======
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
>>>>>>> 1dff7ebbc82c19826cb38a7a43a318a3c2687182
