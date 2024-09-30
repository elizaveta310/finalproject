from aiogram import types, Dispatcher
from database import AsyncSessionLocal
from models.models import User
from datetime import datetime

async def register_user(message: types.Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            User.__table__.select().where(User.telegram_id == str(message.from_user.id))
        )
        user = result.fetchone()
        if not user:
            new_user = User(
                name=message.from_user.full_name,
                telegram_id=str(message.from_user.id)
            )
            session.add(new_user)
            await session.commit()
            await message.reply("Вы успешно зарегистрированы!")
        else:
            await message.reply("Вы уже зарегистрированы.")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(register_user, commands=['register'])
