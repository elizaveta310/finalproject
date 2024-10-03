import requests
from aiogram import types, Dispatcher

async def get_weather(message: types.Message):
    city = message.text.split('/weather')[1].strip()
    if not city:
        await message.reply("Пожалуйста, укажите город. Пример: /weather Москва")
        return
    api_key = 'your_openweathermap_api_key'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        await message.reply(f"🌤 Погода в {city}:\n{weather.capitalize()}, температура: {temp}°C")
    else:
        await message.reply("Не удалось получить данные о погоде. Проверьте название города.")

def register_weather_handlers(dp: Dispatcher):
    dp.register_message_handler(get_weather, commands=['weather'])
