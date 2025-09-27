from aiogram.fsm.context import FSMContext 
from aiogram.fsm.state import State, StatesGroup 

class Register(StatesGroup):
    name = State()
    phone = State()

