from aiogram import types, Dispatcher
from create_bot import bot
from keyboards import kb_week_days, kb_time, kb_cancel, kb_time_choice
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from data_base import sqlite_db_time
from create_bot import sheduler, dp
from handlers.apsched import add_job_sheduler
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from handlers.other import time_chek, rename_days, date_check
async def time_start(message: types.Message):
    await bot.send_message(message.from_user.id, "Вы в меню настройки напоминаний", reply_markup=kb_time.button_case_add)


class FSM_time(StatesGroup):
    name = State()
    day = State()
    time = State()


class FSM_onetime(StatesGroup):
    name = State()
    date = State()
    time = State()


async def add_job_choise(message: types.Message):
    count = await sqlite_db_time.sql_time_count(message.from_user.id)
    if count < 20:
        await bot.send_message(message.from_user.id, 'Выбери тип напоминания', reply_markup=kb_time_choice.button_case_add)
    else:
        await bot.send_message(message.from_user.id, 'Вы не можете добавить напоминание, так как закночился их лимит (20)')


async def add_job(callback_query: types.CallbackQuery):
    count = await sqlite_db_time.sql_time_count(callback_query.from_user.id)
    await callback_query.message.delete()
    if count < 20:
        if callback_query.data.replace('remaind_','') == 'many':
            await FSM_time.name.set()
            await bot.send_message(callback_query.from_user.id, 'Введите название своего напоминания',
                               reply_markup=kb_cancel.button_case_add)
        elif callback_query.data.replace('remaind_','') == 'one':
            await FSM_onetime.name.set()
            await bot.send_message(callback_query.from_user.id, 'Введите название своего напоминания',
                                   reply_markup=kb_cancel.button_case_add)
    else:
        await bot.send_message(callback_query.from_user.id,
                               'Вы не можете добавить напоминание, так как закночился их лимит (20)')

