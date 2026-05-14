import telebot
import ccxt
import pandas as pd
import time
import threading
import os
from datetime import datetime, timedelta
import pytz

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
bot = telebot.TeleBot(BOT_TOKEN)
exchange = ccxt.kucoin()
approved_users = [ADMIN_ID]
last_signals = {}
user_start_time = {}

# OTC 10 পেয়ার লিস্ট
pairs = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/CAD OTC",
    "EUR/JPY OTC", "GBP/JPY OTC", "AUD/USD OTC", "USD/CAD OTC",
    "EUR/GBP OTC", "AUD/JPY OTC"
]

timeframe = "1m"
bd_tz = pytz.timezone('Asia/Dhaka')

def get_bangladesh_time():
    return datetime.now(bd_tz)

def check_strategies():
    for pair in pairs:
        try:
    ohlcv = exchange.fetch_ohlcv(pair, timeframe, limit=50)
            if len(ohlcv) < 20:
                continue

            df = pd.DataFrame(ohlcv, columns=['time','open','high','low','close','volume'])

            # RSI Calculation
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]

            if pd.isna(current_rsi):
                continue

            signal_key = f"{pair}_{timeframe}"

            if current_rsi < 30 and last_signals.get(signal_key) != "CALL":
                last_signals[signal_key] = "CALL"
                send_signal(pair, "CALL", round(current_rsi, 2))

            elif current_rsi > 70 and last_signals.get(signal_key) != "PUT":
                last_signals[signal_key] = "PUT"
                send_signal(pair, "PUT", round(current_rsi, 2))

        except Exception as e:
            print(f"Error with {pair}: {e}")
            continue

def send_signal(pair, action, rsi):
    now = get_bangladesh_time()
    bd_time = now.strftime("%H:%M:%S")

    # Entry Time 2 মিনিট পরে
    entry_time = (now + timedelta(minutes=2)).strftime("%H:%M")

    signal_text = f"""🔥 𝗤𝗨𝗢𝗧𝗘𝗫 𝗢𝗧𝗖 𝗦𝗜𝗚𝗡𝗔𝗟 🔥
━━━━━━━━━━━━━━
💎 𝗣𝗮𝗶𝗿: {pair}
📊 𝗔𝗰𝘁𝗶𝗼𝗻: {action}
⏰ 𝗧𝗶𝗺𝗲𝗳𝗿𝗮𝗺𝗲: 1 Minute
🕒 𝗘𝗻𝘁𝗿𝘆 𝗧𝗶𝗺𝗲: {entry_time}
🇧🇩 𝗕𝗗 𝗧𝗶𝗺𝗲: {bd_time}
📈 𝗥𝗲𝗮𝘀𝗼𝗻: RSI = {rsi}
━━━━━━━━━━━━━━
⚠️ 𝗗𝗘𝗠𝗢 𝗦𝗜𝗚𝗡𝗔𝗟 𝗢𝗡𝗟𝗬
💡 Practice Only - No Real Money"""

    for user_id in approved_users:
        if user_id in user_start_time and (time.time() - user_start_time[user_id]) >= 120:
            try:
                bot.send_message(user_id, signal_text)
            except Exception as e:
                print(f"Send error: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id not in approved_users:
        bot.reply_to(message, "❌ You are not approved")
        return

    bot.reply_to(message, "✅ Bot Active!\n🔥 OTC Auto Signal ON\n⏳ 2 মিনিট পর প্রথম সিগন্যাল পাবে")
    user_start_time[user_id] = time.time()

@bot.message_handler(commands=['status'])
def status(message):
    if message.from_user.id in approved_users:
        count = len([u for u in user_start_time if time.time() - user_start_time[u] >= 120])
        bot.reply_to(message, f"✅ Bot Running\n📊 Pairs: {len(pairs)}\n👥 Active: {count}")

print("Bot Running...")
print(f"Monitoring {len(pairs)} OTC Pairs")

def loop():
    while True:
        try:
            check_strategies()
            time.sleep(30)
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(30)

threading.Thread(target=loop, daemon=True).start()
bot.infinity_polling()
