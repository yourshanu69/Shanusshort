import time
import schedule
import asyncio
import os
from datetime import datetime, timedelta
import pytz
from telegram import Bot
import random

# ===== SETTINGS =====
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Railway এ Env Variable এ রাখবা
CHANNEL_ID = os.getenv("CHANNEL_ID")  # @channelusername বা -1001234567890
PAIRS = ["EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/CAD OTC", "USD/CAD OTC"]

bot = Bot(token=BOT_TOKEN)
tz = pytz.timezone('Asia/Dhaka')

# ===== SIGNAL LOGIC =====
def generate_signal():
    pair = random.choice(PAIRS)
    action = random.choice(["CALL", "PUT"])
    rsi = round(random.uniform(25, 75), 2)
    confidence = random.randint(75, 92)
    
    now = datetime.now(tz)
    entry_time = now + timedelta(minutes=2)
    
    entry_time_str = entry_time.strftime("%I:%M:%S %p")
    signal_time_str = now.strftime("%I:%M:%S %p")
    
    message = f"""
🔥 <b>QUOTEX OTC SIGNAL</b> 🔥
━━━━━━━━━━━
📊 <b>Pair:</b> {pair}
📈 <b>Signal:</b> {action}
⏱️
