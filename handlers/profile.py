from aiogram import types
from dispatcher import dp
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import database as db
import keyboards as kb
import answers as ans


class ProfileStatesGroup(StatesGroup):

    reg = State()
    name = State()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if not db.check_reg(message.from_user.id):
        text = 'Введите имя для регистрации'
        await ProfileStatesGroup.reg.set()
    else: 
        text = 'Вы уже зарегистрированы'
    await message.answer(text)


@dp.message_handler(state=ProfileStatesGroup.reg)
async def cmd_start2(message: types.Message, state: FSMContext):
    if not db.check_name(message.text):
        db.registration(message.from_user.id, message.text)
        text = f'Вы успешно зарегистрировались, ваше имя "{message.text}"\nСмена имени по команде /name'
        await state.reset_state()
    else:
        text = f'Имя "{message.text}" занято, попробуйте другое'
        await ProfileStatesGroup.reg.set()
    await message.answer(text)


@dp.message_handler(commands=['name'])
async def cmd_name(message: types.Message):
    if not db.check_reg(message.from_user.id):
        text = 'Вы не зарегистрировались, используйте команду /start'
    else:
        text = 'Введите новое имя'
        await ProfileStatesGroup.name.set()
    await message.answer(text)


@dp.message_handler(state=ProfileStatesGroup.name)
async def cmd_name2(message: types.Message, state: FSMContext):
    if message.text == '/cancel':
        text = 'Переименование отменено'
        await state.reset_state()
    else:
        if not db.check_name(message.text):
            db.rename(message.from_user.id, message.text)
            text = f'Вы успешно сменили ваше имя на "{message.text}"'
            await state.reset_state()
        else:
            text = f'Имя "{message.text}" занято, попробуйте другое\nДля отмены /cancel'
            await ProfileStatesGroup.name.set()
    await message.answer(text)


@dp.message_handler(commands=['profile'])
async def cmd_name(message: types.Message):
    if not db.check_reg(message.from_user.id):
        text = 'Вы не зарегистрировались, используйте команду /start'
    else:
        text = ans.profile_get(message.from_user.id)
    await message.answer(text)