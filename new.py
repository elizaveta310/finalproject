import telebot

from django.db import models
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from telegram.ext.dispatcher import run_async

# Модель курсов
class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    level = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

# Модель студентов
class Student(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    level = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Модель для сохранение запроса на регистрацию
class RegistrationRequest(models.Model):
    user_id = models.IntegerField()
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=50)
    contact = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Запрос от {self.name} - {self.level}"

# Модель для настройки бота
class BotSettings(models.Model):
    admin_user_id = models.IntegerField()

    def __str__(self):
        return f"Настройка бота"


# Установка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен API вашего бота
TOKEN = "7831994040:AAE69M4u7tUTT7aAattlRV8_ARZYx5H9sP8"

# Константы для сохранения диалога
(START, NAME, LEVEL, CONTACT, CONFIRM, COURSES, SELECT_COURSE, CHOOSE_COURSE) = range(8)

# Функция для оброботки команды /start
def start(update: Update, context: CallbackContext) -> int:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Привет! Я бот для записи на курс английского языка.n'
                              'Чтобы узнать про доступные курси, введите /courses.n'
                              'Чтобы записатися на курс, ввеедите /register.')
    return START

# Функция для выведения курсов
def show_courses(update: Update, context: CallbackContext) -> int:
    """Show available courses."""
    courses = Course.objects.all()
    if courses:
        message = "Доступные курсы:\n"
        for i, course in enumerate(courses):
            message += f"{i+1}. {course.name} ({course.level})\n"
            message += f"  Описание: {course.description}\n"
            message += f"  Цена: {course.price} грн\n\n"
        update.message.reply_text(message)
        return CHOOSE_COURSE
    else:
        update.message.reply_text("На даний момент курсов нету. Следите за обновлениями.")
        return START

# Функция для сбора имени
def name(update: Update, context: CallbackContext) -> int:
    """Store user's name."""
    user_name = update.message.text
    context.user_data['name'] = user_name
    update.message.reply_text(f'Спасибо! Я запомнил ваше имя: {user_name}\n'
                              'Теперь напишите уровень английского языка (начинающий, средний, продвинутый):')
    return LEVEL

# Функция для сбора уровня английского
def level(update: Update, context: CallbackContext) -> int:
    """Store user's level."""
    user_level = update.message.text
    context.user_data['level'] = user_level
    update.message.reply_text(f'Окей. Уровень: {user_level}\n'
                              'Напишите мне ваш номер телефону или електронную почту для связи:')
    return CONTACT

# Функция для сбора контактных данных
def contact(update: Update, context: CallbackContext) -> int:
    """Store user's contact."""
    user_contact = update.message.text
    context.user_data['contact'] = user_contact
    update.message.reply_text(f'Отлично! Ваши данные:\n'
                              f'Имя: {context.user_data["name"]}\n'
                              f'Уровень: {context.user_data["level"]}\n'
                              f'Контакт: {context.user_data["contact"]}\n'
                              f'Всё ли верно? Напишите "Да" для подтверждения или "Нет" для редактирования:')
    return CONFIRM

# Функция для подтверждения данных
def confirm(update: Update, context: CallbackContext) -> int:
    """Confirm user's data."""
    user_choice = update.message.text
    if user_choice.lower() == 'так':
        # Сохраняем данные пользователя в базу
        registration_request = RegistrationRequest.objects.create(
            user_id=update.effective_user.id,
            name=context.user_data["name"],
            level=context.user_data["level"],
                        contact=context.user_data["contact"],
        )
        update.message.reply_text(f'Спасибо за регистрацию! Мы свяжемся с вами в ближайшее время.\n'
                                  f'Ваш ID запрос: {registration_request.id}')
        return ConversationHandler.END
    else:
        update.message.reply_text('Окей, для начала. Введите своё имя:')
        return NAME

