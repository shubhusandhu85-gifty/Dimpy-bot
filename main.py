import os
from flask import Flask
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- aapke handlers yahi rahenge ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey, I'm Dimpy!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "sad" in text or "udas" in text or "dukh" in text:
        reply = "Samajh sakti hu, thoda udas feel ho raha hai..."
    elif "stress" in text or "tension" in text:
        reply = "Tension lena normal hai. 5 min gehri saanse lo..."
    elif "khush" in text or "happy" in text:
        reply = "Wah, ye sunke accha laga! Is khushi ko..."
    else:
        reply = "Hmm, me sun rahi hu. Thoda aur batao?"
    await update.message.reply_text(reply)

# --- Flask wala part UPAR rakho ---
web_app = Flask('')
@web_app.route('/')
def home():
    return "Dimpy Bot is Alive!"

def run_flask():
    web_app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()

# --- Telegram bot sabse LAST me ---
bot_app = ApplicationBuilder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
bot_app.run_polling()
