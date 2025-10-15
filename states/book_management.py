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
