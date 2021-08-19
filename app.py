import numpy as np

from model import get_prediction
from model import imget

from config import TOKEN

from keyboards import watch, stop, connect, connect_or_watch, reconnect_or_watch, reconnect_or_watch_or_help
from states import UserRegistration

import logging
import asyncio

from sqlite import SQLiteDatabase

import cv2
from io import BytesIO

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters import Command, Text

# Hyper-parameters
YOUR_TIME_YES = 20   # check image for defects every YOUR_TIME_YES seconds, if defects prob. > 0.65, you will be notified
YOUR_TIME_ALL = 300  # you will be notified every YOUR_TIME_ALL seconds about current state


# Bot settings
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


# Database connect
db = SQLiteDatabase("database_example.db")  # INPUT your database file


# ================ Handlers =======================

# Show help menu after /start
@dp.message_handler(Command("start"))
async def show_menu(message: types.Message):
    text = """
Hello, my name is Defects detection bot 3000!

I will notify you if any defect happens while 3d-printing! 🖨️
You will also get the current state every 5 minutes after turning on the stream. ⏱️

Here the steps to start bot: 🔔

    🌐 Connect your stream using the "Connect stream" command or button
    👀 Use the "Watch stream" command or button to get images with predictions every 5 minutes and whenever defect is detected
    🎬 To stop getting notifications use the "Stop stream" command or button

If something is not clear, you can always use the "Help" command or button 🆘

Enjoy 🍿
    """

    await message.answer(text)
    await message.answer("To connect the stream click the button below🔽", reply_markup=connect)


# show help menu after /help commands
@dp.message_handler(Text(equals=["Help", "/help"]))
async def process_start_command(message: types.Message):
    text = """
    
I will notify you if any defect happens while 3d-printing! 🖨️
You will also get the current state every 5 minutes after turning on the stream. ⏱️

Here the steps to start bot: 🔔

    🌐 Connect your stream using the "Connect stream" command or button
    👀 Use the "Watch stream" command or button to get images with predictions every 5 minutes and whenever defect is detected
    🎬 To stop getting notifications use the "Stop stream" command or button

If something is not clear, you can always use the "Help" command or button 🆘

Enjoy 🍿
    """

    await message.reply(text)
    await message.answer("To connect the stream or to watch it click the button below🔽", reply_markup=connect_or_watch)


# connect stream command plus user registration in db
@dp.message_handler(Text(equals=["Connect stream", "Reconnect stream", "/connect_stream"]))
async def cmd_dialog(message: types.Message):
    await UserRegistration.stream_link.set()  # вот мы указали начало работы состояний (states)
    await message.reply("Input your path to stream: ", reply=False)


