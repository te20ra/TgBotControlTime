from aiogram import types, Dispatcher
from create_bot import bot
from data_base import sqlite_db, sqlite_db_time
from keyboards import kb_main, kb_game
from create_bot import sheduler, dp
from handlers.apsched import add_job_sheduler
from datetime import datetime, timedelta
async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id,
                           'Привет. Этот бот поможет тебе контролировать время которое ты тратишь на развлечения, а также создавать напоминания.\n'
                           '/game - команда для игр. Там можно добавить/удалить развлечение(всего 10 штук), начать таймер для развлечений и просмотреть список игр\n'
                           '/time - команда для создания/удаления и просмотра напоминаний\n'
                           '/help - команда для вывода команд бота\n'
                           '*Если вдруг бот долго не реагирует на что-то, значит он умер или ожидает иного действия\n'
                           '**Развлечения=игры',
                           reply_markup=kb_main.button_case_add)
    await message.delete()


async def menu(message: types.Message):
    menu = await sqlite_db.sql_read_menu(message)
    if len(menu) > 0:
        for ret in menu:
            await bot.send_message(message.from_user.id, f'{ret[0]}:  {ret[1]}  /  {ret[2]}')
    else:
        await bot.send_message(message.from_user.id, 'Для начала необходимо добавить игры нажав "/Редактировать_игры"')


async def main_menu(message: types.Message):
    await bot.send_message(message.from_user.id, 'Вы в гланвном меню', reply_markup=kb_main.button_case_add)


async def go_to_game(message: types.Message):
    await bot.send_message(message.from_user.id, 'Вы в меню игр', reply_markup=kb_game.button_case_add)


async def start_shedulers_with_bot():
    jobs = await sqlite_db_time.sql_time_start_bot()
    for el in jobs:
        if el[3].startswith('cron_'):
            idsql = el[0]
            iduser = el[1]
            name = el[2]
            days = el[3].replace('cron_','')
            time = datetime.strptime(el[4], '%H:%M')
            time = time - timedelta(minutes=1)
            hour = time.hour
            minute = time.minute
            sheduler.add_job(add_job_sheduler, 'cron', day_of_week=days, hour=hour, minute=minute, id=f'job {idsql}',
                             args=(dp,),
                             kwargs={'iduser': iduser,
                                     'id_sql': idsql,
                                     'name': name})
            if await sqlite_db_time.sql_time_status_check(idsql) == 'OFF':
                sheduler.pause_job(f'job {idsql}')
        elif el[3].startswith('date_'):
            idsql = el[0]
            iduser = el[1]
            name = el[2]
            date = el[3].replace('date_', '')
            time = datetime.strptime(el[4], '%H:%M')
            time = time - timedelta(minutes=1)
            time = datetime.strftime(time, '%H:%M:%S')
            date = date + ' ' + time
            if datetime.strptime(date, '%Y-%m-%d %H:%M:%S') > datetime.now():
                sheduler.add_job(add_job_sheduler, 'date', run_date=date, id=f'job {idsql}',
                                 args=(dp,),
                                 kwargs={'iduser': iduser,
                                         'id_sql': idsql,
                                         'name': name})
                if await sqlite_db_time.sql_time_status_check(idsql) == 'OFF':
                        sheduler.pause_job(f'job {idsql}')
            else:
                await sqlite_db_time.sql_time_delete(idsql)




async def time_chek(time, date = ''):
    try:
        time = datetime.strptime(time, '%H:%M').time()
        if date == '':
            return True
        else:
            date = datetime.strptime(date, '%Y-%m-%d').date()
            if date == datetime.now().date() and time >= (datetime.now() + timedelta(minutes=1)).time():
                return True
            elif date > datetime.now().date():
                return True
    except ValueError:
        return False


async def rename_days(days):
    days_dict = {'mon': 'пн',
                 'tue': 'вт',
                 'wed': 'ср',
                 'thu': 'чт',
                 'fri': 'пт',
                 'sat': 'сб',
                 'sun': 'вс'}
    res = ''
    if days.startswith('cron_'):
        days = days.replace('cron_', '').split(',')
        for i in range(len(days)-1):
            res += (days_dict[days[i]]) + ', '
        return res[:-2]
    elif days.startswith('date_'):
        return days.replace('date_', '')
    else:
        days = days.split(', ')
        for i in range(len(days)-1):
            res += (days_dict[days[i]]) + ', '
        return res[:-2]

async def date_check(date):
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()
        if date >= datetime.now().date():
            return True
        else:
            return False
    except ValueError:
        return False



def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(menu, commands='Список_игр')
    dp.register_message_handler(main_menu, commands='Главное_меню')
    dp.register_message_handler(go_to_game, commands=['game'])