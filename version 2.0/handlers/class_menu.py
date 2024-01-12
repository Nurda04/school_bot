from aiogram import types
from dispatcher import dp
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import database as db
import keyboards as kb
import answers as ans


class ProfileStatesGroup(StatesGroup):

    class_name = State()
    class_password = State()
    class_join = State()
    class_join2 = State()
    choose_op = State()
    choose_class = State()
    class_settings = State()
    class_settings2 = State()
    class_admin = State()
    class_admin2 = State()


async def back_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(text='Класс-меню:', reply_markup=kb.class_menu)
    await ProfileStatesGroup.choose_op.set()


@dp.message_handler(commands=['class'])
async def cmd_class(message: types.Message):
    if not db.check_reg(message.from_user.id):
        await message.answer('Вы не зарегистрированы, для регистрации /start')
    else: 
        await message.answer('Класс-меню:', reply_markup=kb.class_menu)
        await ProfileStatesGroup.choose_op.set()


@dp.callback_query_handler(state=ProfileStatesGroup.choose_op)
async def choose_operation(callback_query: types.CallbackQuery, state: FSMContext):
    global operation, classes
    markup = None
    operation = callback_query.data
    if callback_query.data == 'create':
        check = db.check_class_count(callback_query.from_user.id)
        if len(check) >= 2:
            text = 'У вас превышено количество созданных классов'
            await state.reset_state()
        else:
            text = 'Задайте имя для вашего класса'
            await ProfileStatesGroup.class_name.set()
    elif callback_query.data == 'join':
        text = 'Введите название класса'
        await ProfileStatesGroup.class_join.set()
    else:
        if callback_query.data == 'settings':
            classes = db.get_classes_created(callback_query.from_user.id)
        elif callback_query.data == 'change':
            classes = db.get_classes(callback_query.from_user.id)
        else:
            classes = db.get_classes_admin(callback_query.from_user.id, 2)
        if not classes:
            if callback_query.data == 'settings':
                text = 'У вас нет созданных классов'
            elif callback_query.data == 'change':
                text = 'Вы не состоите ни в одном классе'
            else:
                text = 'Вы не являетесь админом ни в одном классе'
            await state.reset_state()
        else:
            text = 'Выберите класс:'
            markup = kb.class_choose(classes)
            await ProfileStatesGroup.choose_class.set()
    await callback_query.message.edit_text(text=text, reply_markup=markup)


@dp.message_handler(state=ProfileStatesGroup.class_name)
async def class_create(message: types.Message, state: FSMContext):
    if not db.check_class(message.text):
        global class_name
        class_name = message.text
        text = f'Название "{message.text}" записано.\nЗадайте пароль для вашего класса'
        await ProfileStatesGroup.class_password.set()
    else:
        text = f'Название "{message.text}" занято, попробуйте другое'
        await ProfileStatesGroup.class_name.set()
    await message.answer(text)


@dp.message_handler(state=ProfileStatesGroup.class_password)
async def class_create2(message: types.Message, state: FSMContext):
    password = message.text
    db.reg_class(class_name, password, message.from_user.id)
    await message.answer(f'Ваш класс успешно создан!\nНазвание: {class_name}\nПароль: {password}\nДля приглашения пользователей передайте им название и пароль')
    await state.reset_state()


@dp.message_handler(state=ProfileStatesGroup.class_join)
async def class_join(message: types.Message, state: FSMContext):
    global check
    check = db.class_get_pass(message.text)
    if not check:
        text = f'Нет класса "{message.text}"'
        await state.reset_state()
    else:
        check2 = db.class_check_join(message.text, message.from_user.id)
        if not check2:
            global class_name
            class_name = message.text
            text = 'Введите пароль'
            await ProfileStatesGroup.class_join2.set()
        else:
            text = f'Вы уже состоите в классе "{message.text}"'
            await state.reset_state()
    await message.answer(text)


@dp.message_handler(state=ProfileStatesGroup.class_join2)
async def class_join2(message: types.Message, state: FSMContext):
    if check[0] == message.text:
        text = f'Вы вошли в класс "{class_name}"'
        db.class_join(class_name, message.from_user.id)
    else:
        text = 'Неверный пароль'
    await state.reset_state()
    await message.answer(text)


