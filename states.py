from aiogram.dispatcher.filters.state import State, StatesGroup

# create states for saving user answer


# state for saving stream info
class Stream(StatesGroup):
    stream_link = State()


# state for saving notifications period info
class Notification(StatesGroup):
    notifications_period = State()


# state for saving defects period info
class Defect(StatesGroup):
    defects_period = State()

