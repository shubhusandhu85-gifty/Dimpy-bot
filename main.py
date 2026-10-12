import os
import logging
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# --- SETUP ---
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

# Flask ko alag thread me chalana
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Dimpy Bot is Live!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# --- BOT FUNCTIONS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Main Dimpy ka assistant hu 😊\n/period - Period calculator\nKuch bhi pucho!")

async def period_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Apna last period ka date bhejo - jaise: 15 Aug")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome {member.first_name}! 🎉")

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text or not client:
        return
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"You are Dimpy, friendly assistant. Reply in same language as user (Hindi/Eng). Keep under 80 words. User: {user_text}"
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"ERROR: {e}")
        await update.message.reply_text(f"Error aaya: {e}")

# --- MAIN FIX ---
def main():
    # Ye 2 line sabse important hai - isi se wo event loop error fix hoga
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    Thread(target=run_flask, daemon=True).start()
    
    if not BOT_TOKEN:
        print("BOT_TOKEN missing!")
        return

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("period", period_calc))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))
    
    print("Bot Starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
