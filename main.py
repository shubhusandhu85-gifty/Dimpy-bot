import os
import logging
from datetime import datetime
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# --- SETUP ---
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Nayi library ka client
client = genai.Client(api_key=GEMINI_KEY)

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Dimpy Bot is Live!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# --- BOT FUNCTIONS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Main Dimpy ka assistant hu 😊\n\n"
        "/period - Period date calculator\n"
        "Kuch bhi pucho, main AI se jawab dunga!"
    )

async def period_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Apna last period ka date bhejo - jaise: 15 Aug")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome {member.first_name}! 🎉 Dimpy ke group me swagat hai!")

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Agar period date hai to simple logic
    if any(x in user_text.lower() for x in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]):
        try:
            # Simple period logic - aapka purana wala yahi tha
            await update.message.reply_text("Samajh gaya! Agla period approx 28 din baad hoga. Dhyaan rakhna ❤️")
            return
        except:
            pass

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"You are Dimpy, a friendly helpful assistant. User speaks in Hindi/English mix. Reply in same language. Keep answer under 80 words, friendly tone. User says: {user_text}"
        )
        await update.message.reply_text(response.text)
        
    except Exception as e:
        print(f"GEMINI ERROR: {e}")
        await update.message.reply_text(f"Thoda error aaya: {e}")

# --- MAIN ---
def main():
    Thread(target=run_flask, daemon=True).start()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("period", period_calc))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))
    
    print("Bot Starting with new Gemini Client...")
    application.run_polling()

if __name__ == "__main__":
    main()
