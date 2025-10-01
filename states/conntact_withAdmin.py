from aiogram.fsm.context import FSMContext 
from aiogram.fsm.state import State, StatesGroup 


class ContactAdmin(StatesGroup): 
	user_waiting_massage = State() 
	admin_waiting_reply = State()