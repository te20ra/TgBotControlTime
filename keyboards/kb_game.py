from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
button_back = KeyboardButton('/Главное_меню')
button_moder = KeyboardButton('/Редактировать_игры')
button_start_game = KeyboardButton('/Начать_игру')
button_menu = KeyboardButton('/Список_игр')

button_case_add = ReplyKeyboardMarkup(resize_keyboard=True).add(button_start_game).insert(button_menu).add(button_moder).insert(button_back)