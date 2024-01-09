from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import config
import database as db
import keyboards as kb
import answers as ans


storage = MemoryStorage()
PROXY_URL = "http://proxy.server:3128"
bot = Bot(proxy=PROXY_URL, token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)


class ProfileStatesGroup(StatesGroup):

    reg = State()
    name = State()
    admin = State()
    admin2 = State()
    add_les = State()
    add_les_confirm = State()
    choose_obj = State()
    add_hw = State()
    del_hw = State()
    ch_day = State()
    get_period = State()
    get_week = State()


async def on_startup(_):
    db.db_start()
    print('Бот успешно запущен!')


async def back_menu(callback_query: types.CallbackQuery, state: FSMContext):
    global admin_on
    check = db.check_admin(callback_query.from_user.id)
    if not check or check[0] == 0 or check[0] is None:
        markup = kb.menu2
        admin_on = None
    else:
        markup = kb.menu
        admin_on = 'yes'
    await callback_query.message.edit_text(text='Меню:', reply_markup=markup)
    await state.reset_state()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if not db.check_reg(message.from_user.id):
        await message.answer('Введите имя для регистрации')
        await ProfileStatesGroup.reg.set()
    else:
        await message.answer('Вы уже зарегистрированы, открыть меню /menu')


@dp.message_handler(state=ProfileStatesGroup.reg)
async def cmd_start2(message: types.Message, state: FSMContext):
    db.registration(message.from_user.id, message.text)
    await message.answer(f'Вы успешно зарегистрировались, ваше имя "{message.text}"\nСмена имени по команде /name')
    await state.reset_state()


@dp.message_handler(commands=['name'])
async def cmd_name(message: types.Message):
    if not db.check_reg(message.from_user.id):
        await message.answer('Вы не зарегистрировались, используйте команду /start')
    else:
        await message.answer('Введите имя для регистрации')
        await ProfileStatesGroup.name.set()


@dp.message_handler(state=ProfileStatesGroup.name)
async def cmd_name2(message: types.Message, state: FSMContext):
    db.rename(message.from_user.id, message.text)
    await message.answer(f'Вы успешно сменили ваше имя на "{message.text}"')
    await state.reset_state()


@dp.message_handler(commands=['admin'])
async def cmd_admin(message: types.Message):
    global lvl_subj
    lvl_subj = db.check_admin(message.from_user.id)
    if not lvl_subj or lvl_subj[0] == 0 or lvl_subj[0] is None:
        text = 'Вы не админ'
    else:
        text = 'Напишите имя пользователя'
        await ProfileStatesGroup.admin.set()
    await message.answer(text)


@dp.message_handler(state=ProfileStatesGroup.admin)
async def cmd_admin2(message: types.Message, state: FSMContext):
    global name, lvl
    check = db.admin_check_user(message.text)
    if not check:
        text = f'Нет такого пользователя {message.text}'
        markup = None
        await state.reset_state()
    else:
        name = check[0]
        if not check[1]:
            text = f'{name}, уровень админа: Нет\nВыберите что сделать с пользователем?'
            markup = kb.admin2
            lvl = int(0)
            await ProfileStatesGroup.admin2.set()
        else:
            if check[1] < lvl_subj[0]:
                text = f'{name}, уровень админа: 1\nВыберите что сделать с пользователем?'
                markup = kb.admin
                lvl = int(1)
                await ProfileStatesGroup.admin2.set()
            else:
                text = f'Уровень админа {name} выше или равен вашему'
                markup = None
                await state.reset_state()
    if not markup:
        await message.answer(text)
    else:
        await message.answer(text, reply_markup=markup)


