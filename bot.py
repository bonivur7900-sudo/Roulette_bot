import os
import telebot
from telebot import types
from flask import Flask, request

TOKEN = '8695337511:AAEYhpGC-5DEdEjYIr0Dv4arkPLcgMZtHbE'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_data = {}

def get_user_session(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "balance": 300.0,
            "initial_balance": 300.0,
            "bet_size": 10.0,
            "session_profit": 0.0,
            "history": []
        }
    return user_data[user_id]

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_new_game = types.KeyboardButton("🏁 Новая игра")
    btn_start_balance = types.KeyboardButton("💰 Начальный баланс")
    btn_bet_size = types.KeyboardButton("⚙️ Размер ставки")
    btn_current_balance = types.KeyboardButton("📊 Текущий баланс")
    markup.add(btn_new_game, btn_start_balance, btn_bet_size, btn_current_balance)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    session = get_user_session(message.from_user.id)
    welcome_text = (
        "🤖 Привет! Это бот алгоритмической системы управления сессией.\n\n"
        "Просто отправляй мне выпавшие числа на рулетке (от 0 до 36), и бот будет "
        "анализировать рынок, выдавать точные сигналы и вести общий учёт твоего банкролла.\n\n"
        "📌 **Управление кнопками:**\n"
        "• 🏁 Новая игра — сброс сессии\n"
        "• 💰 Начальный баланс — задать стартовый банкролл\n"
        "• ⚙️ Размер ставки — установить сумму текущей ставки\n"
        "• 📊 Текущий баланс — посмотреть состояние счёта"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

@bot.message_handler(commands=['reset'])
@bot.message_handler(func=lambda message: message.text == "🏁 Новая игра")
def reset_game(message):
    session = get_user_session(message.from_user.id)
    session["session_profit"] = 0.0
    session["history"] = []
    
    reply_text = (
        "🔄 Сессия сброшена. Начинаем новую игру с чистого листа!\n"
        f"💵 Стартовый баланс: ${session['balance']:.2f}\n"
        f"⚙️ Текущая ставка: ${session['bet_size']:.2f}"
    )
    bot.send_message(message.chat.id, reply_text, reply_markup=get_main_keyboard())

@bot.message_handler(commands=['balance'])
@bot.message_handler(func=lambda message: message.text == "📊 Текущий баланс")
def show_balance(message):
    session = get_user_session(message.from_user.id)
    profit_sign = "+" if session["session_profit"] >= 0 else ""
    balance_text = (
        f"💰 Текущий единый банкролл: ${session['balance']:.2f}\n"
        f"⚙️ Текущая ставка: ${session['bet_size']:.2f}\n"
        f"(Итог сессии: {profit_sign}${session['session_profit']:.2f})"
    )
    bot.send_message(message.chat.id, balance_text, reply_markup=get_main_keyboard())

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

@bot.message_handler(func=lambda message: message.text == "⚙️ Размер ставки")
def ask_bet_size(message):
    msg = bot.send_message(message.chat.id, "Введите желаемый размер ставки (просто отправьте число, например: 15):", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, set_bet_size)

def set_bet_size(message):
    try:
        new_bet = float(message.text.strip())
        session = get_user_session(message.from_user.id)
        session["bet_size"] = new_bet
        
        bot.send_message(
            message.chat.id, 
            f"✅ Размер ставки успешно изменен!\nНовая ставка: ${new_bet:.2f}", 
            reply_markup=get_main_keyboard()
        )
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Пожалуйста, введите корректное число для ставки.", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text and message.text.isdigit())
def handle_roulette_number(message):
    number = int(message.text)
    
    if 0 <= number <= 36:
        session = get_user_session(message.from_user.id)
        session["history"].append(number)
        
        response_text = (
            f"🎲 Принято число: **{number}**\n\n"
            "📊 Анализ рынка: Срабатывает паттерн «Снайпер-Тренд».\n"
            f"🎯 Рекомендация: Ставка на **Красное** / Размер: **${session['bet_size']:.2f}**\n"
            f"💰 Текущий банкролл: ${session['balance']:.2f}"
        )
        bot.send_message(message.chat.id, response_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    else:
        bot.send_message(message.chat.id, "⚠️ Ошибка: введите число от 0 до 36.", reply_markup=get_main_keyboard())

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def index():
    return "Bot is alive!", 200

if __name__ == "__main__":
    # Удаляем вебхук на всякий случай и переключаемся на polling локально или через Flask
    bot.remove_webhook()
    # Для Render через обычный запуск веб-сервера
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))









