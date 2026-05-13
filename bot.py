import telebot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)
bot.delete_webhook(drop_pending_updates=True)

approved_users = [ADMIN_ID]

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id in approved_users:
        bot.reply_to(message, "✅ Approved আছো। /signal লিখে সিগন্যাল নাও")
    else:
        bot.reply_to(message, "তুমি Approved না।")

@bot.message_handler(commands=['signal'])
def signal(message):
    user_id = message.from_user.id
    if user_id not in approved_users:
        bot.reply_to(message, "তুমি Approved না।")
        return
    
    signal_text = "🚨 SIGNAL\n\nBUY BTC/USDT\nEntry: 67000\nTP: 67500\nSL: 66800"
    bot.send_message(user_id, signal_text)
    bot.reply_to(message, "✅ সিগন্যাল পাঠানো হইছে")

bot.infinity_polling()<b>━━━━━━━━━━━━</b>"""
@bot.message_handler(commands=['signal'])
def handle_signal(msg):
    try:
        if msg.from_user.id in approved_users:
            signal = get_signal()
            bot.reply_to(msg, signal, parse_mode="HTML")
        else:
            bot.reply_to(msg, "Access denied")
    except Exception as e:
        print("Signal error:", e)
        bot.reply_to(msg, "Signal error occurred", parse_mode=None)

print("Bot Running...")
bot.delete_webhook()
print("Webhook deleted, starting polling...")
bot.polling(none_stop=True)

