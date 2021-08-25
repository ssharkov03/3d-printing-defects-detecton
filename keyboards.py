from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


watch = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Watch stream"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

stop = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Stop stream"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

connect = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Connect stream"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

connect_or_watch = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Connect stream"),
            KeyboardButton(text="Watch stream")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


reconnect_or_watch = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Reconnect stream"),
            KeyboardButton(text="Watch stream")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

reconnect_or_watch_or_help = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Reconnect stream"),
            KeyboardButton(text="Watch stream")
        ],
        [
            KeyboardButton(text="Help")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

stream_managing = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Unmute defects notifications"),
            KeyboardButton(text="Mute defects notifications")
        ],
        [

            KeyboardButton(text="Get only scheduled notifications"),
            KeyboardButton(text="Get all notifications")
        ],
        [
            KeyboardButton(text="Stop stream")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

reconnect_editPeriods_watch_help = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Reconnect stream"),
            KeyboardButton(text="Edit notifications period"),
            KeyboardButton(text="Edit defects period")
        ],
        [
            KeyboardButton(text="Help"),
            KeyboardButton(text="Watch stream")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