# Функция для выбора курса
def choose_course(update: Update, context: CallbackContext) -> int:
    """Choose a course."""
    try:
        choice = int(update.message.text)
        courses = Course.objects.all()
        if 0 < choice <= courses.count():
            selected_course = courses[choice - 1]
            context.user_data['course_id'] = selected_course.id
            update.message.reply_text(f'Вы выбрали курс: {selected_course.name}\n'
                                      f'Чтобы записаться, введите /register.')
            return START
        else:
            update.message.reply_text('Неправильный выбор. Попробуйте ещё раз.')
            return CHOOSE_COURSE
    except ValueError:
        update.message.reply_text('Введите число!')
        return CHOOSE_COURSE

# Функция для оброботки неизвестных команд
def unknown(update: Update, context: CallbackContext) -> None:
    """Handle the /unknown command."""
    update.message.reply_text('Извините, я не понимаю эту команду. Попробуйте ещё раз /start.')

@run_async
def cancel(update: Update, context: CallbackContext) -> int:
    """
    Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Диалог отменён. Чтобы начать заново, введите /start'
    )
    return ConversationHandler.END

# Функция для оброботки уведомлений администратора
def admin_message(update: Update, context: CallbackContext) -> None:
    """Handle messages from the admin user."""
    user = update.effective_user
    if user.id == context.bot_data.get('admin_id'):
        update.message.reply_text(f'Привет, админ! \n'
                                  f'Ты можешь просмотреть список зарегистрированых пользователей:\n'
                                  f'/registered_users\n\n'
                                  f'Или просмотреть список запросов на регистрацию:\n'
                                  f'/registration_requests\n')
    else:
        update.message.reply_text('Доступ запрещён.')

# Функция для выведения зарегистрированых пользователей
def registered_users(update: Update, context: CallbackContext) -> None:
    """Show registered users."""
    users = Student.objects.all()
    if users:
        message = "Зарегистрированые пользователи:\n"
        for user in users:
            message += f"Имя: {user.name}\n"
            message += f"Уровень: {user.level}\n"
            message += f"Контакт: {user.phone_number or user.email}\n\n"
        update.message.reply_text(message)
    else:
        update.message.reply_text("Зарегистрированых пользователей нету.")

# Функция для выведения запросов на регистрацию
def registration_requests(update: Update, context: CallbackContext) -> None:
    """Show registration requests."""
    requests = RegistrationRequest.objects.all()
    if requests:
        message = "Запросы на регистрацию:\n"
        for request in requests:
            message += f"ID: {request.id}\n"
            message += f"Имя: {request.name}\n"
            message += f"Уровень: {request.level}\n"
            message += f"Контакт: {request.contact}\n\n"
        update.message.reply_text(message)
    else:
        update.message.reply_text("Запросов на регистрацию нету.")

def main() -> None:
    """Start the bot."""
    updater = Updater(TOKEN)

    # Получение диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Получаем ID администратора из базы данных (если он настроен)
    admin_id = BotSettings.objects.first().admin_user_id if BotSettings.objects.exists() else None
    if admin_id:
        dispatcher.bot_data['admin_id'] = admin_id

    # Регистрация обработчиков
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('register', start)],
        states={
            START: [CommandHandler('courses', show_courses)],
            COURSES: [MessageHandler(Filters.text & ~Filters.command, choose_course)],
            CHOOSE_COURSE: [MessageHandler(Filters.text & ~Filters.command, choose_course)],
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            LEVEL: [MessageHandler(Filters.text & ~Filters.command, level)],
            CONTACT: [MessageHandler(Filters.text & ~Filters.command, contact)],
            CONFIRM: [MessageHandler(Filters.text & ~Filters.command, confirm)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conv_handler)

    # Обработчик для неизвестных команд
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Обработчик для администратора
    dispatcher.add_handler(CommandHandler('registered_users', registered_users))
    dispatcher.add_handler(CommandHandler('registration_requests', registration_requests))

    # Запуск бота
    updater.start_polling()

    # Завершение работы бота,
    # когда визывается Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()