async def add_name_job_onetime(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['iduser'] = message.from_user.id
        data['name_job'] = message.text
    if await sqlite_db_time.sql_time_search(data['name_job'], data['iduser']) == 0 and \
        len(data['name_job']) <= 100 and not data['name_job'].isdigit():
        await FSM_onetime.next()
        await bot.send_message(message.from_user.id,'Напиши дату напоминания в формате "2023-04-22')
    elif len(data['name_job']) > 100:
        await bot.send_message(message.from_user.id,
                               f'Название напоминания слишком длинное. Напишите короче (не более 100 символов)')
    elif data['name_job'].isdigit():
        await bot.send_message(message.from_user.id,
                               f'Название напоминания не может состоять только из цифр. Напишите иначе')
    else:
        await bot.send_message(message.from_user.id,
                               f'Такое напоминане уже есть. Введите заново')


async def add_date_onetime(message: types.Message, state: FSMContext):
    if await date_check(message.text) == True:
        async with state.proxy() as data:
            data['date'] = message.text
        await FSM_onetime.next()
        await bot.send_message(message.from_user.id, 'Теперь введи время в формате "12:34"\nМинимум плюс 2 минуты к настоящему времени')
    else:
        await bot.send_message(message.from_user.id, 'Дата введена неверно')


async def add_time_onetime(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
    if await time_chek(message.text, data['date']) == True:
        time = datetime.strptime(data['time'], '%H:%M')
        time = time - timedelta(minutes=1)
        time = datetime.strftime(time, '%H:%M:%S')
        print(time)
        await bot.send_message(message.from_user.id,
                           f'Напоминание добавлено \nДата: {data["date"]}\nВремя: {data["time"]}\nСтатус: ON',
                           reply_markup=kb_time.button_case_add)
        async with state.proxy() as data:
            data['date'] = 'date_' + data['date']
            name = data['name_job']
            date = data['date'].replace('date_', '')
        await sqlite_db_time.sql_time_new(state)
        idsql = await sqlite_db_time.sql_time_idsql(state)
        await state.finish()
        date = date + ' ' + time
        sheduler.add_job(add_job_sheduler, 'date', run_date=date, id=f'job {idsql}',
                         args=(dp,),
                         kwargs={'iduser': message.from_user.id,
                                 'id_sql': idsql,
                                 'name': name})
    else:
        await bot.send_message(message.from_user.id, 'Время введено неверно')

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
                               f'Название напоминания слишком длинное. Напишите короче (не более 100 символов)')
    elif data['name_job'].isdigit():
        await bot.send_message(message.from_user.id,
                               f'Название напоминания не может состоять только из цифр. Напишите иначе')
    else:
        await bot.send_message(message.from_user.id,
                               f'Такое напоминане уже есть. Введите заново')


async def add_day(callback_query: types.CallbackQuery, state: FSMContext):
    day = callback_query.data.replace('day_','')
    async with state.proxy() as data:
        msgid = data['msgid']
        if day == 'ready' and data['days'].replace('cron_', '') != '':
            await FSM_time.next()
            await callback_query.answer()
            await bot.send_message(callback_query.from_user.id, 'Теперь введи время в формате "12:34"\nМинимум плюс 2 минуты к настоящему времени')
            days = await rename_days(data['days'])
            await bot.edit_message_text(f'Выбранные дни: {days}', callback_query.from_user.id, msgid,
                                        reply_markup='')
            del data['msgid']
        elif day == 'ready' and data['days'] == '':
            await callback_query.answer('Необходимо выбрать дни', show_alert=True)
        elif day in data['days']:
            data['days'] = data['days'].replace(f'{day}, ','')
            await callback_query.answer('День удален')
            if data['days'] != "":
                days = await rename_days(data['days'])
            else:
                days = ""
            await bot.edit_message_text(f'Выбранные дни: {days}', callback_query.from_user.id, msgid,
                                        reply_markup=kb_week_days.button_case_add)
        elif day not in data['days']:
            data['days'] += f'{day}, '
            await callback_query.answer('День добавлен')
            days = await rename_days(data['days'])
            await bot.edit_message_text(f'Выбранные дни: {days}', callback_query.from_user.id, msgid,
                                        reply_markup=kb_week_days.button_case_add)



async def add_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
    if await time_chek(data['time']) == True:
        async with state.proxy() as data:
            days = await rename_days(data['days'])
            await bot.send_message(message.from_user.id, f'Напоминание добавлено \nДни: {days}\nВремя: {data["time"]}\nСтатус: ON',reply_markup=kb_time.button_case_add)
            name = data['name_job']
            days = data['days'].strip().replace(' ','')[:-1]
            time = datetime.strptime(data['time'], '%H:%M')
            time = time - timedelta(minutes=1)
            hour = time.hour
            minute = time.minute
            data['days'] = 'cron_' + days
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
    await callback_query.answer('Напоминание выполнено', show_alert=True)
    await callback_query.message.delete()


async def delete_job(message: types.Message):
    read = await sqlite_db_time.sql_time_read_to_delete(message)
    if len(read) == 0:
        await bot.send_message(message.from_user.id, 'Отсутствуют напоминания')
    else:
        for ret in read:

            if ret[2].startswith('cron') == True:
                days = await rename_days(ret[2])
                await bot.send_message(message.from_user.id, text=f'НАПОМИНАНИЕ: {ret[1]}\nДни: {days}\nВремя: {ret[3]}\nСтатус: {ret[4]}', reply_markup=\
        InlineKeyboardMarkup().add(InlineKeyboardButton('Удалить', callback_data=f'del_time {ret[0]}')))

            elif ret[2].startswith('date') == True:
                date = ret[2].replace('date_','')
                await bot.send_message(message.from_user.id,
                                       text=f'НАПОМИНАНИЕ: {ret[1]}\nДата: {date}\nВремя: {ret[3]}\nСтатус: {ret[4]}',
                                       reply_markup= \
                                           InlineKeyboardMarkup().add(
                                               InlineKeyboardButton('Удалить', callback_data=f'del_time {ret[0]}')))

async def del_time(callback_query: types.CallbackQuery):
    id_sql = callback_query.data.replace('del_time ', '')
    await sqlite_db_time.sql_time_delete(id_sql)
    await callback_query.answer('deleted')
    await callback_query.message.delete()
    sheduler.remove_job(f'job {id_sql}')



async def time_menu(message: types.Message):
    menu = await sqlite_db_time.sql_time_read_menu(message)
    if len(menu) > 0:
        for ret in menu:
            if ret[2].startswith('cron') == True:
                days = await rename_days(ret[2])
                await bot.send_message(message.from_user.id, f'Напоминание: {ret[1]}\nДни: {days}\nВремя: {ret[3]}\nСтатус: {ret[4]}',
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Остановить',
                callback_data=f'job_p_{ret[0]}')).add(InlineKeyboardButton('Возобновить', callback_data=f'job_r_{ret[0]}')))

            elif ret[2].startswith('date') == True:
                date = ret[2].replace('date_', '')
                await bot.send_message(message.from_user.id,
                    f'Напоминание: {ret[1]}\nДата: {date}\nВремя: {ret[3]}\nСтатус: {ret[4]}',
                    reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Остановить',
                    callback_data=f'job_p_{ret[0]}')).add(InlineKeyboardButton('Возобновить', callback_data=f'job_r_{ret[0]}')))
    else:
        await bot.send_message(message.from_user.id, 'Для начала необходимо добавить напоминание')

