import telebot
import threading
import time

TOKEN = "8148889670:AAGeNNbk-KHhufgRQ1CYLNeMfQDJf6n8pyE"
ADMIN_ID = 5626257612  # Твой Telegram ID

bot = telebot.TeleBot(TOKEN)
user_messages = {}  # Хранит соответствие message_id ↔ user_id
user_cache = set()  # Храним ID пользователей, чтобы отправить важное сообщение только 1 раз

# Функция для предотвращения сна Railway
def prevent_sleep():
    while True:
        print("👀 Бот не спит!")
        time.sleep(300)  # Пауза в 5 минут

# Запускаем поток, который не даст Railway уснуть
threading.Thread(target=prevent_sleep, daemon=True).start()

# Обработчик сообщений от пользователей (не администраторов)
@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID)
def handle_user_message(message):
    user_id = message.chat.id

    # Отправляем админу сообщение от пользователя
    sent_message = bot.send_message(
        ADMIN_ID,
        f"📩 *Сообщение от @{message.chat.username or 'пользователя'}* (ID: {user_id}):\n\n{message.text}",
        parse_mode="Markdown"
    )

    # Запоминаем соответствие ID сообщения админа к ID пользователя
    user_messages[sent_message.message_id] = user_id  

    # Подтверждение пользователю, что его сообщение отправлено
    bot.send_message(
        user_id,
        "✅ *Ваше сообщение отправлено администратору проекта OSINT!* \n\nОжидайте, скоро к вам подключиться один из администраторов Проекта.",
        parse_mode="Markdown"
    )

    # Если пользователь пишет впервые, отправляем важное сообщение
    if user_id not in user_cache:
        bot.send_message(
            user_id,
            "⚠️ *ВАЖНОЕ СООБЩЕНИЕ:*\n"
            "— Свободный Администратор ответит в ближайшее время.\n"
            "— Не отправляйте одно и то же сообщение несколько раз.\n"
            "— Если ваш вопрос срочный, уточните это в тексте.",
            parse_mode="Markdown"
        )
        user_cache.add(user_id)  # Запоминаем, что уже отправляли это сообщение

# Обработчик ответов от администратора
@bot.message_handler(func=lambda message: message.reply_to_message and message.chat.id == ADMIN_ID)
def reply_to_user(message):
    try:
        original_message_id = message.reply_to_message.message_id  # ID исходного сообщения от админа
        user_id = user_messages.get(original_message_id)  # Получаем ID пользователя

        if user_id:
            bot.send_message(
                user_id,
                f"📩 *Ответ от Проекта:*\n\n{message.text}",
                parse_mode="Markdown"
            )
            bot.send_message(ADMIN_ID, f"✅ Ответ отправлен пользователю {user_id}!")
        else:
            bot.send_message(ADMIN_ID, "⚠️ Ошибка: Не удалось определить пользователя для ответа.")

    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Ошибка при отправке ответа: {e}")

bot.polling(none_stop=True)
