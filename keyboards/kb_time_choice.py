from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
button1 = InlineKeyboardButton('Однократное напоминание', callback_data='remaind_one')
button2 = InlineKeyboardButton('Многократное напоминание', callback_data='remaind_many')
button_case_add = InlineKeyboardMarkup(row_width=1).add(button1).add(button2)