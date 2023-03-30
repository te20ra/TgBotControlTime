from create_bot import sheduler
from aiogram import Dispatcher
from data_base import sqlite_db, sqlite_db_time
from datetime import datetime
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asyncio import sleep


async def check_timeout(dp: Dispatcher, iduser, id_sql, last_time, starttime):
    status = await sqlite_db.sql_status_check(id_sql)
    if status == 'sleep':
        sheduler.remove_job(f'timeout {id_sql}')
    elif status == 'active' and datetime.now() >= last_time:
        msg = await dp.bot.send_message(iduser, 'Заканчивай, ага', reply_markup= \
        InlineKeyboardMarkup().add(InlineKeyboardButton('СТОП', callback_data=f'stopgame_{id_sql}_{str(starttime)}')))
        await sleep(58)
        try:
            await dp.bot.delete_message(iduser, msg.message_id)
        except:
            print('Сообщение уже удалено')
async def add_job_sheduler(dp: Dispatcher, iduser, id_sql, name):
    print(f'add_job_sheduler {id_sql, name}')
    await sqlite_db_time.sql_alarm_yes(id_sql)
    sheduler.add_job(alarm, 'interval', seconds=60, id=f'alarm {id_sql}',args=(dp,),
                     kwargs={'iduser': iduser,
                             'id_sql': id_sql,
                             'name': name})

async def alarm(dp: Dispatcher, iduser, name, id_sql):
    alarm = await sqlite_db_time.sql_alarm_check(id_sql)
    if alarm == "Yes":
        msg = await dp.bot.send_message(iduser, f'НАПОМИНАЮ\n{name}', \
        reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('Нажми на меня', callback_data=f'job_stop_{id_sql}')))
        await sleep(58)
        try:
            await dp.bot.delete_message(iduser, msg.message_id)
        except:
            print('Сообщение уже удалено')
    else:
        sheduler.remove_job(f'alarm {id_sql}')
        days = await sqlite_db_time.sql_time_days_check(id_sql)
        print(days)
        days.startswith('date_')
        if days.startswith('date_') == True:
            await sqlite_db_time.sql_time_delete(id_sql)