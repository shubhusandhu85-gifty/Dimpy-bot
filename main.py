import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey, I'm Dimpy - your psychologist friend 🧠\nBatao kya feel kar rahe ho?")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "sad" in text or "udas" in text or "dukhi" in text:
        reply = "Samajh sakti hu, thoda udas feel kar rahe ho. Ek gehri saans lo, jo hua uske baare me thoda aur bataoge?"
    elif "stress" in text or "tension" in text:
        reply = "Tension lena normal hai. 5 minute aankhe band karke sirf saans pe dhyan do, fir mujhe batao kaisa lag raha hai."
    elif "khush" in text or "happy" in text:
        reply = "Wah, ye sunke accha laga! Is khushi ko aise hi banaye rakho ✨"
    else:
        reply = "Hmm, me sun rahi hu. Thoda aur detail me batao, tum akele nahi ho."
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()

from flask import Flask
import threading

app = Flask('')
@app.route('/')
def home():
    return "Dimpy Bot is Alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()
