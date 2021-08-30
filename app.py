# Imports
import numpy as np

from model import get_prediction
from model import imget

from config import TOKEN

from keyboards import connect, stream_managing, reconnect_editPeriods_watch_help
from states import Stream, Notification, Defect

import logging
import asyncio

from create_db import create_database
from sqlite import SQLiteDatabase

import cv2
from io import BytesIO

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters import Command, Text

# Hyper-parameters
T = 30  # Check image from camera for defects every T seconds
database_name = "YOUR_NAME.db"  # Input your database filename
Q = 0.65  # Threshold for defects probability
CONNECT_ERRORS_THRESH = 3  # If stream connection errors is greater than thresh then stop bot

# Bot setting
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

# Database create and connect
create_database(database_name)
db = SQLiteDatabase(database_name)


# ================ Handlers =======================
# Start command handler
@dp.message_handler(Command("start"))
async def show_menu(message: types.Message):
    text = """
Hi!

Once you start the stream I will update you when you want ⏱
When a defect occurs I will notify you immediately 🖨️

The steps to *start* bot: 🏁
--------------------------------------------------------
• ***Connect stream*** - connects your stream link 🌐

• ***Edit notifications period*** - every _<input>_ seconds get images with predictions _(600 by default)_ ♾️

• ***Edit defects period*** - every _<input>_ seconds get images with "alerted" defects predictions if they occur _(30 by default)_ 🔁

• ***Watch stream*** - start defects detection & getting updates 📺
"""

    await message.answer(text, parse_mode='Markdown')
    await message.answer("To connect the stream click the button below🔽", reply_markup=connect)


# Help command handler
@dp.message_handler(Text(equals=["Help", "/help"]))
async def process_start_command(message: types.Message):
    text = """
The steps to start bot: 🏁
--------------------------------------------------------
• ***Connect stream*** - connects your stream link 🌐

• ***Edit notifications period*** - every _<input>_ seconds get images with predictions _(600 by default)_ ♾️

• ***Edit defects period*** - every _<input>_ seconds get images with "alerted" defects predictions if they occur _(30 by default)_ 🔁

• ***Watch stream*** - start defects detection & getting updates 📺
--------------------------------------------------------


Commands inside ***Watch stream***:
--------------------------------------------------------
• ***Unmute defects notifications*** - unmutes defects detection if muted _(unmuted by default)_ 🔊

• ***Mute defects notifications*** - mutes defects detection if not muted 🔇

• ***Get only scheduled notifications*** - turn off alert defects updates 📅

• ***Get all notifications*** - get all updates _(all by default)_ 🔔

• ***Stop stream*** - stop getting updates 🎬
--------------------------------------------------------

Enjoy 🍿
    """

    await message.reply(text, parse_mode="Markdown")
    await message.answer("To set the stream click one of the buttons below🔽", reply_markup=reconnect_editPeriods_watch_help)


# Connnect stream command & user registration in db
@dp.message_handler(Text(equals=["Connect stream", "Reconnect stream", "/connect_stream"]))
async def cmd_dialog_stream(message: types.Message):
    await Stream.stream_link.set()  # states start working
    await message.reply("Input the link to your stream: ", reply=False)

