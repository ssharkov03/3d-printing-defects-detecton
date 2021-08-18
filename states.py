from aiogram.dispatcher.filters.state import State, StatesGroup


# create states for saving user answer
class UserRegistration(StatesGroup):
    stream_link = State()
