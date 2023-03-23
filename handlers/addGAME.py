from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import bot
from keyboards import kb_add_game3, kb_add_game2, kb_cancel, kb_main
from data_base import sqlite_db
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text

class FSM_user(StatesGroup):
    game = State()
    maxtime = State()


async def mode_menu(message: types.Message):
    count = await sqlite_db.sql_count(message.from_user.id)
    if count < 10:
        await bot.send_message(message.from_user.id, 'Вы перешли в режим редактирования. Выберете действие',
                           reply_markup=kb_add_game3.button_case_add)
    else:
        await bot.send_message(message.from_user.id, 'Вы перешли в режим редактирования. Выберете действие',
                               reply_markup=kb_add_game2.button_case_add)


async def add_game_start(message: types.Message):
    await FSM_user.game.set()
    await message.reply('Введите название игры', reply_markup=kb_cancel.button_case_add)


async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('ОК', reply_markup=kb_main.button_case_add)


async def add_game_name(message : types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['iduser'] = message.from_user.id
        data['name'] = message.text
        if await sqlite_db.sql_search(data['name'], data['iduser']) == 0 and len(data['name']) <= 30 and not data['name'].isdigit():
            await FSM_user.next()
            await message.reply('Теперь введите лимит времени в сутки (в минутах)\n'
                                '*число от 1 до 180')
        elif len(data['name']) > 30:
            await bot.send_message(message.from_user.id,
                                   f'Название игры слишком длинное. Напиши короче (не более 30 символов)')
        elif data['name'].isdigit():
            await bot.send_message(message.from_user.id,
                                   f'Название игры не может состоять только из цифр. Напиши иначе')
        else:
            await bot.send_message(message.from_user.id,
                                   f'Игра с именем "{data["name"]}" уже есть. Введите игру заново')

async def add_game_maxtime(message : types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['spendtime'] = 0
        data['maxtime'] = message.text
    if data['maxtime'].isdigit() and 0 < int(data['maxtime']) <= 180:
        await sqlite_db.sql_add(state)
        await state.finish()
        count = await sqlite_db.sql_count(message.from_user.id)
        if count < 10:
            await bot.send_message(message.from_user.id, f'Игра "{data["name"]}" с лимтом времени "{data["maxtime"]}" добавлена',
                               reply_markup=kb_add_game3.button_case_add)
        else:
            await bot.send_message(message.from_user.id,
                                   f'Игра "{data["name"]}" с лимтом времени "{data["maxtime"]}" добавлена',
                                  reply_markup=kb_add_game2.button_case_add)
    else:
        await bot.send_message(message.from_user.id,
                               'Необходимо ввести время в минутах от 0 до 180')


async def delete_game(message: types.Message):
    read = await sqlite_db.sql_read_to_delete(message)
    for ret in read:
        await bot.send_message(message.from_user.id, text=f'{ret[1]}:  {ret[2]}  /  {ret[3]}', reply_markup=\
        InlineKeyboardMarkup().add(InlineKeyboardButton('Удалить', callback_data=f'del {ret[0]}')))


async def del_game(callback_query: types.CallbackQuery):
    id_sql = callback_query.data.replace('del ', '')
    #name = await sqlite_db.sql_name(id_sql)
    await sqlite_db.sql_delete(id_sql)
    await callback_query.answer('deleted')
    #await bot.send_message(callback_query.from_user.id, f'Игра "{name}" удалена',
                           #reply_markup=kb_add_game3.button_case_add)
    await callback_query.message.delete()





def register_handlers(dp: Dispatcher):
    dp.register_message_handler(mode_menu, commands='Редактировать_игры')
    dp.register_message_handler(add_game_start, commands='Добавить_игру')
    dp.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state='*')
    dp.register_message_handler(cancel_handler, state="*", commands='Отмена')
    dp.register_message_handler(add_game_name, state=FSM_user.game)
    dp.register_message_handler(add_game_maxtime, state=FSM_user.maxtime)
    dp.register_message_handler(delete_game, commands='Удалить_игру')
    dp.register_callback_query_handler(del_game, lambda x: x.data and x.data.startswith('del '))



