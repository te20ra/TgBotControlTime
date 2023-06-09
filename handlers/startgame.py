from aiogram import types, Dispatcher
from create_bot import bot, sheduler, dp
from data_base import sqlite_db
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime
from datetime import timedelta
from pytz import timezone
from keyboards import kb_main
from aiogram.dispatcher import FSMContext
from handlers.apsched import check_timeout


class FsmStart(StatesGroup):
    start = State()


async def select_game(message: types.Message):
    read = await sqlite_db.sql_read_to_start_game(message.from_user.id)
    status = await sqlite_db.sql_status_check_all(message.from_user.id)
    st = []
    for i in status:
        st.append(i[0])
    print(st)
    if 'active' in st:
        await bot.send_message(message.from_user.id, 'Другая игра активна. Закончи ее')
    elif len(read) > 0:
        await bot.send_message(message.from_user.id, 'Вы перешли в режим выбора игры')
        for ret in read:
            await bot.send_message(message.from_user.id, text=f'{ret[0]}:  {ret[1]}  /  {ret[2]}', reply_markup= \
                InlineKeyboardMarkup().add(InlineKeyboardButton('Выбрать', callback_data=f'select {ret[0]}')))
    else:
        await bot.send_message(message.from_user.id, 'Нет доступных игр')




async def game_selcted(callback_query: types.CallbackQuery):
    game = callback_query.data.replace("select ", "")
    await callback_query.answer()
    await FsmStart.start.set()
    await sqlite_db.sql_status_active(callback_query.from_user.id, game)
    await bot.send_message(callback_query.from_user.id, f'Нажмите на "/Старт" для начала отсчета таймера игры "{game}"',
                           reply_markup= InlineKeyboardMarkup().add(InlineKeyboardButton('Старт', callback_data=f'gamestart_{game}')))


async def game_started(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    game = callback_query.data.replace("gamestart_", "")
    iduser = callback_query.from_user.id
    starttime = datetime.now()
    id_sql = await sqlite_db.sql_return_id_sql(iduser, game)
    maxtime = await sqlite_db.sql_maxtime(id_sql)
    spend_time = await sqlite_db.sql_spend_time(id_sql)
    last_time = starttime + timedelta(minutes=maxtime-spend_time)
    await sqlite_db.sql_do_last_time(str(last_time), id_sql)
    sheduler.add_job(check_timeout, 'interval', seconds=60, id=f'timeout {id_sql}', args=(dp,), max_instances=1,
                     kwargs={'iduser': iduser,
                             'id_sql': id_sql,
                             'last_time': last_time,
                             'starttime': starttime})

    last_time =last_time.astimezone(timezone('Europe/Moscow')).strftime('%H:%M')
    await callback_query.message.edit_text(f'У тебя есть время до {last_time}\nКак закончишь играть, нажми на кнопку', reply_markup= \
        InlineKeyboardMarkup().add(InlineKeyboardButton('СТОП', callback_data=f'stopgame_{id_sql}_{str(starttime)}')))


async def game_stoped(callback_query: types.CallbackQuery):
    line = callback_query.data.split('_')
    id_sql = line[1]
    starttime = datetime.strptime(line[2].split('.')[0], '%Y-%m-%d %H:%M:%S')
    timespend = ((datetime.now()) - starttime).seconds // 60
    await sqlite_db.sql_status_sleep(id_sql)
    await sqlite_db.sql_update_spendtime(id_sql, timespend)
    await callback_query.answer("GG")
    await bot.send_message(callback_query.from_user.id, f'Таймер остановлен\nВы провели в игре {timespend} минут',
                           reply_markup=kb_main.button_case_add)
    await sqlite_db.sql_do_last_time('', id_sql)
    await callback_query.message.delete()



async def game_exit(message: types.Message):
    await bot.send_message(message.from_user.id, 'Вы в главном меню', reply_markup=kb_main.button_case_add)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(select_game, commands='Начать_игру')
    dp.register_callback_query_handler(game_selcted, lambda x: x.data and x.data.startswith('select'))
    dp.register_callback_query_handler(game_started, lambda x: x.data and x.data.startswith('gamestart'), state=FsmStart.start)
    dp.register_callback_query_handler(game_stoped, lambda x: x.data and x.data.startswith('stopgame'))
    dp.register_message_handler(game_exit, commands='Назад')