@dp.message_handler(state=UserRegistration.stream_link)
async def stream(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        stream_link = data['text']
        print(stream_link)
        print(type(stream_link))

        # check if stream active, if not - reconnect or watch previous successfully connected stream
        cap = cv2.VideoCapture(stream_link)
        ret, frame = cap.read()
        if not ret or frame is None:
            await message.answer(
                "Stream is not connected, something went wrong...", disable_notification=False)
            await message.answer("To reconnect the stream or to watch it click the button below🔽",
                                 reply_markup=reconnect_or_watch)
            dp.current_state(user=message.from_user.id)
            await state.reset_state()

        else:
            if not db.subscriber_exists(message.from_user.id):
                # if user not in db then add it
                db.add_subscriber(user_id=message.from_user.id, status=False, stream=stream_link)
            else:
                # if user already in db then update it
                db.update_stream(user_id=message.from_user.id, status=False, stream=stream_link)

            await message.answer(
                "Stream connected...")
            await message.answer("To watch the stream click the button below🔽",
                                 reply_markup=watch)
            dp.current_state(user=message.from_user.id)
            await state.reset_state()


# start stream command
@dp.message_handler(Text(equals=["Watch stream", "/watch"]))
async def subscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        # if user not in db then add it
        db.add_subscriber(user_id=message.from_user.id, status=True)

    else:
        # if user already in db then update it
        db.update_subscription(user_id=message.from_user.id, status=True)

    await message.answer(
        "Stream starting...")
    await message.answer("To stop the stream click the button below🔽",
                         reply_markup=stop)


# stop stream
@dp.message_handler(Text(equals=["Stop stream", "/stop"]))
async def unsubscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        # if user not in db then just write it to db with non-active status
        db.add_subscriber(message.from_user.id, False)
        await message.answer("You are not watching stream yet!", disable_notification=False)
    else:
        # if user in db then update his status to non-active
        db.update_subscription(message.from_user.id, False)

        await message.answer("Stopping stream...")
        await message.answer("To restart the bot click one of buttons below🔽",
                             reply_markup=reconnect_or_watch_or_help)


# alert defects notifications
async def get_yes_defects(time=10):

    while True:

        # wait "time" seconds till next defects check happens (among all users)
        await asyncio.sleep(time)

        # get list of active watchers
        subscriptions = db.get_subscriptions()

        for s in subscriptions:

            # 4th column in db
            stream_link = s[3]

            cap = cv2.VideoCapture(stream_link)
            ret, frame = cap.read()

            if ret and frame is not None:
                # if video stream active, then continue detection

                verdict, prob_yes_defects = get_prediction(frame)
                # for logs
                print("TEST_YES: OK")

                # loud notification - medium defects detected
                if prob_yes_defects >= 0.65:  # 0.65 - based on verdicts in get_prediction

                    # load photo to memory and push it to bot
                    bio = BytesIO()
                    bio.name = 'image.jpeg'
                    frame = np.flip(frame, axis=-1)
                    image = imget(frame)
                    image.save(bio, 'JPEG')
                    bio.seek(0)

                    # s[1] - 2nd column of db
                    await bot.send_photo(
                        s[1],
                        photo=bio,
                        caption=verdict + f'{prob_yes_defects * 100:.4f}%',
                        disable_notification=False
                    )
            else:
                # if video stream not active, notify user
                await bot.send_message(
                    s[1],
                    text="Reload your stream, something went wrong..."
                )
                db.update_subscription(s[1], False)
                await bot.send_message(
                    s[1],
                    text="Stopping stream...",
                )
                await bot.send_message(s[1], text="To reconnect stream or try watching again click the button below🔽", reply_markup=reconnect_or_watch)


async def scheduled(time=30):
    while True:

        # wait "time" seconds till next defects check happens (among all users)
        await asyncio.sleep(time)

        # get list of active watchers
        subscriptions = db.get_subscriptions()

        for s in subscriptions:

            # 4th column in db
            stream_link = s[3]

            # get frame from stream
            cap = cv2.VideoCapture(stream_link)
            ret, frame = cap.read()

            if ret and frame is not None:
                # if video stream active, then continue detection

                verdict, prob_yes_defects = get_prediction(frame)
                # for logs
                # print(f"TEST {s[1]}: OK")

                # load photo to memory and push it to bot
                bio = BytesIO()
                bio.name = 'image.jpeg'
                frame = np.flip(frame, axis=-1)
                image = imget(frame)
                image.save(bio, 'JPEG')
                bio.seek(0)

                # s[1] - 2nd column of db
                await bot.send_photo(
                    s[1],
                    photo=bio,
                    caption=verdict + f'{prob_yes_defects * 100:.4f}%',
                    disable_notification=True
                )

            else:
                pass
                # for logs
                # print(f"TEST {s[1]}: NOT OK")

if __name__ == '__main__':
    # create event loop
    loop = asyncio.get_event_loop()
    loop.create_task(get_yes_defects(YOUR_TIME_YES))
    loop.create_task(scheduled(YOUR_TIME_ALL))
    executor.start_polling(dp, skip_updates=True)
