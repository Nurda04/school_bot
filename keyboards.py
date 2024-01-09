from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import database as db


btnmenu = InlineKeyboardButton('Меню', callback_data='menu')
week = InlineKeyboardButton('Неделя', callback_data='week')


# - - - Главное Меню - - -
list_m = []
ops = ['add_hw', 'add_les', 'del_hw', 'del_les', 'get_hw', 'get_les']
menus = ['Добавить ДЗ', 'Добавить предмет', 'Удалить ДЗ', 'Удалить предмет', 'Узнать ДЗ', 'Узнать расписание']
for i in range(6):
    btn_m = InlineKeyboardButton(menus[i], callback_data=ops[i])
    list_m.append(btn_m)
    menu = InlineKeyboardMarkup(row_width=2).add(*list_m)
    
list_m2 = []
ops2 = ['add_hw', 'del_hw', 'get_hw', 'get_les']
menus2 = ['Добавить ДЗ', 'Удалить ДЗ', 'Узнать ДЗ', 'Узнать расписание']
for i in range(4):
    btn_m2 = InlineKeyboardButton(menus2[i], callback_data=ops2[i])
    list_m2.append(btn_m2)  
    menu2 = InlineKeyboardMarkup(row_width=2).add(*list_m2)

get_hw = InlineKeyboardButton('Узнать ДЗ', callback_data='get_hw')
get_les = InlineKeyboardButton('Узнать расписание', callback_data='get_les')
menu3 = InlineKeyboardMarkup(row_width=2).add(get_hw, get_les)


# - - - Выбор Дня - - -
list_d = []
days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
for key_d, day in enumerate(days):
    btn_d = InlineKeyboardButton(day, callback_data='day' + str(key_d+1))
    list_d.append(btn_d)
    choose_day = InlineKeyboardMarkup(row_width=2).add(*list_d, btnmenu)
    choose_day2 = InlineKeyboardMarkup(row_width=2).add(*list_d, week, btnmenu)


# - - - Выбор предмета - - -
def kb_choose_obj(day):
    btn_list = []
    schedules = db.get_schedule(day)
    for key, schedule in enumerate(schedules):
        btn = InlineKeyboardButton(schedule[0], callback_data=str(key))
        btn_list.append(btn)
        choose_obj = InlineKeyboardMarkup(row_width=2).add(*btn_list, btnmenu)
        return choose_obj
        

# - - - Выбор ДЗ для удаления - - -
def kb_del_hw(i):
    btn_list = []
    for r in range(1, i+1):
        btn = InlineKeyboardButton(str(r), callback_data=str(r))
        btn_list.append(btn)
    del_hw = InlineKeyboardMarkup(row_width=2).add(*btn_list, btnmenu)
    return del_hw


# - - - Выбор недели - - -
now = InlineKeyboardButton('Текущая', callback_data='task1')
next = InlineKeyboardButton('Следующая', callback_data='task2')
get_week = InlineKeyboardMarkup(row_width=2).add(now, next, btnmenu)


# - - - Подтверждение Добавления Предмета - - -
yes = InlineKeyboardButton('Да', callback_data='yes')
no = InlineKeyboardButton('Нет', callback_data='no')
confirm = InlineKeyboardMarkup(row_width=2).add(yes, no, btnmenu)


# - - - Админ-панель - - -
up = InlineKeyboardButton('Повысить', callback_data='+1')
down = InlineKeyboardButton('Понизить', callback_data='-1')
cancel = InlineKeyboardButton('Отмена', callback_data='cancel')
admin = InlineKeyboardMarkup(row_width=2).add(up, down, cancel)
admin2 = InlineKeyboardMarkup(row_width=2).add(up, cancel)
admin3 = InlineKeyboardMarkup(row_width=2).add(down, cancel)


# - - - Класс-панель - - -
create = InlineKeyboardButton('Создать', callback_data='create')
settings = InlineKeyboardButton('Настройки', callback_data='settings')
join = InlineKeyboardButton('Войти в класс', callback_data='join')
change = InlineKeyboardButton('Сменить класс', callback_data='change')
info = InlineKeyboardButton('Инфо', callback_data='info')
admin = InlineKeyboardButton('Админ', callback_data='admin')
class_menu = InlineKeyboardMarkup(row_width=2).add(create, settings, join, change, info, admin)


# - - - Настройки-класса - - -
rename = InlineKeyboardButton('Преименовать', callback_data='rename')
repass = InlineKeyboardButton('Сменить пароль', callback_data='repass')
info = InlineKeyboardButton('Инфо', callback_data='info')
admin = InlineKeyboardButton('Админ', callback_data='admin')
delete = InlineKeyboardButton('Удалить', callback_data='delete')
class_settings = InlineKeyboardMarkup(row_width=2).add(rename, repass, info, admin, delete, btnmenu)


# - - - Выбор класса для настроек или смены текущего - - -
def class_choose(classes):
    btn_list = []
    for key, class_name in enumerate(classes):
        btn = InlineKeyboardButton(class_name[0], callback_data=str(key))
        btn_list.append(btn)
    choose_class = InlineKeyboardMarkup(row_width=2).add(*btn_list, btnmenu)
    return choose_class
