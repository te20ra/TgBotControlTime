from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
button_delete = KeyboardButton('/Удалить_игру')
button_back = KeyboardButton('/Главное_меню')

button_case_add = ReplyKeyboardMarkup(resize_keyboard=True).add(button_delete).insert(button_back)
