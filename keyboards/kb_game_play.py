from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
button_start = KeyboardButton('/Старт')
button_back = KeyboardButton('/Назад')

button_case_add = ReplyKeyboardMarkup(resize_keyboard=True).add(button_start).add(button_back)
