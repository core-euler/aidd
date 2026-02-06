from aiogram.fsm.state import State, StatesGroup


class CreateTask(StatesGroup):
    title = State()
    difficulty = State()
    deadline = State()
