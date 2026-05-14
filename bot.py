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
        bot.reply_to(message, "✅ Approved আছো। /signal লিখে সিগনাল নাও")
    else:
        bot.reply_to(message, "❌ Approved না")

@bot.message_handler(commands=['signal'])
def signal(message):
    user_id = message.from_user.id
    if user_id not in approved_users:
        bot.reply_to(message, "❌ Approved না")
        return

    signal_text = "🚨 SIGNAL\nBUY BTC/USDT\nEntry: 67000\nTP: 67500\nSL: 66800"
    bot.send_message(user_id, signal_text)
    bot.reply_to(message, "✅ সিগনাল পাঠানো হইছে")

print("Bot Running...")
bot.polling(none_stop=True)