@dp.message_handler(state=Stream.stream_link)
async def stream(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        stream_link = data['text']
        print(stream_link)  # as log

        # Check if stream active, if not - reconnect or watch previous successfully connected stream
        cap = cv2.VideoCapture(stream_link)
        ret, frame = cap.read()
        if not ret or frame is None:
            await message.answer(
                "Stream is not connected, something went wrong...", disable_notification=False, reply_markup=reconnect_editPeriods_watch_help)
            dp.current_state(user=message.from_user.id)
            await state.reset_state()

        else:
            if not db.user_exists(message.from_user.id):
                # if user not in db then add it
                db.add_user(user_id=message.from_user.id, status=False, stream=stream_link)
            else:
                # if user already in db then update it
                db.update_stream(user_id=message.from_user.id, status=False, stream=stream_link)

            # Stream successfully connected
            await message.answer(
                "Stream link is active...", reply_markup=reconnect_editPeriods_watch_help)

            # Close state
            dp.current_state(user=message.from_user.id)
            await state.reset_state()


# Start stream command
@dp.message_handler(Text(equals=["Watch stream", "/watch"]))
async def subscribe(message: types.Message):
    if not db.user_exists(message.from_user.id):
        # if user not in db then add it
        db.add_user(user_id=message.from_user.id, status=True)

    else:
        # if user already in db then update it
        db.update_status(user_id=message.from_user.id, status=True)

    await message.answer(
        "Stream starting...")
    await message.answer("Now you will get periodical notifications and defects messages when they occur!")
    await message.answer("To modify the stream click one of the buttons below🔽",
                         reply_markup=stream_managing)


# Stop stream command
@dp.message_handler(Text(equals=["Stop stream", "/stop"]))
async def unsubscribe(message: types.Message):
    if not db.user_exists(message.from_user.id):
        # if user not in db then just write it to db with non-active status
        db.add_user(user_id=message.from_user.id, status=False)
        await message.answer("You are not watching stream yet!", disable_notification=False)

    else:
        # if user in db then update his status to non-active
        db.update_status(user_id=message.from_user.id, status=False)

        await message.answer("Stopping stream...", reply_markup=reconnect_editPeriods_watch_help)


# Set notification period & user registration in db
@dp.message_handler(Text(equals=["Notification period", "/notification_period", "Edit notifications period"]))
async def cmd_dialog_notifications(message: types.Message):
    await Notification.notifications_period.set()  # вот мы указали начало работы состояний (states)
    await message.reply("Every N seconds you will get the notification independently on result\nInput N: ", reply=False)

@dp.message_handler(state=Notification.notifications_period)
async def notification_period(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        time = data['text']
        try:
            time = int(time)
            if time < T or time > 20000:

                # if time input is integer but less than update period

                text = f"""
Defects period is not updated. Please, input the integer in range 
_[{T}; 20000]_"""

                await message.answer(
                    text=text,
                    reply_markup=reconnect_editPeriods_watch_help,
                    parse_mode="Markdown")
                dp.current_state(user=message.from_user.id)
                await state.reset_state()

            else:

                # if time input is correct
                if not db.user_exists(message.from_user.id):
                    # if user not in db then add it
                    db.add_user(user_id=message.from_user.id, status=False)
                    db.update_notifications_period(user_id=message.from_user.id, status=False,
                                                   notifications_period=time)
                else:
                    # if user already in db then update it
                    db.update_notifications_period(user_id=message.from_user.id, status=False, notifications_period=time)

                await message.answer(
                    "Notification period is updated...", reply_markup=reconnect_editPeriods_watch_help)

                dp.current_state(user=message.from_user.id)
                await state.reset_state()

        except:

            # if time input cannot be converted to integer
            await message.answer(
                "Notification period is not updated. Please, input the integer...", reply_markup=reconnect_editPeriods_watch_help)
            dp.current_state(user=message.from_user.id)
            await state.reset_state()


# set defects period plus user registration in db
@dp.message_handler(Text(equals=["Defects period", "/defects_period", "Edit defects period"]))
async def cmd_dialog_defects(message: types.Message):
    await Defect.defects_period.set()  # вот мы указали начало работы состояний (states)
    await message.reply("Once you get defects notification, you will get it every K seconds\nInput K: ", reply=False)

@dp.message_handler(state=Defect.defects_period)
async def defect_period(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        time = data['text']

        try:
            time = int(time)

            if time < T or time > 20000:

                # if time input is integer but less than update period

                text = f"""
Defects period is not updated. Please, input the integer in range 
_[{T}; 20000]_"""
                await message.answer(
                    text=text,
                    reply_markup=reconnect_editPeriods_watch_help, parse_mode="Markdown")
                dp.current_state(user=message.from_user.id)
                await state.reset_state()

            else:

                # if time input is correct
                if not db.user_exists(message.from_user.id):
                    # if user not in db then add it
                    db.add_user(user_id=message.from_user.id, status=False)
                    db.update_defects_period(user_id=message.from_user.id, status=False,
                                             defects_period=time)
                else:
                    # if user already in db then update it
                    db.update_defects_period(user_id=message.from_user.id, status=False,
                                             defects_period=time)

                await message.answer(
                    "Defects period is updated...", reply_markup=reconnect_editPeriods_watch_help)

                dp.current_state(user=message.from_user.id)
                await state.reset_state()

        except:

            # if time input cannot be converted to integer
            await message.answer(
                "Defects period is not updated. Please, input the integer...",
                reply_markup=reconnect_editPeriods_watch_help)
            dp.current_state(user=message.from_user.id)
            await state.reset_state()


# Mute alert notifications (prob >= Q) command
@dp.message_handler(Text(equals=["Mute defects notifications", "/mute_defects_notifications"]))
async def mute(message: types.Message):

    db.update_mute(user_id=message.from_user.id, defects_mute=True)
    await message.answer(
        "Now your notifications are muted...", reply_markup=stream_managing)


# Unmute alert notifications command
@dp.message_handler(Text(equals=["Unmute defects notifications", "/unmute_defects_notifications"]))
async def unmute(message: types.Message):

    db.update_mute(user_id=message.from_user.id, defects_mute=False)
    await message.answer(
        "Now your notifications are loud...", reply_markup=stream_managing)


# Not to detect defects command (only scheduled notifications)
@dp.message_handler(Text(equals=["Get only scheduled notifications", "/get_scheduled"]))
async def stop_defects(message: types.Message):

    db.update_defects_detect(user_id=message.from_user.id, detect_defects=False)
    await message.answer(
        "Now you will only receive scheduled notifications...", reply_markup=stream_managing)


# Detect defects command (all notifications)
@dp.message_handler(Text(equals=["Get all notifications", "/get_all"]))
async def start_defects(message: types.Message):

    db.update_defects_detect(user_id=message.from_user.id, detect_defects=True)
    await message.answer(
        "Now you will also receive notifications about possible defects...", reply_markup=stream_managing)


async def defects_check(T):
    while True:

        # wait T seconds till next defects check happens (among all users)
        await asyncio.sleep(T)

        # get list of active watchers
        users = db.get_users()

        for user in users:
            """
            Column structure by index:
            0 - id
            1 - user_id (chat_id)
            2 - status (watching or not)
            3 - stream (stream_link)
            4 - notifications_period (in what time next notification appears independently on result)
            5 - predictions_since_last (number of predictions made since last prediction)
            6 - defects_period (in what time next notification about defect appears if last one was about defect as well)
            7 - defects_since_last (number of defects occured since last defect)
            8 - detect_defects (True if you want to get notifications when defects occur)
            9 - defects_mute (Mutes defects notifications)
            10 - connection_errors (Counts connection errors (in a row only))
            """

            stream_link = user[3]

            # get frame from stream
            cap = cv2.VideoCapture(stream_link)
            ret, frame = cap.read()

            if ret and frame is not None:

                # No connection errors
                db.update_connection_errors(user_id=user[1], connection_errors=0)

                # if video stream active, then continue detection
                if user[8]:

                    '''if we want to get all notifications, 
                    then we need check image for defects every T seconds'''
                    verdict, prob_yes_defects = get_prediction(img=frame, thresh=Q)

                    # Scheduled notifications
                    if user[5] * T >= user[4]:

                        # load photo to memory and push it to bot
                        bio = BytesIO()
                        bio.name = 'image.jpeg'
                        frame = np.flip(frame, axis=-1)
                        image = imget(frame)
                        image.save(bio, 'JPEG')
                        bio.seek(0)

                        await bot.send_photo(
                            user[1],
                            photo=bio,
                            caption=verdict + f'{prob_yes_defects * 100:.4f}%',
                            disable_notification=True
                        )
                        # if message is sent, then we start counting predictions again
                        db.update_predictions_since_last(user_id=user[1], predictions_since_last=1)
                    else:
                        # if time has not passed, then we increase predictions quantity
                        db.update_predictions_since_last(user_id=user[1], predictions_since_last=user[5] + 1)

                    # Defects notifications
                    if user[7] * T >= user[6] and prob_yes_defects >= Q:
                        print(f"defects! {user[1]}")
                        # load photo to memory and push it to bot
                        bio = BytesIO()
                        bio.name = 'image.jpeg'
                        frame = np.flip(frame, axis=-1)
                        image = imget(frame)
                        image.save(bio, 'JPEG')
                        bio.seek(0)

                        await bot.send_photo(
                            user[1],
                            photo=bio,
                            caption=verdict + f'{prob_yes_defects * 100:.4f}%',
                            disable_notification=user[9]
                        )
                        # if message is sent, then we start counting defects again
                        db.update_defects_since_last(user_id=user[1], defects_since_last=1)

                    elif prob_yes_defects >= Q:
                        # if current is with defects, then we increase its quantity
                        db.update_defects_since_last(user_id=user[1], defects_since_last=user[7] + 1)
                    else:
                        # if current is without defects, then we start counting them again
                        db.update_defects_since_last(user_id=user[1], defects_since_last=1)
                else:

                    '''if only scheduled notifications needed, 
                    then get predictions only when needed time is gone'''
                    if user[5] * T >= user[4]:
                        verdict, prob_yes_defects = get_prediction(img=frame, thresh=Q)
                        # load photo to memory and push it to bot
                        bio = BytesIO()
                        bio.name = 'image.jpeg'
                        frame = np.flip(frame, axis=-1)
                        image = imget(frame)
                        image.save(bio, 'JPEG')
                        bio.seek(0)

                        await bot.send_photo(
                            user[1],
                            photo=bio,
                            caption=verdict + f'{prob_yes_defects * 100:.4f}%',
                            disable_notification=True
                        )
                        db.update_predictions_since_last(user_id=user[1], predictions_since_last=1)
                    else:
                        db.update_predictions_since_last(user_id=user[1], predictions_since_last=user[5] + 1)

            elif not ret and user[10] + 1 < CONNECT_ERRORS_THRESH:

                '''if stream error, but its quantity is less than CONNECT_ERRORS_THRESH 
                then continue detection because its "fake" error'''
                db.update_connection_errors(user_id=user[1], connection_errors=user[10] + 1)

            else:

                '''if video stream not active, notify user'''
                db.update_status(user_id=user[1], status=False)
                db.update_connection_errors(user_id=user[1], connection_errors=0)
                await bot.send_message(
                    user[1],
                    text="Reconnect your stream, something went wrong...",
                    reply_markup=reconnect_editPeriods_watch_help
                )


if __name__ == '__main__':
    # create event loop
    loop = asyncio.get_event_loop()
    loop.create_task(defects_check(T))
    executor.start_polling(dp, skip_updates=True)

