import psycopg2
from psycopg2 import Error
from config import login_bd, password_bd

def sql_start():
    try:
        global cur, connection
        # Подключение к существующей базе данных
        connection = psycopg2.connect(user=login_bd,
                                      # пароль, который указали при установке PostgreSQL
                                      password=password_bd,
                                      host="127.0.0.1",
                                      port="5432",
                                      database='database1')
        # Курсор для выполнения операций с базой данных
        cur = connection.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS data_games(id_sql SERIAL PRIMARY KEY, iduser TEXT, name TEXT, spendtime INTEGER, maxtime INTEGER, status TEXT, last_time TEXT, deleted TEXT)')
        print('data_time - OK')
        connection.commit()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

async def sql_stop(_):
    cur.close()
    connection.close()
    print("Соединение с PostgreSQL закрыто")


async def sql_count(userid):
    cur.execute('SELECT count(iduser) FROM data_games WHERE "iduser"=\'%s\' AND "deleted" = \'No\'', (userid,))
    return cur.fetchone()[0]

async def sql_add(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO data_games (iduser, name, spendtime, maxtime, status, last_time, deleted) VALUES (\'%s\', %s, \'%s\', \'%s\', \'sleep\', \'\', \'No\')', tuple(data.values()))
        connection.commit()


async def sql_read_menu(message):
    cur.execute('SELECT name, spendtime, maxtime FROM data_games WHERE "iduser" = \'%s\' AND "deleted" = \'No\'', (message.from_user.id,))
    return cur.fetchall()


async def sql_read_to_delete(message):
    cur.execute('SELECT id_sql, name, spendtime, maxtime FROM data_games WHERE "iduser" = \'%s\' AND "deleted" = \'No\' AND "status" = \'sleep\'', (message.from_user.id,))
    return cur.fetchall()


async def sql_read_to_start_game(iduser):
    cur.execute('SELECT name, spendtime, maxtime FROM data_games WHERE "iduser" = \'%s\' AND "deleted" = \'No\' AND spendtime < maxtime', (iduser,))
    return cur.fetchall()


async def sql_delete(id_sql):
    cur.execute('UPDATE data_games SET "deleted" = \'Yes\' WHERE "id_sql" = %s', (id_sql,))
    connection.commit()


async def sql_update_spendtime(id_sql, spendtime):
    cur.execute('UPDATE data_games SET spendtime = (spendtime + %s) WHERE id_sql = %s', (spendtime, id_sql))
    connection.commit()


async def sql_status_active(userid, game):
    cur.execute('UPDATE data_games SET status = \'active\' WHERE "iduser" = \'%s\' AND name = %s AND deleted = \'No\'', (userid, game))
    connection.commit()


async def sql_status_sleep(id_sql):
    cur.execute('UPDATE data_games SET status = \'sleep\' WHERE id_sql = %s', (id_sql,))
    connection.commit()


async def sql_status_check(id_sql):
    cur.execute('SELECT status FROM data_games WHERE id_sql = %s', (id_sql,))
    return cur.fetchone()[0]


async def sql_status_check_all(iduser):
    cur.execute('SELECT status FROM data_games WHERE "iduser" = \'%s\' AND deleted = \'No\'', (iduser,))
    return cur.fetchall()


async def sql_maxtime(id_sql):
    cur.execute('SELECT maxtime FROM data_games WHERE id_sql = %s', (id_sql,))
    return cur.fetchone()[0]


async def sql_do_last_time(last_time, id_sql):
    cur.execute('UPDATE data_games SET last_time = %s WHERE id_sql = %s ', (last_time, id_sql))
    connection.commit()


async def sql_last_time(id_sql):
    cur.execute('SELECT last_time FROM data_games WHERE id_sql = %s', (id_sql,))
    return cur.fetchone()[0]

async def sql_spend_time(id_sql):
    cur.execute('SELECT spendtime FROM data_games WHERE id_sql = %s', (id_sql,))
    return cur.fetchone()[0]

async def sql_return_id_sql(userid,game):
    cur.execute('SELECT id_sql FROM data_games WHERE "iduser" = \'%s\' AND status = \'active\' AND deleted = \'No\' AND name = %s',(userid,game))
    return cur.fetchone()[0]
async def sql_clear_spendtime():
    cur.execute('UPDATE data_games SET spendtime = 0 WHERE status = \'sleep\'')
    connection.commit()

async def sql_search(name,iduser):
    cur.execute('SELECT EXISTS(SELECT name FROM data_games WHERE name = %s AND "iduser" = \'%s\' AND deleted = \'No\')', (name,iduser))
    return cur.fetchone()[0]