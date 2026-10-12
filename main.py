import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_KEY:
    import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Dimpy Bot is Live!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Main Dimpy hu 😊\n/period likho period calculator ke liye\nKuch bhi pucho!")

async def period_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Apna last period ka date bhejo - jaise: 15 Aug")

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text
        if not user_text:
            return
        # Period simple logic
        if "21 sep" in user_text.lower() or "21" in user_text.lower() and "sep" in user_text.lower():
            await update.message.reply_text("21 Sep se agla period ~19 Oct ke aas paas aayega. Dhyaan rakho 😊")
            return
        
        if not GEMINI_KEY:
            await update.message.reply_text("Hi! Main Dimpy hu, batao kya help chahiye? 😊")
            return

        response = model.generate_content(f"You are Dimpy, a sweet friendly girl. Reply in same language as user, under 80 words. User: {user_text}")
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"AI Error: {e}")
        await update.message.reply_text(f"Hi! Main Dimpy hu 😊 Bolo kya baat hai?")

def main():
    Thread(target=run_flask, daemon=True).start()
    if not BOT_TOKEN:
        print("BOT_TOKEN missing!")
        return
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("period", period_calc))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))
    print("Bot Starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
