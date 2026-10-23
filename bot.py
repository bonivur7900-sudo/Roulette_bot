

import telebot
from telebot import types

# --- ГЛАВНАЯ КЛАВИАТУРА С КНОПКАМИ ---
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_new_game = types.KeyboardButton("🏁 Новая игра")
    btn_balance = types.KeyboardButton("💰 Начальный баланс")
    btn_info = types.KeyboardButton("📊 Текущий баланс")
    
    # Распределяем кнопки по рядам
    markup.row(btn_new_game, btn_balance)
    markup.row(btn_info)
    return markup


# --- 1. КНОПКА "🏁 Новая игра" И КОМАНДЫ /start, /reset ---
@bot.message_handler(commands=['start', 'reset'])
@bot.message_handler(func=lambda msg: msg.text == "🏁 Новая игра")
def start_new_game(message):
    global bankroll  # Замените на имя вашей переменной баланса, если нужно
    
    text = (
        "🎲 **Новая игра начата!**\n\n"
        "Отправляй мне выпавшие числа рулетки (от 0 до 36).\n"
        "Для управления банкроллом используй кнопки ниже:"
    )
    bot.send_message(
        message.chat.id, 
        text, 
        reply_markup=get_main_keyboard(), 
        parse_mode="Markdown"
    )


# --- 2. КНОПКА "💰 Начальный баланс" ---
@bot.message_handler(func=lambda msg: msg.text == "💰 Начальный баланс")
def ask_for_balance(message):
    msg = bot.send_message(
        message.chat.id,
        "✏️ **Введите новый начальный баланс** (просто отправьте число, например: `500`):",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_balance_input)


def process_balance_input(message):
    global bankroll  # Имя вашей переменной баланса
    
    # Отмена ввода при нажатии любой другой кнопки
    if message.text in ["🏁 Новая игра", "💰 Начальный баланс", "📊 Текущий баланс"]:
        bot.send_message(message.chat.id, "⚠️ Ввод баланса отменен.", reply_markup=get_main_keyboard())
        return

    try:
        clean_text = message.text.replace('$', '').strip()
        new_balance = float(clean_text)
        
        bankroll = new_balance  # Сохраняем баланс
        
        bot.send_message(
            message.chat.id,
            f"✅ **Баланс успешно установлен!**\nНовая сессия начата с суммой: **${new_balance:.2f}**",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    except ValueError:
        bot.send_message(
            message.chat.id,
            "❌ **Ошибка!** Вы ввели не число. Нажмите кнопку «💰 Начальный баланс» и попробуйте еще раз.",
            reply_markup=get_main_keyboard()
        )


# --- 3. КНОПКА "📊 Текущий баланс" ---
@bot.message_handler(func=lambda msg: msg.text == "📊 Текущий баланс")
def check_balance(message):
    bot.send_message(
        message.chat.id,
        f"💰 Текущий единый банкролл: **${bankroll:.2f}**",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
                    )
    
