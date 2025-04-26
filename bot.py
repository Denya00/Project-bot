from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
import json
import logging
from config import TOKEN
from commands import *
from keyboards import *
from reminder import Reminder
import re

with open("data.json") as f:
    exercise_data = json.load(f)["exercises"]

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
reminder = Reminder(bot)

class WorkoutStates(StatesGroup):
    select_level = State()
    select_category = State()
    select_duration = State()
    set_reminder = State()

@dp.message(START_COMMAND)
async def start_command(message: types.Message):
    await message.answer(
        "Welcome! I'm GymGen bot! I will help to generate new workout for ya =)\n\n"
        "Available commands:\n"
        "/create_workout_plan - Create workout\n"
        "/set_reminder - Set reminders"
    )

@dp.message(CREATE_WORKOUT_COMMAND)
async def create_workout(message: types.Message, state: FSMContext):
    await state.set_state(WorkoutStates.select_level)
    await message.answer("Select your level:", reply_markup=level_keyboard())

@dp.message(WorkoutStates.select_level)
async def process_level(message: types.Message, state: FSMContext):
    level = message.text.lower()
    if level not in ["beginner", "intermediate", "advanced"]:
        await message.answer("Please use the buttons!")
        return
    
    await state.update_data(level=level)
    await state.set_state(WorkoutStates.select_category)
    await message.answer("Choose category:", reply_markup=category_keyboard())

@dp.message(WorkoutStates.select_category)
async def process_category(message: types.Message, state: FSMContext):
    category = message.text.lower().replace(" ", "_")
    valid_categories = ["full_body", "upper_body", "lower_body", "cardio"]
    
    if category not in valid_categories:
        await message.answer("Invalid choice!")
        return
    
    await state.update_data(category=category)
    await state.set_state(WorkoutStates.select_duration)
    await message.answer("Select duration:", reply_markup=duration_keyboard())

@dp.message(WorkoutStates.select_duration)
async def process_duration(message: types.Message, state: FSMContext):
    try:
        duration = int(message.text)
        if duration not in [15, 30, 45, 60]:
            raise ValueError
        
        data = await state.get_data()
        level = data['level']
        category = data['category']
        
        exercises = exercise_data[level][category]
        selected = []
        total_time = 0
        
        remaining_time = duration * 60
        for ex in exercises:
            if ex['duration'] <= remaining_time:
                selected.append(ex)
                remaining_time -= ex['duration']
                if remaining_time <= 0:
                    break
        
        if not selected:
            await message.answer("No exercises found for this duration!")
            return
        
        workout_text = f"🏋️ {duration}min {level.title()} {category.replace('_', ' ')} Workout:\n\n"
        workout_text += "\n".join([f"{idx+1}. {ex['text']}" for idx, ex in enumerate(selected)])
        
        await message.answer(workout_text)
        
        for idx, ex in enumerate(selected, 1):
            await asyncio.sleep(1) 
            await message.answer_photo(
                ex['thumbnail'],
                caption=f"Demo for exercise {idx}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Watch Video", url=ex['video'])]
                ])
            )
        
        await state.clear()
        
    except ValueError:
        await message.answer("Please use buttons: 15, 30, 45 or 60")

@dp.message(SET_REMINDER_COMMAND)
async def set_reminder(message: types.Message, state: FSMContext):
    await state.set_state(WorkoutStates.set_reminder)
    await message.answer("Choose reminder time:", reply_markup=reminder_time_keyboard())

@dp.message(WorkoutStates.set_reminder)
async def process_reminder(message: types.Message, state: FSMContext):
    try:
        time_str = message.text
        hour, minute = map(int, time_str.split(':'))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError
        
        await reminder.schedule_reminder(
            chat_id=message.chat.id,
            hour=hour,
            minute=minute
        )
        await message.answer(f"Reminder set for {time_str}")
        await state.clear()
        
    except (ValueError, IndexError):
        await message.answer("Invalid format! Use HH:MM")

async def on_shutdown():
    await reminder.shutdown()

async def main():
    try:
        reminder.start() 
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_my_commands([ 
            types.BotCommand(command="start", description="Start bot"),
            types.BotCommand(command="create_workout_plan", description="Create workout"),
            types.BotCommand(command="set_reminder", description="Set reminders"),
        ])
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        reminder.shutdown() 
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")