@dp.callback_query_handler(state=ProfileStatesGroup.choose_class)
async def choose_class(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'menu':
        await back_menu(callback_query, state)
        return
    global class_name
    class_name = classes[int(callback_query.data)][0]
    markup = None
    if operation == 'change':
        db.class_change(class_name, callback_query.from_user.id)
        text = f'Ваш текущий класс сменен на "{class_name}"'
        await state.reset_state()
    elif operation == 'admin':
        text = 'Напишите имя пользователя'
        await ProfileStatesGroup.class_admin.set()
    elif operation == 'info':
        text = ans.class_info(class_name, operation)
        await state.reset_state()
    else: 
        text = 'Выберите что сделать:'
        markup = kb.class_settings
        await ProfileStatesGroup.class_settings.set()
    await callback_query.message.edit_text(text=text, reply_markup=markup)


@dp.callback_query_handler(state=ProfileStatesGroup.class_settings)
async def class_settings(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'menu':
        await back_menu(callback_query, state)
        return
    global settings
    settings = callback_query.data
    if callback_query.data == 'rename' or callback_query.data == 'repass':
        if callback_query.data == 'rename':
            text = 'Введите новое название'
        elif callback_query.data == 'repass':
            text = 'Введите новый пароль'
        await ProfileStatesGroup.class_settings2.set()
    elif callback_query.data == 'admin':
        text = 'Напишите имя пользователя'
        await ProfileStatesGroup.class_admin.set()
    else:
        if callback_query.data == 'info':
            text = ans.class_info(class_name, None)
        elif callback_query.data == 'delete':
            text = f'Класс "{class_name}" удален'
            db.class_del(class_name)
        await state.reset_state()
    await callback_query.message.edit_text(text=text)


@dp.message_handler(state=ProfileStatesGroup.class_settings2)
async def class_settings2(message: types.Message, state: FSMContext):
    if settings == 'rename':
        if message.text == '/cancel':
            text = 'Переименование отменено'
            await state.reset_state()
        else:
            if not db.check_class(message.text):
                text = f'Название сменено на "{message.text}"'
                db.class_rename(message.text, class_name)
                await state.reset_state()
            else:
                text = f'Название "{message.text}" занято, попробуйте другое\nДля отмены /cancel'
                await ProfileStatesGroup.class_settings2.set()
    else:
        text = f'Пароль сменен на "{message.text}"'
        db.class_repass(message.text, class_name)
        await state.reset_state()
    await message.answer(text)


@dp.message_handler(state=ProfileStatesGroup.class_admin)
async def class_admin(message: types.Message, state: FSMContext):
    global name, lvl
    markup = None
    lvl = db.admin_check_user(message.text, class_name)
    check = db.get_name(message.from_user.id)
    if not lvl:
        text = f'Нет такого пользователя {message.text}'
        await state.reset_state()
    elif check == message.text:
        text = f'{message.text} это вы'
        await state.reset_state()
    else:
        name = message.text
        if lvl[0] == 0:
            text = f'{name}, уровень: Участник'
            markup = kb.admin2
        elif lvl[0] == 1:
            text = f'{name}, уровень: Модератор'
            markup = kb.admin
        else:
            if operation == 'admin':
                if lvl[0] == 2:
                    text = f'Пользователь {message.text} является админом'
                else:
                    text = f'Пользователь {message.text} является владельцем'
                await state.reset_state()
                await message.answer(text, reply_markup=markup)
                return
            else:
                text = f'{name}, уровень: Админ'
                markup = kb.admin3
        await ProfileStatesGroup.class_admin2.set()
    await message.answer(text, reply_markup=markup)


@dp.callback_query_handler(state=ProfileStatesGroup.class_admin2)
async def class_admin2(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'cancel':
        text='Отмена'
    else:
        admin_name = {
            0 : 'Участник',
            1 : 'Модератор',
            2 : 'Админ'
        }
        grade = {
            '+1' : 'повышен',
            '-1' : 'понижен'
        }
        admin_name = admin_name.get(lvl[0])
        grade = grade.get(callback_query.data)
        new_lvl = lvl[0]+int(callback_query.data)
        db.admin_change(new_lvl, name, class_name)
        text=f'Уровень {name} был {grade} до: {admin_name}'
    await callback_query.message.edit_text(text=text)
    await state.reset_state()