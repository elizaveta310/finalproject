from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, Filters
from telegram.ext import CommandHandler
import sqlite3 # Импорт модуля для работы с SQLite

CHOOSE, NAME, EMAIL, LEVEL = range(4)

def register_handler(update: Update, context: CallbackContext) -> int:
  user = update.effective_user
  user_id = user.id
  first_name = user.first_name

  # Сохраняем имя и id пользователя в базу данных
  user_data = {"id": user_id, "first_name": first_name}
  save_user_data(user_data) # Ф-ия для сохранения в БД

  update.message.reply_text(f"Привет, {first_name}! Чтобы зарегистрироваться на курс, пожалуйста, введите ваше имя:")

  return NAME

def register_name(update: Update, context: CallbackContext) -> int:
  user = update.effective_user
  user_id = user.id
  name = update.message.text

  # Сохраняем имя в базу данных
  update_user_data(user_id, {"name": name})

  update.message.reply_text("Теперь введите ваш email:")
  return EMAIL

def register_email(update: Update, context: CallbackContext) -> int:
  user = update.effective_user
  user_id = user.id
  email = update.message.text

  # Сохраняем email в базу данных
  update_user_data(user_id, {"email": email})

  keyboard = [
    [InlineKeyboardButton("Beginner", callback_data='beginner')],
    [InlineKeyboardButton("Intermediate", callback_data='intermediate')],
    [InlineKeyboardButton("Advanced", callback_data='advanced')],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  update.message.reply_text("Выберите ваш уровень знания английского языка:", reply_markup=reply_markup)
  return LEVEL

def register_level(update: Update, context: CallbackContext) -> int:
  query = update.callback_query
  user = query.from_user
  user_id = user.id
  level = query.data

  # Сохраняем уровень английского в базу данных
  update_user_data(user_id, {"level": level})

  update.callback_query.edit_message_text(
    text="Спасибо за регистрацию! Вы успешно зарегистрировались."
  )
  return ConversationHandler.END


def save_user_data(user_data):
  """Сохраняет данные пользователя в базу данных."""
  conn = sqlite3.connect('your_database.db') # Подключение к базе данных
  cursor = conn.cursor()

  # Создаем таблицу, если ее еще нет
  cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY,
      first_name TEXT,
      name TEXT,
      email TEXT,
      level TEXT
    )
  """)

  # Добавляем данные пользователя в таблицу
  cursor.execute(
    "INSERT INTO users (id, first_name, name, email, level) VALUES (?, ?, ?, ?, ?)",
    (user_data['id'], user_data['first_name'], user_data.get('name'), user_data.get('email'), user_data.get('level'))
  )

  conn.commit()
  conn.close()

def update_user_data(user_id, user_data):
  """Обновляет данные пользователя в базе данных."""
  conn = sqlite3.connect('your_database.db')
  cursor = conn.cursor()

  # Обновляем данные пользователя в таблице users
  cursor.execute(
    "UPDATE users SET name = ?, email = ?, level = ? WHERE id = ?",
    (user_data.get('name'), user_data.get('email'), user_data.get('level'), user_id)
  )

  conn.commit()
  conn.close()

# Регистрация обработчика
register_handler = ConversationHandler(
  entry_points=[CommandHandler('register', register_handler)],
  states={
    NAME: [MessageHandler(Filters.text & ~Filters.command, register_name)],
    EMAIL: [MessageHandler(Filters.text & ~Filters.command, register_email)],
    LEVEL: [CallbackQueryHandler(register_level)],
  },
  fallbacks=[],
)