async def job_pause(callback_query: types.CallbackQuery):
    idsql = callback_query.data.replace('job_p_', '')
    ret = (await sqlite_db_time.sql_time_one_line(idsql))[0]
    days = await rename_days(ret[1])
    if ret[-1] == 'ON' and ret[-2] == 'No':
        await sqlite_db_time.sql_time_status_OFF(idsql)
        await callback_query.answer()
        sheduler.pause_job(f'job {idsql}')
        ndays = ''
        if ret[1].startswith('cron'):
            ndays = 'Дни'
        elif ret[1].startswith('date'):
            ndays = 'Дата'
        await callback_query.message.edit_text(f'Напоминание: {ret[0]}\n{ndays}: {days}\nВремя: {ret[2]}\nСтатус: OFF',
                                               reply_markup=InlineKeyboardMarkup().add(
                                                   InlineKeyboardButton('Остановить',
                                                                        callback_data=f'job_p_{idsql}'))
                                               .add(InlineKeyboardButton('Возобновить',
                                                                         callback_data=f'job_r_{idsql}'))
                                               )
    elif ret[-1] == 'ON' and ret[-2] == 'Yes':
        await callback_query.answer('Сначала необходимо завершить данное напомниние')
    else:
        await callback_query.answer('Напоминание уже остановлено')


async def job_resume(callback_query: types.CallbackQuery):
    idsql = callback_query.data.replace('job_r_', '')
    ret = (await sqlite_db_time.sql_time_one_line(idsql))[0]
    days = await rename_days(ret[1])
    if ret[-1] == 'OFF' and ret[-2] == 'No':
        await sqlite_db_time.sql_time_status_ON(idsql)
        await callback_query.answer()
        sheduler.resume_job(f'job {idsql}')
        ndays = ''
        if ret[1].startswith('cron'):
            ndays = 'Дни'
        elif ret[1].startswith('date'):
            ndays = 'Дата'
        await callback_query.message.edit_text(f'Напоминание: {ret[0]}\n{ndays}: {days}\nВремя: {ret[2]}\nСтатус: ON',
                                               reply_markup=InlineKeyboardMarkup().add(
                                                   InlineKeyboardButton('Остановить',
                                                                        callback_data=f'job_p_{idsql}'))
                                               .add(InlineKeyboardButton('Возобновить',
                                                                         callback_data=f'job_r_{idsql}'))
                                               )
    elif ret[-1] == 'OFF' and ret[-2] == 'Yes':
        await callback_query.answer('Сначала необходимо завершить данное напомниние')
    else:
        await callback_query.answer('Напоминание уже возобнавлено')

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(time_start, commands='time')
    dp.register_message_handler(add_job_choise, commands='Добавить_напоминание')
    dp.register_callback_query_handler(add_job, lambda x: x.data and x.data.startswith('remaind_'))
    dp.register_message_handler(add_name_job, state=FSM_time.name)
    dp.register_callback_query_handler(add_day, lambda x: x.data and x.data.startswith('day_'), state=FSM_time.day)
    dp.register_message_handler(add_time, state=FSM_time.time)
    dp.register_message_handler(add_name_job_onetime, state=FSM_onetime.name)
    dp.register_message_handler(add_date_onetime, state=FSM_onetime.date)
    dp.register_message_handler(add_time_onetime, state=FSM_onetime.time)
    dp.register_callback_query_handler(job_stop, lambda x: x.data and x.data.startswith('job_stop_'))
    dp.register_message_handler(delete_job, commands='Удалить_напомнинание')
    dp.register_callback_query_handler(del_time, lambda x: x.data and x.data.startswith('del_time'))
    dp.register_message_handler(time_menu, commands='Показать_напоминания')
    dp.register_callback_query_handler(job_pause,lambda x: x.data and x.data.startswith('job_p_'))
    dp.register_callback_query_handler(job_resume, lambda x: x.data and x.data.startswith('job_r_'))