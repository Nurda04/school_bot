from aiogram import types
from dispatcher import dp
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import database as db
import keyboards as kb
import answers as ans


class ProfileStatesGroup(StatesGroup):

    add_les = State()
    add_les_confirm = State()
    choose_obj = State()
    add_hw = State()
    del_hw = State()
    ch_day = State()
    get_period = State()
    get_week = State()


async def back_menu(callback_query: types.CallbackQuery, state: FSMContext):
    global admin_on, cur_class
    cur_class = db.get_class(callback_query.from_user.id)
    check = db.check_admin(callback_query.from_user.id)
    if not check or check[0] == 0:
        markup = kb.menu2
        admin_on = None
    else:
        markup = kb.menu
        admin_on = 'yes'
    await callback_query.message.edit_text(text='Меню:', reply_markup=markup)
    await state.reset_state() 


@dp.message_handler(commands=['menu'])
async def cmd_menu(message: types.Message):
    global admin_on, cur_class
    markup = None
    cur_class = db.get_class_current(message.from_user.id)
    if not cur_class or cur_class[0] is None:
        text = 'У вас не выбран класс, для выбора /class'
    else:
        check = db.check_admin(message.from_user.id, cur_class[0])
        cur_class = cur_class[0]
        if check == 0:
            markup = kb.menu3
        elif check == 1:
            markup = kb.menu2
            admin_on = None
        else: 
            markup = kb.menu
            admin_on = 'yes'
        text = 'Меню:'
    await message.answer(text, reply_markup=markup)    


@dp.callback_query_handler()
async def choose_operation(callback_query: types.CallbackQuery, state: FSMContext):
    global operation
    operation = callback_query.data    
    if operation == 'get_hw' or operation == 'get_les': 
        markup = kb.choose_day2
    else:
        markup = kb.choose_day
    await ProfileStatesGroup.ch_day.set()
    await callback_query.message.edit_text(text='Выберите день:', reply_markup=markup)


