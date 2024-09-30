from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import BOT_TOKEN
from database import init_db
from handlers.main import register_handlers

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Привет! Я помогу записаться на курсы английского языка.")

async def on_startup(dispatcher):
    await init_db()
    print("База данных инициализирована.")
    register_handlers(dispatcher)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
