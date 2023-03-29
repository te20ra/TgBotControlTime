import psycopg2
from psycopg2 import Error


def sql3_start():
    try:
        global cur, connection
        # Подключение к существующей базе данных
        connection = psycopg2.connect(user="te20ra",
                                      # пароль, который указали при установке PostgreSQL
                                      password="gigi123",
                                      host="127.0.0.1",
                                      port="5432",
                                      database='database1')
        # Курсор для выполнения операций с базой данных
        cur = connection.cursor()
        cur.execute(
                'CREATE TABLE IF NOT EXISTS data_time(id_sql SERIAL PRIMARY KEY, iduser TEXT, name TEXT, days TEXT, time TEXT, alarm TEXT, status TEXT, deleted TEXT)')
        print('data_game - OK')
        connection.commit()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)


async def sql_time_new(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO data_time (iduser, name, days, time, alarm, status, deleted) VALUES ( \'%s\', %s, %s, %s, \'No\', \'ON\', \'No\')', tuple(data.values()))
        connection.commit()


async def sql_time_search(name,iduser):
    cur.execute('SELECT EXISTS(SELECT name FROM data_time WHERE name = %s AND "iduser" = \'%s\' AND deleted = \'No\')', (name,iduser))
    return cur.fetchone()[0]


async def sql_time_idsql(state):
    async with state.proxy() as data:
        cur.execute('SELECT id_sql FROM data_time WHERE "iduser" = \'%s\' AND name = %s AND days = %s AND time = %s AND deleted = \'No\'', tuple(data.values()))
        return cur.fetchone()[0]


async def sql_time_days_check(id_sql):
    cur.execute('SELECT days FROM data_time WHERE id_sql = %s', (id_sql,))
    return cur.fetchone()[0]


async def sql_time_days_change(id_sql,days):
    cur.execute('UPDATE data_time SET days = %s WHERE id_sql = %s ', (days, id_sql))
    connection.commit()


async def sql_alarm_check(id_sql):
    cur.execute('SELECT alarm FROM data_time WHERE id_sql = %s', (id_sql,))
    return cur.fetchone()[0]


async def sql_alarm_yes(id_sql):
    cur.execute('UPDATE data_time SET alarm = \'Yes\' WHERE id_sql = %s', (id_sql,))
    connection.commit()


async def sql_alarm_no(id_sql):
    cur.execute('UPDATE data_time SET alarm = \'No\' WHERE id_sql = %s', (id_sql,))
    connection.commit()


async def sql_time_read_to_delete(message):
    cur.execute('SELECT id_sql, name, days, time, status FROM data_time WHERE "iduser" = \'%s\' AND deleted = \'No\'', (message.from_user.id,))
    return cur.fetchall()


async def sql_time_delete(id_sql):
    cur.execute('UPDATE data_time SET deleted = \'Yes\' WHERE id_sql = %s', (id_sql,))
    connection.commit()


async def sql_time_read_menu(message):
    cur.execute('SELECT id_sql, name, days, time, status FROM data_time WHERE "iduser" = \'%s\' AND deleted = \'No\'', (message.from_user.id,))
    return cur.fetchall()


async def sql_time_status_check(id_sql):
    cur.execute('SELECT status FROM data_time WHERE id_sql = %s AND deleted = \'No\'',(id_sql,))
    return cur.fetchone()[0]


async def sql_time_status_OFF(id_sql):
    cur.execute('UPDATE data_time SET status = \'OFF\' WHERE id_sql = %s',(id_sql,))
    connection.commit()


async def sql_time_status_ON(id_sql):
    cur.execute('UPDATE data_time SET status = \'ON\' WHERE id_sql = %s',(id_sql,))
    connection.commit()


async def sql_time_deleted_check(id_sql):
    cur.execute('SELECT deleted FROM data_time WHERE id_sql = %s AND deleted = \'No\'',(id_sql,))
    return cur.fetchone()[0]


async def sql_time_start_bot():
    cur.execute('SELECT id_sql, iduser, name, days, time FROM data_time WHERE deleted = \'No\'')
    return cur.fetchall()


async def sql_time_one_line(id_sql):
    cur.execute('SELECT name, days, time, status FROM data_time WHERE id_sql = %s',(id_sql,))
    return cur.fetchall()


async def sql_time_count(userid):
    cur.execute('SELECT count(iduser) FROM data_time WHERE "iduser" = \'%s\' AND deleted = \'No\'', (userid,))
    return cur.fetchone()[0]