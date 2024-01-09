import sqlite3 as sq


def db_start():
    global db, cur
    db = sq.connect("/home/Nurda04/school_bot/bot.db")
    cur = db.cursor()


# - - - Регистрация и смена имени - - -
def check_reg(user_id):
    return cur.execute("SELECT name FROM users WHERE user_id = ?", (user_id,)).fetchone()

def registration(user_id, name):
    cur.execute("INSERT INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
    db.commit()

def rename(user_id, name):
    cur.execute("UPDATE users SET name = ? WHERE user_id = ?", (name, user_id))
    db.commit()


# - - - Админ-панель - - -
def check_admin(user_id):
    return cur.execute("SELECT admin FROM users WHERE user_id = ?", (user_id,)).fetchone()

def admin_check_user(name):
    return cur.execute("SELECT name, admin FROM users WHERE name = ?", (name,)).fetchone()

def admin_change(new_lvl, name):
    cur.execute("UPDATE users SET admin = ? WHERE name = ?", (new_lvl, name))
    db.commit()


# - - - Неделя текущая или следующая в выдаче расписания - - -
def week_period():
    return cur.execute("SELECT strftime('%d.%m', 'now', 'weekday 0', '-6 days') AS start, strftime('%d.%m', 'now', 'weekday 0', '-2 days') AS end").fetchone()

def week_period2():
    return cur.execute("SELECT strftime('%d.%m', 'now', 'weekday 0', '+1 days') AS start, strftime('%d.%m', 'now', 'weekday 0', '+5 days') AS end").fetchone()


# - - - Выдача расписания с ДЗ и без- - -
def get_schedule(day):
    return cur.execute(f"SELECT * FROM {day}").fetchall()

def get_schedule_check(time):
    return cur.execute(f"SELECT strftime('%W', 'now', 'localtime', '+{time} days', '+6 hours') AS time").fetchone()[0]


# - - - Выдача предметов для меню-панели - - -
def get_schedule_obj(day):
    return cur.execute(f"SELECT object FROM {day}").fetchall()


# - - - Проверка наличия предмета для внесения данных - - -
def check_obj(day, les):
    return cur.execute(f"SELECT object FROM {day} WHERE object = ?", (les,)).fetchone()


# - - - Добавление ДЗ, проверка наличия, получение существующего для мульти ДЗ - - -
def check_hw(obj, day, week, time, record):
    return cur.execute(f"SELECT {week} FROM {day} WHERE {record} = strftime('%W', 'now', 'localtime', '+{time} days', '+6 hours') AND object = ?", (obj,)).fetchone()

def get_hw(obj, day, week):
    return cur.execute(f"SELECT {week} FROM {day} WHERE object = ?", (obj,)).fetchone()[0]

def add_hw(obj, task, day, week, time, record):
    cur.execute(f"UPDATE {day} SET {week} = ?, {record} = strftime('%W', 'now', 'localtime', '+{time} days', '+6 hours') WHERE object = ?", (task, obj))
    db.commit()


# - - - Добавление предмета - - -
def add_les(les, day):
    cur.execute(f"INSERT INTO {day} (object) VALUES (?)", (les,))
    db.commit()


# - - - Удаление предмета - - -
def del_obj(obj, day):
    cur.execute(f"DELETE FROM {day} WHERE object = ?", (obj,))
    db.commit()


# - - - Удаление ДЗ одинарное и мульти - - -
def del_hw(obj, day, week, record):
    cur.execute(f"UPDATE {day} SET {week} = ?, {record} = ? WHERE object = ?", (None, None, obj,))
    db.commit()

def del_hw2(obj, task, day, week):
    cur.execute(f"UPDATE {day} SET {week} = ? WHERE object = ?", (task, obj))
    db.commit()
