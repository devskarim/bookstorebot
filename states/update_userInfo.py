from aiogram.fsm.context import FSMContext 
from aiogram.fsm.state import State, StatesGroup 


class EditStates(StatesGroup):
    selecting_fields = State()
    waiting_name = State()
    waiting_phone = State()
    waiting_username = State()
    confirming_changes = State()