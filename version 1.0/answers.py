from aiogram.types import InlineKeyboardMarkup
import database as db
import keyboards as kb


def schedule_get(day, day_name, operation, time, record)->(str):
    answer = f'<b>{day_name}:</b>\n'
    schedules = db.get_schedule(day)
    if not schedules:
        answer += 'Нет записей предметов\n'
    else:
        for schedule in schedules:
            if operation == 'get_hw':
                answer += f'{schedule[0]} - '
                b = str(int(db.get_schedule_check(time)))
                if record == 'rec_week1':
                    a = str(schedule[4])
                    i = 1
                else:
                    a = str(schedule[5])
                    i = 2
                if a == b:
                    tasks = ''.join(schedule[i])
                    task_s = tasks.split('. ')
                    for tasks1 in task_s:
                        task = ''.join(tasks1)
                        task1 = task.split(', ')
                        answer += f'{task1[1]}\n'
                else:
                    answer += 'Нет записей ДЗ\n'
            else: answer += f'{schedule[0]}\n'
    return answer


def schedule_get_all(operation, week, time, record)->(str):
    text = []
    day = ['day1', 'day2', 'day3', 'day4', 'day5']
    day_name = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
    for i in range(0, 5):
        s = schedule_get(day[i], day_name[i], operation, time, record)
        text.append(s)
    text_all = '\n'.join(text)
    if operation == 'get_hw':
        if week == 'task2':
            period = db.week_period2()
        else: period = db.week_period()
        answer = f'{period[0]} - {period[1]}\n'
        answer += text_all
    else: answer = text_all
    return answer


def schedule_choose_obj(day, day_name)->(str, InlineKeyboardMarkup):
    schedules = db.get_schedule(day)
    answer = f'<b>{day_name}</b>'
    if not schedules:
        answer += '\nНет записей предметов'
        markup = None
    else:
        kb.kb_choose_obj(day)
        answer += ', выберите предмет:'
        markup = kb.choose_obj
    return answer, markup


def schedule_del_hw(task_s)->(str, InlineKeyboardMarkup):
    markup = kb.kb_del_hw(len(task_s))
    answer = 'Выберите ДЗ: \n'
    for key, tasks1 in enumerate(task_s):
        task = ''.join(tasks1)
        task1 = task.split(', ')
        answer += f'{str(key+1)}. {task1[1]}\n'
    return answer, markup


def schedule_del_hw_not_adm(task_s2, user_id):
    task_s = []
    task_s3 = []
    for tasks1 in task_s2:
        task = ''.join(tasks1)
        task1 = task.split(', ')
        if int(task1[0]) == user_id:
            tas = ', '.join(task1)
            task_s.append(tas)
        if int(task1[0]) != user_id:
            tas = ', '.join(task1)
            task_s3.append(tas)
    return task_s, task_s3
