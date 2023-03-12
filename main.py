import logging
import os
import random
import sqlite3

from aiogram import Bot
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

import db
from habits import add_habit, get_user_habits

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("/start"))
keyboard.add(KeyboardButton("/help"))
keyboard.add(KeyboardButton("/quote"))
keyboard.add(KeyboardButton("/habit"))
keyboard.add(KeyboardButton("/myhabits"))

storage = MemoryStorage()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot, storage=storage)

# Set up logging
logging.basicConfig(level=logging.INFO)

quotes = [
    "I eat Green Berets for breakfast. And right now, I'm very hungry!",
    "Remember, Sully, when I promised to kill you last? I lied.",
    "Let off some steam, Bennett.",
    "Don't Worry",
    "You Can't Drive That Car In There",
    "If it bleeds, we can kill it",
    "Hasta la vista, baby!",
    "Come with me if you want to live."
]


try:
    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {db.TABLE_NAME} (
        {db.COLUMN_ID} INTEGER PRIMARY KEY,
        {db.COLUMN_NAME} TEXT NOT NULL,
        {db.COLUMN_DESCRIPTION} TEXT NOT NULL,
        {db.COLUMN_DAYS} INTEGER NOT NULL,
        {db.COLUMN_DIFFICULTY} TEXT NOT NULL,
        {db.COLUMN_USER_ID} INTEGER NOT NULL
    )
''')
    conn.commit()
    cursor.close()
    conn.close()
except sqlite3.Error as error:
    print(f"Error while creating database: {error}")


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("Welcome to Commando Bot. Use /help to see the list of available commands.")


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    help_text = "The following commands are available:\n"
    help_text += "/start - Start the bot\n"
    help_text += "/help - Get help\n"
    help_text += "/quote - Get a random quote from Commando movie\n"
    help_text += "/habit - Add new habits\n"
    help_text += "/myhabits - Check my habits\n"
    await message.reply(help_text)


@dp.message_handler(commands=['quote'])
async def quote_command(message: types.Message):
    quote = random.choice(quotes)
    await message.reply(quote)


class HabitState(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_days = State()
    waiting_for_difficulty = State()


@dp.message_handler(commands=['habit'])
async def habit_command(message: types.Message):
    await message.answer("Enter the habit name:")
    await HabitState.waiting_for_name.set()


@dp.message_handler(state=HabitState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        await message.answer("Enter the habit description:")
        await HabitState.waiting_for_description.set()


@dp.message_handler(state=HabitState.waiting_for_description)
async def process_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
        await message.answer("Enter the number of days to track the habit:")
        await HabitState.waiting_for_days.set()


@dp.message_handler(state=HabitState.waiting_for_days)
async def process_days(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['days'] = message.text
        await message.answer("Enter the difficulty level (low, medium, or high):")
        await HabitState.waiting_for_difficulty.set()


@dp.message_handler(state=HabitState.waiting_for_difficulty)
async def process_difficulty(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['difficulty'] = message.text
        await message.answer("Habit added:")
        await message.answer(f"Name: {data['name']}\n"
                              f"Description: {data['description']}\n"
                              f"Days to track: {data['days']}\n"
                              f"Difficulty level: {data['difficulty']}\n")

        # Call add_habit to add the habit to the database
        add_habit(data[db.COLUMN_NAME], data[db.COLUMN_DESCRIPTION], data[db.COLUMN_DAYS], data[db.COLUMN_DIFFICULTY], message.from_user.id)
        await state.finish()


@dp.message_handler(commands=['myhabits'])
async def get_habits(message: types.Message):
    user_id = message.from_user.id
    habits = get_user_habits(user_id)
    if habits:
        habits_text = "\n".join([f"💪<b>{habit.name}:</b> {habit.description}\n"
                                 f"⏳ <b>Days:</b> {habit.days}\n"
                                 f"🛠 <b>Difficulty:</b> {habit.difficulty}\n"
                                 for habit in habits])
        await message.answer(f"<b>🗂 Your habits:</b>\n\n{habits_text}",
                              parse_mode='HTML', reply_markup=keyboard)
    else:
        await message.answer("You don't have any habits yet.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
