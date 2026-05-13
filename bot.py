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
    
    signal_data = get_signal()
    bot.reply_to(msg, f"📊 Signal: {signal_data}")

print("Bot Running...")
bot.polling(none_stop=True)
