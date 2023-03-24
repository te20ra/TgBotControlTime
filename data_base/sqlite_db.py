import sqlite3 as sq


def sql_start():
    global base, cur
    base = sq.connect('game_control.db')
    cur = base.cursor()
    if base:
        print('Data base connected')
    base.execute('CREATE TABLE IF NOT EXISTS data_games(id_sql INTEGER PRIMARY KEY, iduser TEXT, name TEXT, spendtime INTEGER, maxtime INTEGER, status TEXT, last_time TEXT, deleted TEXT)')
    print('data_games - OK')
    base.commit()


async def sql_count(userid):
    return cur.execute('SELECT count(iduser) FROM data_games WHERE iduser == ? AND deleted == "No"', (userid,)).fetchone()[0]


async def sql_add(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO data_games VALUES (null, ?, ?, ?, ?, "sleep", "", "No")', tuple(data.values()))
        base.commit()


async def sql_read_menu(message):
    return cur.execute('SELECT name, spendtime, maxtime FROM data_games WHERE iduser == ? AND deleted == "No"', (message.from_user.id,)).fetchall()



async def sql_read_to_delete(message):
    return cur.execute('SELECT id_sql, name, spendtime, maxtime FROM data_games WHERE iduser == ? AND deleted == "No" AND status == "sleep"', (message.from_user.id,)).fetchall()


async def sql_read_to_start_game(iduser):
    return cur.execute('SELECT name, spendtime, maxtime FROM data_games WHERE iduser == ? AND deleted == "No" AND spendtime < maxtime', (iduser,)).fetchall()


async def sql_delete(id_sql):
    cur.execute('UPDATE data_games SET deleted == "Yes" WHERE id_sql == ?', (id_sql,))
    base.commit()


async def sql_update_spendtime(id_sql, spendtime):
    cur.execute('UPDATE data_games SET spendtime == (spendtime + ?) WHERE id_sql == ?', (spendtime, id_sql))
    base.commit()


async def sql_status_active(userid, game):
    cur.execute('UPDATE data_games SET status == "active" WHERE iduser == ? AND name == ? AND deleted == "No"', (userid, game))
    base.commit()


async def sql_status_sleep(id_sql):
    cur.execute('UPDATE data_games SET status == "sleep" WHERE id_sql == ?', (id_sql,))
    base.commit()


async def sql_status_check(id_sql):
    return cur.execute('SELECT status FROM data_games WHERE id_sql == ?', (id_sql,)).fetchone()[0]


async def sql_status_check_all(iduser):
    return cur.execute('SELECT status FROM data_games WHERE iduser == ? AND deleted == "No"', (iduser,)).fetchall()


async def sql_maxtime(id_sql):
    return cur.execute('SELECT maxtime FROM data_games WHERE id_sql == ?', (id_sql,)).fetchone()[0]


#async def sql_name(id_sql):
   #return cur.execute('SELECT name FROM data_games WHERE id_sql == ?', (id_sql,)).fetchone()[0]


async def sql_do_last_time(last_time, id_sql):
    cur.execute('UPDATE data_games SET last_time == ? WHERE id_sql == ? ', (last_time, id_sql))
    base.commit()


async def sql_last_time(id_sql):
    return cur.execute('SELECT last_time FROM data_games WHERE id_sql == ?', (id_sql,)).fetchone()[0]


async def sql_spend_time(id_sql):
    return cur.execute('SELECT spendtime FROM data_games WHERE id_sql == ?', (id_sql,)).fetchone()[0]


async def sql_return_id_sql(userid,game):
    return cur.execute('SELECT id_sql FROM data_games WHERE iduser == ? AND status = "active" AND deleted == "No" AND name == ?',(userid,game)).fetchone()[0]

async def sql_clear_spendtime():
    cur.execute('UPDATE data_games SET spendtime == 0 WHERE status == "sleep"')
    base.commit()

async def sql_search(name,iduser):
    return cur.execute('SELECT EXISTS(SELECT name FROM data_games WHERE name == ? AND iduser == ? AND deleted == "No")', (name,iduser)).fetchone()[0]