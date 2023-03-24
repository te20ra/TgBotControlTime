from aiogram import types, Dispatcher
from create_bot import bot
from keyboards import kb_week_days, kb_time, kb_cancel
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from data_base import sqlite_db_time
from create_bot import sheduler, dp
from handlers.apsched import add_job_sheduler
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from handlers.other import time_chek, rename_days
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
        if day == 'ready' and data['days'] != '':
            await FSM_time.next()
            await callback_query.answer()
            await bot.send_message(callback_query.from_user.id, 'Теперь введи время в формате "12:34"')
            data['days'] = data['days'][:-2]
            days = rename_days(data['days'])[:-2]
            await bot.edit_message_text(f'Выбранные дни: {days}', callback_query.from_user.id, msgid,
                                        reply_markup='')
            del data['msgid']
        elif day == 'ready' and data['days'] == '':
            await callback_query.answer('Необходимо выбрать дни',show_alert=True)
        elif day in data['days']:
            data['days'] = data['days'].replace(f'{day}, ','')
            await callback_query.answer('День удален')
            if data['days'] != "":
                days = rename_days(data['days'][:-2])[:-2]
            else:
                days =""
            await bot.edit_message_text(f'Выбранные дни: {days}', callback_query.from_user.id, msgid,
                                        reply_markup=kb_week_days.button_case_add)
        elif day not in data['days']:
            data['days'] += f'{day}, '
            await callback_query.answer('День добавлен')
            days = rename_days(data['days'][:-2])[:-2]
            await bot.edit_message_text(f'Выбранные дни: {days}', callback_query.from_user.id, msgid,
                                        reply_markup=kb_week_days.button_case_add)



async def add_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
    if time_chek(data['time']) == True:
        async with state.proxy() as data:
            days = rename_days(data['days'])[:-2]
            await bot.send_message(message.from_user.id, f'Напоминание добавлено \nДни: {days}\nВремя: {data["time"]}\nСтатус: ON',reply_markup=kb_time.button_case_add)
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
    await callback_query.message.delete()
    await sqlite_db_time.sql_alarm_no(id_sql)
    await callback_query.answer('Напоминание выполнено')


async def delete_job(message: types.Message):
    read = await sqlite_db_time.sql_time_read_to_delete(message)
    for ret in read:
        days = rename_days(ret[2])[:-2]
        await bot.send_message(message.from_user.id, text=f'НАПОМИНАНИЕ: {ret[1]}\nДни: {days}\nВремя: {ret[3]}\nСтатус: {ret[4]}', reply_markup=\
        InlineKeyboardMarkup().add(InlineKeyboardButton('Удалить', callback_data=f'del_time {ret[0]}')))


async def del_game(callback_query: types.CallbackQuery):
    id_sql = callback_query.data.replace('del_time ', '')
    await sqlite_db_time.sql_time_delete(id_sql)
    await callback_query.answer('deleted')
    await callback_query.message.delete()
    sheduler.remove_job(f'job {id_sql}')



async def time_menu(message: types.Message):
    menu = await sqlite_db_time.sql_time_read_menu(message)
    if len(menu) > 0:
        for ret in menu:
            days = rename_days(ret[2])[:-2]
            await bot.send_message(message.from_user.id, f'Напоминание: {ret[1]}\nДни: {days}\nВремя: {ret[3]}\nСтатус: {ret[4]}',
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Остановить',
             callback_data=f'job_p_{ret[0]}'))
            .add(InlineKeyboardButton('Возобновить', callback_data=f'job_r_{ret[0]}')))
    else:
        await bot.send_message(message.from_user.id, 'Для начала необходимо добавить напоминание')

async def job_pause(callback_query: types.CallbackQuery):
    idsql = callback_query.data.replace('job_p_', '')
    ret = (await sqlite_db_time.sql_time_one_line(idsql))[0]
    days = rename_days(ret[1])[:-2]
    if ret[-1] == 'ON':
        await sqlite_db_time.sql_time_status_OFF(idsql)
        await callback_query.answer()
        sheduler.pause_job(f'job {idsql}')
        await callback_query.message.edit_text(f'Напоминание: {ret[0]}\nДни: {days}\nВремя: {ret[2]}\nСтатус: OFF',
                                               reply_markup=InlineKeyboardMarkup().add(
                                                   InlineKeyboardButton('Остановить',
                                                                        callback_data=f'job_p_{idsql}'))
                                               .add(InlineKeyboardButton('Возобновить',
                                                                         callback_data=f'job_r_{idsql}'))
                                               )
    else:
        await callback_query.answer('Напоминание уже остановлено')


async def job_resume(callback_query: types.CallbackQuery):
    idsql = callback_query.data.replace('job_r_', '')
    ret = (await sqlite_db_time.sql_time_one_line(idsql))[0]
    days = rename_days(ret[1])[:-2]
    if ret[-1] == 'OFF':
        await sqlite_db_time.sql_time_status_ON(idsql)
        await callback_query.answer()
        sheduler.resume_job(f'job {idsql}')
        await callback_query.message.edit_text(f'Напоминание: {ret[0]}\nДни: {days}\nВремя: {ret[2]}\nСтатус: ON',
                                               reply_markup=InlineKeyboardMarkup().add(
                                                   InlineKeyboardButton('Остановить',
                                                                        callback_data=f'job_p_{idsql}'))
                                               .add(InlineKeyboardButton('Возобновить',
                                                                         callback_data=f'job_r_{idsql}'))
                                               )
    else:
        await callback_query.answer('Напоминание уже возобнавлено')

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
    dp.register_callback_query_handler(job_pause,lambda x: x.data and x.data.startswith('job_p_'))
    dp.register_callback_query_handler(job_resume, lambda x: x.data and x.data.startswith('job_r_'))