from aiogram.utils import executor
from create_bot import dp, sheduler
from data_base import sqlite_db, sqlite_db_time
from handlers import addGAME, other, startgame, time
async def on_startup(_):
    print('Бот вышел в онлайн')
    sqlite_db.sql_start()
    sqlite_db_time.sql3_start()
    sheduler.start()
    await other.start_shedulers_with_bot()

addGAME.register_handlers(dp)
other.register_handlers_client(dp)
startgame.register_handlers(dp)
time.register_handlers(dp)

sheduler.add_job(sqlite_db.sql_clear_spendtime, "cron", day="1-31", hour="00", minute="01")
executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=sqlite_db.sql_stop)

