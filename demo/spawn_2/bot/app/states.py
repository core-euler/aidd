from aiogram.fsm.state import State, StatesGroup


class TaskCreate(StatesGroup):
    waiting_title = State()
    waiting_difficulty = State()
    waiting_deadline = State()
    waiting_deadline_manual = State()
