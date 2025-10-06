from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

TYPE_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Income"), KeyboardButton(text="Expense")]],
    one_time_keyboard=False,
)
