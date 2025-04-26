from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def level_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Beginner")],
            [KeyboardButton(text="Intermediate")],
            [KeyboardButton(text="Advanced")]
        ],
        resize_keyboard=True
    )

def category_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Full Body")],
            [KeyboardButton(text="Upper Body")],
            [KeyboardButton(text="Lower Body")],
            [KeyboardButton(text="Cardio")]
        ],
        resize_keyboard=True
    )

def duration_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="15"), KeyboardButton(text="30")],
            [KeyboardButton(text="45"), KeyboardButton(text="60")]
        ],
        resize_keyboard=True
    )

def reminder_time_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="07:00"), KeyboardButton(text="12:00")],
            [KeyboardButton(text="18:00"), KeyboardButton(text="20:00")]
        ],
        resize_keyboard=True
    )