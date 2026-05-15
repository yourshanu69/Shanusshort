import os
import time
import pandas as pd
import ccxt
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = telebot.TeleBot(BOT_TOKEN)

exchange = ccxt.binance({
    'options': {'defaultType': 'future'},
    'enableRateLimit': True
})

pairs = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "DOGE/USDT"]
timeframe = "5m"
last_signals = {}

def send_signal(pair, signal_type, rsi):
    message = f"""
🚨 RSI Signal Alert 🚨
Pair: {pair}
Signal: {signal_type}
RSI: {rsi}
Timeframe: {timeframe}
"""
    try:
        bot.send_message(chat_id=ADMIN_ID, text=message)
        print(f"Signal sent: {pair} {signal_type}")
    except Exception as e:
        print(f"Telegram Error: {e}")

def check_strategies():
    for pair in pairs:
        try:
            ohlcv = exchange.fetch_ohlcv(pair, timeframe, limit=50)
            if len(ohlcv) < 20:
                continue

            df = pd.DataFrame(ohlcv, columns=['time','open','high','low','close','volume'])
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

print("Bot started...")
while True:
    check_strategies()
    time.sleep(60)
