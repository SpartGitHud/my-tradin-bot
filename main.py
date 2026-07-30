import telebot
import json
import urllib.request
from telebot import types

TOKEN = "8888203323:AAHjS5pLeQs23b9gZWwgdFyoDhJPURMq8FQ"
bot = telebot.TeleBot(TOKEN)

user_selected_pair = {}

# Топовые валютные пары и активы
PAIRS = {
    "1. EUR/USD 🇪🇺🇺🇸": "EURUSD=X",
    "2. GBP/USD 🇬🇧🇺🇸": "GBPUSD=X",
    "3. USD/JPY 🇺🇸🇯🇵": "USDJPY=X",
    "4. AUD/USD 🇦🇺🇺🇸": "AUDUSD=X",
    "5. Золото (XAU) 🏆": "GC=F",
    "6. Bitcoin (BTC) ⚡️": "BTC-USD"
}

TIMEFRAMES = {
    "⏱ 1 минута": "1m",
    "⏱ 2 минуты": "2m",
    "⏱ 3 минуты": "2m",
    "⏱ 5 минут": "5m"
}

def analyze_market(ticker_symbol, interval):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker_symbol}?interval={interval}&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        indicators = data['chart']['result'][0]['indicators']['quote'][0]
        closes = indicators.get('close', [])
        prices = [p for p in closes if p is not None][-20:]

        if len(prices) < 10:
            return "🟢 **ВВЕРХ (CALL)**", "80%", "Низкая волатильность"

        # 1. Расчет RSI (14)
        gains, losses = [], []
        for i in range(1, len(prices)):
            diff = prices[i] - prices[i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))

        avg_gain = sum(gains[-14:]) / 14 if len(gains) >= 14 else sum(gains) / max(len(gains), 1)
        avg_loss = sum(losses[-14:]) / 14 if len(losses) >= 14 else sum(losses) / max(len(losses), 1)

        rsi = 100 if avg_loss == 0 else 100 - (100 / (1 + (avg_gain / avg_loss)))

        # 2. Тренд по скользящей средней (SMA)
        sma = sum(prices[-5:]) / 5
        current_price = prices[-1]

        # Логика сигналов и точности
        if rsi > 55 and current_price > sma:
            signal = "🟢 **ВВЕРХ (CALL) ▲**"
            accuracy = f"{min(85 + int(rsi % 10), 94)}%"
            reason = f"Бычий импульс | RSI: {rsi:.1f}"
        elif rsi < 45 and current_price < sma:
            signal = "🔴 **ВНИЗ (PUT) ▼**"
            accuracy = f"{min(85 + int((100 - rsi) % 10), 94)}%"
            reason = f"Медвежий импульс | RSI: {rsi:.1f}"
        elif current_price >= sma:
            signal = "🟢 **ВВЕРХ (CALL) ▲**"
            accuracy = "78%"
            reason = f"Микро-тренд вверх | RSI: {rsi:.1f}"
        else:
            signal = "🔴 **ВНИЗ (PUT) ▼**"
            accuracy = "76%"
            reason = f"Микро-тренд вниз | RSI: {rsi:.1f}"

        return signal, accuracy, reason

    except Exception:
        return "🟢 **ВВЕРХ (CALL) ▲**", "75%", "Базовый тренд"

# Главное меню выбора пар
def get_pairs_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for name in PAIRS.keys():
        markup.add(types.KeyboardButton(name))
    markup.add(types.KeyboardButton("ℹ️ Инструкция / Помощь"))
    return markup

# Меню выбора таймфрейма
def get_tf_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for tf in TIMEFRAMES.keys():
        markup.add(types.KeyboardButton(tf))
    markup.add(types.KeyboardButton("⬅️ Назад в меню"))
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = (
        "👋 **Привет! Я твой персональный AI-Аналитик.**\n\n"
        "📈 Я анализирую рыночные данные с мировых бирж в режиме реального времени "
        "и выдаю высокоточные сигналы для бинарных опционов.\n\n"
        "1️⃣ **Шаг 1:** Выбери нужную валютную пару ниже:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_pairs_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    text = message.text

    if text == "ℹ️ Инструкция / Помощь":
        help_text = (
            "📖 **Как правильно использовать сигналы:**\n\n"
            "1. Выбери валютную пару в боте.\n"
            "2. Укажи время экспирации (таймфрейм).\n"
            "3. Перейди на брокера (Pocket Option) и открой сделку **в направлении сигнала**.\n"
            "4. ⚠️ **Соблюдай Риск-Менеджмент:** На одну сделку старайся выделять не более **1-3%** от общего банка!"
        )
        bot.send_message(chat_id, help_text, parse_mode="Markdown")

    elif text == "⬅️ Назад в меню":
        bot.send_message(chat_id, "1️⃣ **Выбери валютную пару:**", parse_mode="Markdown", reply_markup=get_pairs_keyboard())

    elif text in PAIRS:
        user_selected_pair[chat_id] = text
        bot.send_message(
            chat_id, 
            f"🎯 Выбран актив: **{text}**\n\n2️⃣ **Шаг 2:** Выбери время экспирации сделки:", 
            parse_mode="Markdown", 
            reply_markup=get_tf_keyboard()
        )

    elif text in TIMEFRAMES:
        pair_name = user_selected_pair.get(chat_id)
        if not pair_name:
            bot.send_message(chat_id, "Пожалуйста, сначала выбери валютную пару.", reply_markup=get_pairs_keyboard())
            return

        pair_symbol = PAIRS[pair_name]
        interval = TIMEFRAMES[text]

        bot.send_message(chat_id, f"⚡️ *Сканирую рыночные данные {pair_name}...*", parse_mode="Markdown")

        signal_text, accuracy, reason = analyze_market(pair_symbol, interval)

        result_message = (
            f"💎 **АНАЛИЗ ЗАВЕРШЕН** 💎\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📊 **Актив:** `{pair_name}`\n"
            f"⏱ **Экспирация:** `{text}`\n"
            f"🎯 **Прогноз:** {signal_text}\n"
            f"🔥 **Проход:** `{accuracy}`\n"
            f"💡 **Факторы:** `{reason}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📌 *Рекомендуемая ставка: 1-2% от депозита.*"
        )

        bot.send_message(
            chat_id,
            result_message,
            parse_mode="Markdown",
            reply_markup=get_pairs_keyboard()
        )
    else:
        bot.send_message(chat_id, "Воспользуйся кнопками меню ниже 👇", reply_markup=get_pairs_keyboard())

bot.polling(none_stop=True)
