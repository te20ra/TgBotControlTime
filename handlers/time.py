from aiogram import types, Dispatcher
from create_bot import bot
from keyboards import kb_week_days, kb_time, kb_cancel
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from data_base import sqlite_db_time
#from aiogram.dispatcher.filters import Text
from create_bot import sheduler, dp
from handlers.apsched import add_job_sheduler
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime,timedelta

async def time_start(message: types.Message):
    await bot.send_message(message.from_user.id, "Вы в меню настройки напоминаний", reply_markup=kb_time.button_case_add)


class FSM_time(StatesGroup):
    name = State()
    day = State()
    time = State()

async def add_job(message: types.Message):
    await FSM_time.name.set()
    await bot.send_message(message.from_user.id, 'Введи название своего напоминания', reply_markup=kb_cancel.button_case_add)


async def add_name_job(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['iduser'] = message.from_user.id
        data['name_job'] = message.text
        data['days'] = ''
    if await sqlite_db_time.sql_time_search(data['name_job'], data['iduser']) == 0 and \
        len(data['name_job']) <= 100 and not data['name_job'].isdigit():
        await FSM_time.next()
        msg = await bot.send_message(message.from_user.id,'Выбери дни напоминания, а после нажми на кнопку "Дни выбраны"', reply_markup=kb_week_days.button_case_add)
        async with state.proxy() as data:
            data['msgid'] = msg.message_id
    elif len(data['name_job']) > 100:
        await bot.send_message(message.from_user.id,
                               f'Название напоминания слишком длинное. Напиши короче (не более 100 символов)')
    elif data['name_job'].isdigit():
        await bot.send_message(message.from_user.id,
                               f'Название напоминания не может состоять только из цифр. Напиши иначе')
    else:
        await bot.send_message(message.from_user.id,
                               f'Такое напоминане уже есть. Введите заново')


async def add_day(callback_query: types.CallbackQuery, state: FSMContext):
    day = callback_query.data.replace('day_','')
    async with state.proxy() as data:
        msgid = data['msgid']
        if day == 'ready':
            await FSM_time.next()
            await callback_query.answer()
            await bot.send_message(callback_query.from_user.id, 'Теперь введи время в формате "12:34"')
            data['days'] = data['days'][:-2]
            del data['msgid']
        elif day in data['days']:
            data['days'] = data['days'].replace(f'{day}, ','')
            await callback_query.answer('День удален')
            await bot.edit_message_text(f'Выбранные дни: {data["days"][:-2]}', callback_query.from_user.id, msgid,
                                        reply_markup=kb_week_days.button_case_add)
        elif day not in data['days']:
            data['days'] += f'{day}, '
            await callback_query.answer('День добавлен')
            await bot.edit_message_text(f'Выбранные дни: {data["days"][:-2]}', callback_query.from_user.id, msgid,
                                        reply_markup=kb_week_days.button_case_add)

def time_chek(time):
    if len(time) == 5:
        s1 = time[0:2]
        s2 = time[2]
        s3 = time[3:]
        if s1.isdigit() and 0 <= int(s1) <= 24 and s2 == ':' and s3.isdigit() and 00 <= int(s3) <=59:
            return True
        else:
            return False
    else:
        return False




async def add_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
    if time_chek(data['time']) == True:
        async with state.proxy() as data:
            await bot.send_message(message.from_user.id, f'Напоминание добавлено \nДни: {data["days"]}\nВремя: {data["time"]}\nСтатус: ON',reply_markup=kb_time.button_case_add)
            name = data['name_job']
            days = data['days'].strip().replace(' ','')
            data['time'] = datetime.strptime(data['time'], '%H:%M')
            data['time'] = data['time'] - timedelta(minutes=1)
            data['time'] = datetime.strftime(data['time'], '%H:%M')
            hour = data['time'].split(':')[0]
            minute = data['time'].split(':')[1]

            await sqlite_db_time.sql_time_new(state)
            idsql = await sqlite_db_time.sql_time_idsql(state)
            await state.finish()
            sheduler.add_job(add_job_sheduler, 'cron', day_of_week=days, hour=hour, minute=minute, id=f'job {idsql}', args=(dp,),
                     kwargs={'iduser': message.from_user.id,
                             'id_sql': idsql,
                             'name': name})


    else:
        await bot.send_message(message.from_user.id, 'Время введено неверно')


async def job_stop(callback_query: types.CallbackQuery):
    id_sql = callback_query.data.replace('job_stop_','')
    await sqlite_db_time.sql_alarm_no(id_sql)
    await callback_query.answer('Напоминание выполнено')


async def delete_job(message: types.Message):
    read = await sqlite_db_time.sql_time_read_to_delete(message)
    for ret in read:
        await bot.send_message(message.from_user.id, text=f'НАПОМИНАНИЕ: {ret[1]}\nДни: {ret[2]}\nВремя: {ret[3]}\nСтатус: {ret[4]}', reply_markup=\
        InlineKeyboardMarkup().add(InlineKeyboardButton('Удалить', callback_data=f'del_time {ret[0]}')))


async def del_game(callback_query: types.CallbackQuery):
    id_sql = callback_query.data.replace('del_time ', '')
    await sqlite_db_time.sql_time_delete(id_sql)
    sheduler.remove_job(f'job {id_sql}')
    await callback_query.answer('deleted')
    await callback_query.message.delete()

    ''' deleted = await sqlite_db_time.sql_time_deleted_check(id_sql)
     if deleted == 'No':
         await sqlite_db_time.sql_time_delete(id_sql)
         sheduler.remove_job(f'job {id_sql}')
         await callback_query.answer('deleted')
     elif deleted == 'Yes':
         await sqlite_db_time.sql_time_delete(id_sql)
         await callback_query.answer('deleted')
     status = await sqlite_db_time.sql_time_status_check(id_sql)
     if status == 'ON':
         await sqlite_db_time.sql_time_delete(id_sql)
         sheduler.remove_job(f'job {id_sql}')
         await callback_query.answer('deleted')
     elif status == 'OFF':
         await sqlite_db_time.sql_time_delete(id_sql)
         await callback_query.answer('deleted')
    '''

async def time_menu(message: types.Message):
    menu = await sqlite_db_time.sql_time_read_menu(message)
    if len(menu) > 0:
        for ret in menu:
            await bot.send_message(message.from_user.id, f'НАПОМИНАНИЕ: {ret[0]}\nДни: {ret[1]}\nВремя: {ret[2]}\nСтатус: {ret[3]}')
    else:
        await bot.send_message(message.from_user.id, 'Для начала необходимо добавить напоминание')


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(time_start, commands='time')
    dp.register_message_handler(add_job, commands='Добавить_напоминание')
    dp.register_message_handler(add_name_job, state=FSM_time.name)
    dp.register_callback_query_handler(add_day, lambda x: x.data and x.data.startswith('day_'), state=FSM_time.day)
    dp.register_message_handler(add_time, state=FSM_time.time)
    dp.register_callback_query_handler(job_stop, lambda x: x.data and x.data.startswith('job_stop_'))
    dp.register_message_handler(delete_job, commands='Удалить_напомнинание')
    dp.register_callback_query_handler(del_game, lambda x: x.data and x.data.startswith('del_time'))
    dp.register_message_handler(time_menu, commands='Показать_напоминания')