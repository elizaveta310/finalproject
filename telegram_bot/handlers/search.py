from aiogram import types, Dispatcher
from database import AsyncSessionLocal
from models.models import Course
from sqlalchemy import or_

async def search_courses(message: types.Message):
    query = message.text.replace('/search', '').strip()
    if not query:
        await message.reply("Пожалуйста, введите ключевые слова для поиска. Пример: /search Python")
        return
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Course).where(
                or_(
                    Course.name.ilike(f'%{query}%'),
                    Course.description.ilike(f'%{query}%')
                )
            )
        )
        courses = result.scalars().all()
        if courses:
            response = f"📚 **Результаты поиска по '{query}':**\n"
            for course in courses:
                response += f"{course.id}: {course.name} - {course.description}\n"
            await message.reply(response)
        else:
            await message.reply("Курсы по вашему запросу не найдены.")

def register_search_handlers(dp: Dispatcher):
    dp.register_message_handler(search_courses, commands=['search'])
