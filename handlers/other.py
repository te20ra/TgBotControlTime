from aiogram import types, Dispatcher
from create_bot import bot
from data_base import sqlite_db, sqlite_db_time
from keyboards import kb_main, kb_game
from create_bot import sheduler, dp
from handlers.apsched import add_job_sheduler
async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id,
                           'Здарова. Этот бот поможет тебе контролировать время которое ты тратишь на игры, а также создавать напоминания.\n'
                           '/moder - команда для добавления в список новой игры или удаления старой (Всего может быть 10 игр)\n'
                           '/game_start - команда для начала выбора игры и отсчета таймера\n'
                           '/menu - команда для просмотра добавленных игр и оставшегося времени\n'
                           '/help - команда для вывода команд бота\n'
                           '/time - команда для создания и удаления напоминаний\n'
                           '*Если вдруг бот долго не реагирует на что-то, значит он умер или ожидает иного действия',
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
    jobs = await sqlite_db_time.sql_time_read_deleted()
    print(jobs)
    print(sheduler.get_jobs())
    for el in jobs:
        idsql = el[0]
        iduser = el[1]
        name = el[2]
        days = el[3]
        hour = el[4].split(':')[0]
        minute = el[4].split(':')[1]
        print(idsql,iduser,name,days,hour,minute)
        sheduler.add_job(add_job_sheduler, 'cron', day_of_week=days, hour=hour, minute=minute, id=f'job {idsql}',
                         args=(dp,),
                         kwargs={'iduser': iduser,
                                 'id_sql': idsql,
                                 'name': name})

    print(sheduler.get_jobs())


def time_chek(time):
    if len(time) == 5:
        s1 = time[0:2]
        s2 = time[2]
        s3 = time[3:]
        if s1.isdigit() and 0 <= int(s1) <= 24 and s2 == ':' and s3.isdigit() and 00 <= int(s3) <= 59:
            return True
        else:
            return False
    else:
        return False


def rename_days(days):
    days_dict = {'mon': 'пн',
                 'tue': 'вт',
                 'wed': 'ср',
                 'thu': 'чт',
                 'fri': 'пт',
                 'sat': 'сб',
                 'sun': 'вс'}
    res = ''
    if len(days) >= 3:
        days = days.split(', ')[:-1]
        for i in range(len(days)):
            res += (days_dict[days[i]]) + ', '
    return res

def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(menu, commands='Список_игр')
    dp.register_message_handler(main_menu, commands='Главное_меню')
    dp.register_message_handler(go_to_game, commands=['game'])