from aiogram import executor
from dispatcher import dp
import database as db
import handlers


async def on_startup(_):
    db.db_start()
    print('Бот успешно запущен!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)