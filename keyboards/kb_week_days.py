from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

buttons = [InlineKeyboardButton('ПН', callback_data='day_mon'),
           InlineKeyboardButton('ВТ', callback_data='day_tue'),
           InlineKeyboardButton('СР', callback_data='day_wed'),
           InlineKeyboardButton('ЧТ', callback_data='day_thu'),
           InlineKeyboardButton('ПТ', callback_data='day_fri'),
           InlineKeyboardButton('СБ', callback_data='day_sat'),
           InlineKeyboardButton('ВС', callback_data='day_sun')]
button_case_add = InlineKeyboardMarkup(row_width=3).row(*buttons).add(InlineKeyboardButton('Дни выбраны', callback_data='day_ready'))