@dp.callback_query_handler(state=ProfileStatesGroup.ch_day)
async def choose_day(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'menu':
        await back_menu(callback_query, state)
        return
    global day, day_name
    days = {
        "day1" : "Понедельник",
        "day2" : "Вторник",
        "day3" : "Среда",
        "day4" : "Четверг",
        "day5" : "Пятница"
    }
    day_name = days.get(callback_query.data)
    day = callback_query.data
    markup = None
    if callback_query.data == 'week' or operation == 'add_hw' or operation == 'get_hw' or operation == 'del_hw':
        if operation == 'get_hw' or operation == 'add_hw' or operation == 'del_hw':
            text = 'Выберите неделю:'
            markup=kb.get_week
            await ProfileStatesGroup.get_week.set()
        else:
            answer = ans.schedule_get_all(operation, None, None, None, cur_class)
            text = answer
            await state.reset_state()
    else:
        match operation:
            case 'add_les':
                text = 'Назовите предмет'
                await ProfileStatesGroup.add_les.set()
            case 'get_les':
                time = '0'
                record = 'rec_week1'
                text = ans.schedule_get(day, day_name, operation, time, record, cur_class)
                await state.reset_state()
            case _:
                text, markup = ans.schedule_choose_obj(day, day_name, cur_class)
                if not markup:
                    await state.reset_state()
                else:
                    await ProfileStatesGroup.choose_obj.set()
    await callback_query.message.edit_text(text=text, reply_markup=markup)


@dp.message_handler(state=ProfileStatesGroup.add_les)
async def add_les(message: types.Message, state: FSMContext):
    global les
    les = message.text
    markup = None
    if not db.check_obj(day, les, cur_class):
        text = f'Подтвердите добавление предмета {les}'
        markup=kb.confirm
        await ProfileStatesGroup.add_les_confirm.set()
    else: 
        text = f'Предмет {les} уже существует'
        await state.reset_state()
    await message.answer(text, reply_markup=markup)


@dp.callback_query_handler(state=ProfileStatesGroup.add_les_confirm)
async def add_les_confirm(callback_query: types.CallbackQuery, state: FSMContext):
    match callback_query.data:
        case 'yes':
            await callback_query.message.edit_text(text=f'Предмет {les} добавлен')
            db.add_les(les, day, cur_class)
            await state.reset_state()
        case 'no':
            await callback_query.message.edit_text(text='Назовите предмет')
            await ProfileStatesGroup.add_les.set()
        case 'menu':
            await back_menu(callback_query, state)
    

@dp.callback_query_handler(state=ProfileStatesGroup.choose_obj)
async def choose_obj(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'menu':
        await back_menu(callback_query, state)
        return
    global obj, task_s, task_s3
    obj = db.get_schedule(day, cur_class)[int(callback_query.data)][0]
    markup = None
    match operation:
        case 'add_hw':
            text = f'Напишите ДЗ к предмету {obj}'
            await ProfileStatesGroup.add_hw.set()
        case 'del_les':
            db.del_obj(obj, day, cur_class)
            text = f'Предмет {obj} удалён'
            await state.reset_state()
        case 'del_hw': 
            if not db.check_hw(obj, day, week, time, record, cur_class):
                text = f'Нет ДЗ у предмета {obj}'
                await state.reset_state()
            else:
                tasks = ''.join(db.get_hw(obj, day, week, cur_class))
                task_s2 = tasks.split('. ')
                if not admin_on:
                    task_s, task_s3 = ans.schedule_del_hw_not_adm(task_s2, callback_query.from_user.id)
                else:
                    task_s = task_s2
                if len(task_s2) > 1:
                    if len(task_s) > 1:
                        answer, markup = ans.schedule_del_hw(task_s)
                        text = answer
                        await ProfileStatesGroup.del_hw.set()
                    else:
                        task = '. '.join(task_s3)
                        db.del_hw2(obj, task, day, week, cur_class)
                        text = f'ДЗ предмета {obj} удалено'
                        await state.reset_state()
                else: 
                    db.del_hw(obj, day, week, record, cur_class)
                    text = f'ДЗ предмета {obj} удалено'
                    await state.reset_state()
    await callback_query.message.edit_text(text=text, reply_markup=markup)
    

@dp.callback_query_handler(state=ProfileStatesGroup.get_week)
async def get_week(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'menu':
        await back_menu(callback_query, state)
        return
    global week, time, record
    week = callback_query.data
    times = {
        "task1": "0",
        "task2": "7"
    }
    time = times.get(week)
    records = {
        "task1": "rec_week1",
        "task2": "rec_week2"
    }
    record = records.get(week)
    markup = None
    if operation == 'add_hw' or operation == 'del_hw':
        text, markup = ans.schedule_choose_obj(day, day_name, cur_class)
        if not markup:
            await state.reset_state()
        else:    
            await ProfileStatesGroup.choose_obj.set()
    else:
        if day == 'week':
            text = ans.schedule_get_all(operation, week, time, record, cur_class)
        else: 
            text = ans.schedule_get(day, day_name, operation, time, record, cur_class)
        await state.reset_state()
    await callback_query.message.edit_text(text=text, reply_markup=markup)


@dp.message_handler(state=ProfileStatesGroup.add_hw)
async def add_hw(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if not db.check_hw(obj, day, week, time, record, cur_class):
        task = f'{id}, {message.text}'
    else:
        task = db.get_hw(obj, day, week, cur_class)
        task += f'. {id}, {message.text}'
    db.add_hw(obj, task, day, week, time, record, cur_class)
    await message.answer(f'Задание "{message.text}" добавлено')
    await state.reset_state()


@dp.callback_query_handler(state=ProfileStatesGroup.del_hw)
async def del_hw(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'menu':
        await back_menu(callback_query, state)
        return
    task_id = callback_query.data
    task_s.pop(int(task_id)-1)
    task = '. '.join(task_s)
    if not admin_on:
        task += '. ' + '. '.join(task_s3)
    db.del_hw2(obj, task, day, week, cur_class)
    await callback_query.message.edit_text(text=f'ДЗ {task_id} удалено')
    await state.reset_state()