@dp.callback_query_handler(state=ProfileStatesGroup.admin2)
async def cmd_admin3(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'cancel':
        text='Отмена'
    else:
        adm_lvl = callback_query.data
        new_lvl = lvl+int(adm_lvl)
        db.admin_change(new_lvl, name)
        text=f'Уровень админа пользователя {name} был изменен до {str(new_lvl)}'
    await callback_query.message.edit_text(text=text)
    await state.reset_state()



@dp.message_handler(commands=['menu'])
async def cmd_menu(message: types.Message):
    global admin_on
    check = db.check_admin(message.from_user.id)
    if not check or check[0] == 0 or check[0] is None:
        markup = kb.menu2
        admin_on = None
    else:
        markup = kb.menu
        admin_on = 'yes'
    await message.answer('Меню:', reply_markup=markup)


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
    if callback_query.data == 'menu':
        await back_menu(callback_query, state)
    elif callback_query.data == 'week' or operation == 'add_hw' or operation == 'get_hw' or operation == 'del_hw':
        if operation == 'get_hw' or operation == 'add_hw' or operation == 'del_hw':
            await callback_query.message.edit_text(text='Выберите неделю:', reply_markup=kb.get_week)
            await ProfileStatesGroup.get_week.set()
        else:
            answer = ans.schedule_get_all(operation, None, None, None)
            await callback_query.message.edit_text(text=answer)
            await state.reset_state()
    else:
        match operation:
            case 'add_les':
                await callback_query.message.edit_text(text='Назовите предмет')
                await ProfileStatesGroup.add_les.set()
            case 'get_les':
                time = '0'
                record = 'rec_week1'
                answer = ans.schedule_get(day, day_name, operation, time, record)
                await callback_query.message.edit_text(text=answer)
                await state.reset_state()
            case _:
                answer, markup = ans.schedule_choose_obj(day, day_name)
                if not markup:
                    await callback_query.message.edit_text(text=answer)
                    await state.reset_state()
                else:
                    await callback_query.message.edit_text(text=answer, reply_markup=markup)
                    await ProfileStatesGroup.choose_obj.set()


@dp.message_handler(state=ProfileStatesGroup.add_les)
async def add_les(message: types.Message, state: FSMContext):
    global les
    les = message.text
    if not db.check_obj(day, les):
        await message.answer(f'Подтвердите добавление предмета {les}', reply_markup=kb.confirm)
        await ProfileStatesGroup.add_les_confirm.set()
    else:
        await message.answer(f'Предмет {les} уже существует')
        await state.reset_state()


@dp.callback_query_handler(state=ProfileStatesGroup.add_les_confirm)
async def add_les_confirm(callback_query: types.CallbackQuery, state: FSMContext):
    match callback_query.data:
        case 'yes':
            await callback_query.message.edit_text(text=f'Предмет {les} добавлен')
            db.add_les(les, day)
            await state.reset_state()
        case 'no':
            await callback_query.message.edit_text(text='Назовите предмет')
            await ProfileStatesGroup.add_les.set()
        case 'menu':
            await back_menu(callback_query, state)


@dp.callback_query_handler(state=ProfileStatesGroup.choose_obj)
async def choose_obj(callback_query: types.CallbackQuery, state: FSMContext):
    global obj, task_s, task_s3
    if callback_query.data == 'menu':
        await back_menu(callback_query, state)
        return
    obj = db.get_schedule(day)[int(callback_query.data)][0]
    match operation:
        case 'add_hw':
            await callback_query.message.edit_text(text=f'Напишите ДЗ к предмету {obj}')
            await ProfileStatesGroup.add_hw.set()
        case 'del_les':
            db.del_obj(obj, day)
            await callback_query.message.edit_text(text=f'Предмет {obj} удалён')
            await state.reset_state()
        case 'del_hw':
            if not db.check_hw(obj, day, week, time, record):
                await callback_query.message.edit_text(text=f'Нет ДЗ у предмета {obj}')
                await state.reset_state()
            else:
                tasks = ''.join(db.get_hw(obj, day, week))
                task_s2 = tasks.split('. ')
                if not admin_on:
                    task_s, task_s3 = ans.schedule_del_hw_not_adm(task_s2, callback_query.from_user.id)
                else:
                    task_s = task_s2
                if len(task_s2) > 1:
                    if len(task_s) > 1:
                        answer, markup = ans.schedule_del_hw(task_s)
                        await callback_query.message.edit_text(text=answer, reply_markup=markup)
                        await ProfileStatesGroup.del_hw.set()
                    else:
                        task = '. '.join(task_s3)
                        db.del_hw2(obj, task, day, week)
                        await callback_query.message.edit_text(text=f'ДЗ предмета {obj} удалено')
                        await state.reset_state()
                else:
                    db.del_hw(obj, day, week, record)
                    await callback_query.message.edit_text(text=f'ДЗ предмета {obj} удалено')
                    await state.reset_state()


@dp.callback_query_handler(state=ProfileStatesGroup.get_week)
async def get_week(callback_query: types.CallbackQuery, state: FSMContext):
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
    match callback_query.data:
        case 'menu':
            await back_menu(callback_query, state)
        case _:
            if operation == 'add_hw' or operation == 'del_hw':
                answer, markup = ans.schedule_choose_obj(day, day_name)
                if not markup:
                    await callback_query.message.edit_text(text=answer)
                    await state.reset_state()
                else:
                    await callback_query.message.edit_text(text=answer, reply_markup=markup)
                    await ProfileStatesGroup.choose_obj.set()
            else:
                if day == 'week':
                    answer = ans.schedule_get_all(operation, week, time, record)
                else:
                    answer = ans.schedule_get(day, day_name, operation, time, record)
                await callback_query.message.edit_text(text=answer)
                await state.reset_state()


@dp.message_handler(state=ProfileStatesGroup.add_hw)
async def add_hw(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if not db.check_hw(obj, day, week, time, record):
        task = f'{id}, {message.text}'
    else:
        task = db.get_hw(obj, day, week)
        task += f'. {id}, {message.text}'
    db.add_hw(obj, task, day, week, time, record)
    await bot.send_message(chat_id=message.chat.id, text=f'Задание "{message.text}" добавлено')
    await state.reset_state()


@dp.callback_query_handler(state=ProfileStatesGroup.del_hw)
async def del_hw(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'menu':
        await back_menu(callback_query, state)
    else:
        task_id = callback_query.data
        task_s.pop(int(task_id)-1)
        task = '. '.join(task_s)
        if not admin_on:
            task += '. ' + '. '.join(task_s3)
        db.del_hw2(obj, task, day, week)
        await callback_query.message.edit_text(text=f'ДЗ {task_id} удалено')
        await state.reset_state()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
