import telebot
from telebot import types
import threading
from strategy import get_signal
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

approved_users = set()
pending_users = set()
bot_running = False

MARKETS = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC"]

@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('/signal', '/start')
    
    if user_id in approved_users:
        bot.reply_to(msg, "✅ Approved আছো। /signal লিখে সিগনাল নাও", reply_markup=markup)
    elif user_id in pending_users:
        bot.reply_to(msg, "⏳ Approval Pending. Wait করো", reply_markup=markup)
    else:
        pending_users.add(user_id)
        bot.reply_to(msg, "📩 Request পাঠানো হয়েছে। Approval এর জন্য Wait করো", reply_markup=markup)
        bot.send_message(ADMIN_ID, f"New Request: {user_id}")

@bot.message_handler(commands=['approve'])
def approve(msg):
    if msg.from_user.id!= ADMIN_ID:
        return
    try:
        uid = int(msg.text.split()[1])
        approved_users.add(uid)
        pending_users.discard(uid)
        bot.send_message(uid, "✅ Approved! এখন /signal দিয়ে সিগনাল নাও")
        bot.reply_to(msg, f"Approved: {uid}")
    except:
        bot.reply_to(msg, "Format: /approve USERID")

@bot.message_handler(commands=['signal'])
def signal(msg):
    user_id = msg.from_user.id
    if user_id not in approved_users:
        bot.reply_to(msg, "❌ তুমি Approved না। /start দিয়ে রিকোয়েস্ট পাঠাও")
        return
    from datetime import datetime, timedelta
import pytz

def get_signal():
    # বাংলাদেশ টাইম + 2 মিনিট যোগ করো
    bd_tz = pytz.timezone('Asia/Dhaka')
    entry_time = datetime.now(bd_tz) + timedelta(minutes=2)
    
    signal = {
        "action": "SELL",
        "market": "GBPUSD-OTC", 
        "confidence": "81",
        "entry_time": entry_time.strftime('%H:%M')  # BST time
    }
    return signal
    signal_data = get_signal()

    
    action = signal_data['action']
    market = signal_data['market']
    confidence = signal_data['confidence']
    time = signal_data['time']
    entry_time = signal_data['entry_time']  # ✅ ঠিক
    # Action অনুযায়ী emoji আর color
    if action.upper() == "CALL":
        action_icon = "🟢"
        action_text = "BUY / CALL"
    else:
        action_icon = "🔴" 
        action_text = "SELL / PUT"
    
    # Confidence level অনুযায়ী emoji
    conf = int(confidence)
    if conf >= 85:
        conf_icon = "🔥"
        conf_level = "HIGH"
    elif conf >= 70:
        conf_icon = "⚡"
        conf_level = "MEDIUM"
    else:
        conf_icon = "⚠️"
        conf_level = "LOW"
    
    reply = f"""<b>━━━━━━━━━━━━</b>
🎯 <b>PRO SIGNAL ALERT</b> 🎯
<b>━━━━━━━━━━━━</b>

💱 <b>Pair:</b> <code>{market}</code>
{action_icon} <b>Signal:</b> <b>{action_text}</b>
📊 <b>Confidence:</b> {conf_icon} {confidence}% <i>({conf_level})</i>
⏰ <b>Entry Time:</b> <code>{entry_time}</code> BST
⏳ <b>Expiry:</b> <code>1 Minute</code>

<b>━━━━━━━━━━━━</b>
⚠️ <i>Money Management মেনে ট্রেড করো</i>
⚠️ <i>এটা Financial Advice না</i>
<b>━━━━━━━━━━━━</b>"""
    
    bot.reply_to(msg, reply, parse_mode="HTML")

print("Bot Running...")
bot.delete_webhook()
print("Webhook deleted, starting polling...")
bot.polling(none_stop=True)

