import sqlite3 as sq


def sql3_start():
    global base, cur
    base = sq.connect('game_control.db')
    cur = base.cursor()
    base.execute('CREATE TABLE IF NOT EXISTS data_time(id_sql INTEGER PRIMARY KEY, iduser TEXT, name TEXT, days TEXT, time TEXT, alarm TEXT, status TEXT, deleted TEXT)')
    print('data_time - OK')
    base.commit()


async def sql_time_new(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO data_time VALUES (null, ?, ?, ?, ?, "No", "ON", "No")', tuple(data.values()))
        base.commit()


async def sql_time_search(name,iduser):
    return cur.execute('SELECT EXISTS(SELECT name FROM data_time WHERE name == ? AND iduser == ? AND deleted == "No")', (name,iduser)).fetchone()[0]


async def sql_time_idsql(state):
    async with state.proxy() as data:
        return cur.execute('SELECT id_sql FROM data_time WHERE iduser == ? AND name == ? AND days = ? AND time = ? AND deleted == "No"', tuple(data.values())).fetchone()[0]


async def sql_time_days_check(id_sql):
    return cur.execute('SELECT days FROM data_time WHERE id_sql == ?', (id_sql,)).fetchone()[0]


async def sql_time_days_change(id_sql,days):
    cur.execute('UPDATE data_time SET days == ? WHERE id_sql == ? ', (days, id_sql))
    base.commit()


async def sql_alarm_check(id_sql):
    return cur.execute('SELECT alarm FROM data_time WHERE id_sql == ?', (id_sql,)).fetchone()[0]


async def sql_alarm_yes(id_sql):
    cur.execute('UPDATE data_time SET alarm == "Yes" WHERE id_sql == ?', (id_sql,))
    base.commit()


async def sql_alarm_no(id_sql):
    cur.execute('UPDATE data_time SET alarm == "No" WHERE id_sql == ?', (id_sql,))
    base.commit()


async def sql_time_read_to_delete(message):
    return cur.execute('SELECT id_sql, name, days, time, status FROM data_time WHERE iduser == ? AND deleted == "No"', (message.from_user.id,)).fetchall()


async def sql_time_delete(id_sql):
    cur.execute('UPDATE data_time SET deleted == "Yes" WHERE id_sql == ?', (id_sql,))
    base.commit()


async def sql_time_read_menu(message):
    return cur.execute('SELECT id_sql, name, days, time, status FROM data_time WHERE iduser == ? AND deleted == "No"', (message.from_user.id,)).fetchall()


async def sql_time_status_check(id_sql):
    return cur.execute('SELECT status FROM data_time WHERE id_sql == ? AND deleted == "No"',(id_sql,)).fetchone()[0]


async def sql_time_status_OFF(id_sql):
    cur.execute('UPDATE data_time SET status == "OFF" WHERE id_sql == ?',(id_sql,))
    base.commit()

async def sql_time_status_ON(id_sql):
    cur.execute('UPDATE data_time SET status == "ON" WHERE id_sql == ?',(id_sql,))
    base.commit()

async def sql_time_deleted_check(id_sql):
    return cur.execute('SELECT deleted FROM data_time WHERE id_sql == ? AND deleted == "No"',(id_sql,)).fetchone()[0]

async def sql_time_read_deleted():
    return cur.execute('SELECT id_sql, iduser, name, days, time FROM data_time WHERE deleted == "No"').fetchall()