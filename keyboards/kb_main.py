from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
button_game = KeyboardButton('/game')
button_help = KeyboardButton('/help')
button_time = KeyboardButton('/time')

#button_start_game = KeyboardButton('/game_start')
#button_menu = KeyboardButton('/menu')

button_case_add = ReplyKeyboardMarkup(resize_keyboard=True).add(button_game).insert(button_time).add(button_help)