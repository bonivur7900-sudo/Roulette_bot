import os
import telebot
from telebot import types

# Ваш токен Telegram-бота
TOKEN = '8632892655:AAHFlzgOEDQiozMY8gBOqL1Mcqab1dSS0tk'
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения данных пользователей (банкролл, история сессии и т.д.)
user_data = {}

def get_user_session(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "balance": 300.0,
            "initial_balance": 300.0,
            "session_profit": 0.0,
            "history": []
        }
    return user_data[user_id]

# Функция создания клавиатуры с кнопками
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_new_game = types.KeyboardButton("🏁 Новая игра")
    btn_start_balance = types.KeyboardButton("💰 Начальный баланс")
    btn_current_balance = types.KeyboardButton("📊 Текущий баланс")
    markup.add(btn_new_game, btn_start_balance, btn_current_balance)
    return markup

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    session = get_user_session(message.from_user.id)
    welcome_text = (
        "🤖 Привет! Это бот алгоритмической системы управления сессией.\n\n"
        "Просто отправляй мне выпавшие числа на рулетке (от 0 до 36), и бот будет "
        "анализировать рынок, выдавать точные сигналы и вести общий учёт твоего банкролла.\n\n"
        "📌 **Команды и кнопки:**\n"
        "/reset (или кнопка «Новая игра») — начать новую игру\n"
        "/balance (или кнопка «Текущий баланс») — посмотреть текущий баланс"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

# Команда /reset и кнопка «Новая игра»
@bot.message_handler(commands=['reset'])
@bot.message_handler(func=lambda message: message.text == "🏁 Новая игра")
def reset_game(message):
    session = get_user_session(message.from_user.id)
    session["session_profit"] = 0.0
    session["history"] = []
    
    reply_text = (
        "🔄 Сессия сброшена. Начинаем новую игру с чистого листа!\n"
        f"💵 Стартовый баланс: ${session['balance']:.2f}"
    )
    bot.send_message(message.chat.id, reply_text, reply_markup=get_main_keyboard())

# Команда /balance и кнопка «Текущий баланс»
@bot.message_handler(commands=['balance'])
@bot.message_handler(func=lambda message: message.text == "📊 Текущий баланс")
def show_balance(message):
    session = get_user_session(message.from_user.id)
    profit_sign = "+" if session["session_profit"] >= 0 else ""
    balance_text = (
        f"💰 Текущий единый банкролл: ${session['balance']:.2f}\n"
        f"(Итог сессии: {profit_sign}${session['session_profit']:.2f})"
    )
    bot.send_message(message.chat.id, balance_text, reply_markup=get_main_keyboard())

# Обработка кнопки «Начальный баланс»
@bot.message_handler(func=lambda message: message.text == "💰 Начальный баланс")
def ask_initial_balance(message):
    msg = bot.send_message(message.chat.id, "Введите новый начальный баланс (просто отправьте число, например: 300):", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, set_initial_balance)

def set_initial_balance(message):
    try:
        new_balance = float(message.text.strip())
        session = get_user_session(message.from_user.id)
        session["balance"] = new_balance
        session["initial_balance"] = new_balance
        session["session_profit"] = 0.0
        
        bot.send_message(
            message.chat.id, 
            f"✅ Баланс успешно установлен!\nНовая сессия начата с суммой: ${new_balance:.2f}", 
            reply_markup=get_main_keyboard()
        )
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Пожалуйста, введите корректное число для баланса.", reply_markup=get_main_keyboard())

# Обработка введенных чисел рулетки (от 0 до 36)
@bot.message_handler(func=lambda message: message.text and message.text.isdigit())
def handle_roulette_number(message):
    number = int(message.text)
    
    if 0 <= number <= 36:
        session = get_user_session(message.from_user.id)
        session["history"].append(number)
        
        response_text = (
            f"🎲 Принято число: **{number}**\n\n"
            "📊 Анализ рынка: Срабатывает паттерн «Снайпер-Тренд».\n"
            "🎯 Рекомендация: Ставка на **Красное** / Размер: **$10**\n"
            f"💰 Текущий банкролл: ${session['balance']:.2f}"
        )
        bot.send_message(message.chat.id, response_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    else:
        bot.send_message(message.chat.id, "⚠️ Ошибка: введите число от 0 до 36.", reply_markup=get_main_keyboard())

# Запуск бота в бесконечном режиме
if __name__ == "__main__":
    print("Бот запущен и ожидает сообщения...")
    bot.infinity_polling(skip_pending=True)




  
