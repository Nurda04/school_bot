import sqlite3 as sq


def db_start():
    global db, cur
    db = sq.connect("Desktop/Python/school_bot/bot.db")
    cur = db.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
                'user_id' INTEGER,
                'name' TEXT PRIMARY KEY,
                'admin' INTEGER DEFAULT (0),
                'current_class' TEXT REFERENCES classes (class) ON DELETE SET NULL ON UPDATE CASCADE)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS classes(
                'class' TEXT PRIMARY KEY,
                'password' TEXT,
                'creator_id' INTEGER)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS class_members( 
                'class' TEXT REFERENCES classes (class) ON DELETE CASCADE ON UPDATE CASCADE,
                'user_id' INTEGER,
                'name' TEXT REFERENCES users (name) ON UPDATE CASCADE,
                'admin' INTEGER DEFAULT (0))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS day1(
                'object' TEXT,
                'task1' TEXT,
                'task2' TEXT,
                'rec_week1' DATETIME,
                'rec_week2' DATETIME,
                'class' TEXT REFERENCES classes (class) ON DELETE CASCADE ON UPDATE CASCADE)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS day2(
                'object' TEXT,
                'task1' TEXT,
                'task2' TEXT,
                'rec_week1' DATETIME,
                'rec_week2' DATETIME,
                'class' TEXT REFERENCES classes (class) ON DELETE CASCADE ON UPDATE CASCADE)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS day3(
                'object' TEXT,
                'task1' TEXT,
                'task2' TEXT,
                'rec_week1' DATETIME,
                'rec_week2' DATETIME,
                'class' TEXT REFERENCES classes (class) ON DELETE CASCADE ON UPDATE CASCADE)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS day4(
                'object' TEXT,
                'task1' TEXT,
                'task2' TEXT,
                'rec_week1' DATETIME,
                'rec_week2' DATETIME,
                'class' TEXT REFERENCES classes (class) ON DELETE CASCADE ON UPDATE CASCADE)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS day5(
                'object' TEXT,
                'task1' TEXT,
                'task2' TEXT,
                'rec_week1' DATETIME,
                'rec_week2' DATETIME,
                'class' TEXT REFERENCES classes (class) ON DELETE CASCADE ON UPDATE CASCADE)""")
    db.execute("PRAGMA foreign_keys = ON")
    db.commit()


# - - - Регистрация и смена имени - - -
def check_reg(user_id):
    return cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)).fetchone()

def check_name(name):
    return cur.execute("SELECT name FROM users WHERE name = ?", (name,)).fetchone()

def registration(user_id, name):
    cur.execute("INSERT INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
    db.commit()

def rename(user_id, name):
    cur.execute("UPDATE users SET name = ? WHERE user_id = ?", (name, user_id))
    db.commit()


# - - - Регистрация класса - - -
def check_class_count(user_id):
    return cur.execute("SELECT creator_id FROM classes WHERE creator_id = ?", (user_id,)).fetchall()

def get_name(user_id):
    return cur.execute("SELECT name FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]

def check_class(class_name):
    return cur.execute("SELECT class FROM classes WHERE class = ?", (class_name,)).fetchone()

def reg_class(class_name, password, user_id):
    cur.execute("INSERT INTO classes (class, password, creator_id) VALUES (?, ?, ?)", (class_name, password, user_id))
    cur.execute("INSERT INTO class_members (class, user_id, name, admin) VALUES (?, ?, ?, 3)", (class_name, user_id, get_name(user_id)))
    db.commit()


# - - - Получение текущего класса - - -
def get_class_current(user_id):
    return cur.execute("SELECT current_class FROM users WHERE user_id = ?", (user_id,)).fetchone()


# - - - Выдача классов в которых состоит пользователь для смены текущего класса - - -
def get_classes(user_id):
    return cur.execute("SELECT class FROM class_members WHERE user_id = ?", (user_id,)).fetchall()


# - - - Выдача созданных классов для настроек - - -
def get_classes_created(user_id):
    return cur.execute("SELECT class FROM classes WHERE creator_id = ?", (user_id,)).fetchall()


# - - - Смена текущего класса - - -
def class_change(class_name, user_id):
    cur.execute("UPDATE users SET current_class = ? WHERE user_id = ?", (class_name, user_id))
    db.commit()


# - - - Удаление класса - - -    
def class_del(class_name):
    cur.execute("DELETE FROM classes WHERE class = ?", (class_name,))
    db.commit()


# - - - Вход в класс - - -
def class_check_join(class_name, user_id):
    return cur.execute("SELECT user_id FROM class_members WHERE class = ? AND user_id = ?", (class_name, user_id)).fetchone()

def class_get_pass(class_name):
    return cur.execute("SELECT password FROM classes WHERE class = ?", (class_name,)).fetchone()

def class_join(class_name, user_id):
    cur.execute("INSERT INTO class_members (class, user_id, name) VALUES (?, ?, ?)", (class_name, user_id, get_name(user_id)))
    db.commit()


# - - - Настройки класса - - -
def class_rename(class_name_new, class_name):
    cur.execute("UPDATE classes SET class = ? WHERE class = ?", (class_name_new, class_name))
    db.commit()

def class_repass(class_pass_new, class_name):
    cur.execute("UPDATE classes SET password = ? WHERE class = ?", (class_pass_new, class_name))
    db.commit()


# - - - Инфо класса - - -
def get_class_info(class_name):
    info = cur.execute("SELECT class, password FROM classes WHERE class = ?", (class_name,)).fetchall()[0]
    info2 = cur.execute("SELECT name FROM class_members WHERE class = ?", (class_name,)).fetchall()
    info3 = cur.execute("SELECT GROUP_CONCAT(name, ', ') FROM class_members WHERE class = ? AND admin = 2", (class_name,)).fetchall()[0]
    info4 = cur.execute("SELECT GROUP_CONCAT(name, ', ') FROM class_members WHERE class = ? AND admin = 1", (class_name,)).fetchall()[0]
    return info, info2, info3, info4

def get_class_creator(class_name):
    return cur.execute("SELECT name FROM class_members WHERE class = ? AND admin = 3", (class_name,)).fetchone()[0]


# - - - Админ-панель создателя и админа - - -
def get_classes_admin(user_id, admin):
    return cur.execute("SELECT GROUP_CONCAT(class, ', ') FROM class_members WHERE user_id = ? AND admin = ?", (user_id, admin)).fetchall()[0]

def admin_check_user(name, class_name):
    return cur.execute("SELECT admin FROM class_members WHERE name = ? AND class = ?", (name, class_name)).fetchone()

def admin_change(new_lvl, name, class_name):
    cur.execute("UPDATE class_members SET admin = ? WHERE name = ? AND class = ?", (new_lvl, name, class_name))
    db.commit()


# - - - Получение уровня админа для меню-панели - - -
def check_admin(user_id, cur_class):
    return cur.execute("SELECT admin FROM class_members WHERE user_id = ? AND class = ?", (user_id, cur_class)).fetchone()[0]


# - - - Неделя текущая или следующая в выдаче расписания - - -
def week_period():
    return cur.execute("SELECT strftime('%d.%m', 'now', 'weekday 0', '-6 days') AS start, strftime('%d.%m', 'now', 'weekday 0', '-2 days') AS end").fetchone()

def week_period2():
    return cur.execute("SELECT strftime('%d.%m', 'now', 'weekday 0', '+1 days') AS start, strftime('%d.%m', 'now', 'weekday 0', '+5 days') AS end").fetchone()


# - - - Выдача расписания - - -
def get_schedule(day, cur_class):
    return cur.execute(f"SELECT * FROM {day} WHERE class = ?", (cur_class,)).fetchall()

def get_schedule_check(time):
    return cur.execute(f"SELECT strftime('%W', 'now', 'localtime', '+{time} days', '+6 hours') AS time").fetchone()[0]


# - - - Выдача предметов для меню-панели - - -
def get_schedule_obj(day, cur_class):
    return cur.execute(f"SELECT object FROM {day} WHERE class = ?", (cur_class,)).fetchall()


# - - - Проверка наличия предмета для внесения данных - - -
def check_obj(day, les, cur_class):
    return cur.execute(f"SELECT object FROM {day} WHERE object = ? AND class = ?", (les, cur_class)).fetchone()


# - - - Добавление ДЗ, проверка наличия, получение существующего для мульти ДЗ - - -
def check_hw(obj, day, week, time, record, cur_class):
    return cur.execute(f"SELECT {week} FROM {day} WHERE {record} = strftime('%W', 'now', 'localtime', '+{time} days', '+6 hours') AND object = ? AND class = ?", (obj, cur_class)).fetchone()

def get_hw(obj, day, week, cur_class):
    return cur.execute(f"SELECT {week} FROM {day} WHERE object = ? AND class = ?", (obj, cur_class)).fetchone()[0]

def add_hw(obj, task, day, week, time, record, cur_class):
    cur.execute(f"UPDATE {day} SET {week} = ?, {record} = strftime('%W', 'now', 'localtime', '+{time} days', '+6 hours') WHERE object = ? AND class = ?", (task, obj, cur_class))
    db.commit()


# - - - Добавление предмета - - -    
def add_les(les, day, cur_class):
    cur.execute(f"INSERT INTO {day} (object, class) VALUES (?, ?)", (les, cur_class))
    db.commit()


# - - - Удаление предмета - - -
def del_obj(obj, day, cur_class):
    cur.execute(f"DELETE FROM {day} WHERE object = ? AND class = ?", (obj, cur_class))
    db.commit()


# - - - Удаление ДЗ одинарное и мульти - - -
def del_hw(obj, day, week, record, cur_class):
    cur.execute(f"UPDATE {day} SET {week} = ?, {record} = ? WHERE object = ? AND class = ?", (None, None, obj, cur_class))
    db.commit()

def del_hw2(obj, task, day, week, cur_class):
    cur.execute(f"UPDATE {day} SET {week} = ? WHERE object = ? AND class = ?", (task, obj, cur_class))
    db.commit()
