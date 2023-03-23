from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
button_add = KeyboardButton('/Добавить_напоминание')
button_delete = KeyboardButton('/Удалить_напомнинание')
button_menu = KeyboardButton('/Показать_напоминания')
button_back = KeyboardButton('/Главное_меню')

#button_case_add = ReplyKeyboardMarkup(resize_keyboard=True).add(button_add).insert(button_delete).add(button_menu).insert(button_back)
button_case_add = ReplyKeyboardMarkup(resize_keyboard=True).add(button_add).add(button_delete).add(button_menu).add(button_back)