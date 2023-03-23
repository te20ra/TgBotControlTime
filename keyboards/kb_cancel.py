from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
button_back = KeyboardButton('/Отмена')
button_case_add = ReplyKeyboardMarkup(resize_keyboard=True).insert(button_back)
