import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# --- SETUP ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Render pe TELEGRAM_BOT_TOKEN ya BOT_TOKEN dono chalega
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN:
    logging.error("BOT_TOKEN nahi mila!")
if not GEMINI_KEY:
    logging.error("GEMINI_API_KEY nahi mila!")

# Gemini Client - AQ wali key ke liye
client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Dimpy Bot is Live! Bot is working."

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# --- BOT FUNCTIONS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Main Dimpy ka assistant hu 😊\n\n"
        "/period - Period calculator\n"
        "Kuch bhi pucho, main AI se jawab dunga! Hindi/English dono me."
    )

async def period_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Apna last period ka date bhejo - jaise: 15 Aug\n"
        "Main agla date bata dungi ❤️"
    )

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome {member.first_name}! 🎉 Dimpy ke group me swagat hai!")

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text:
        return

    # Period word check
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    if any(m in user_text.lower() for m in months):
        if any(c.isdigit() for c in user_text):
            await update.message.reply_text("Samajh gaya! Agla period approx 28 din baad hoga. Dhyaan rakhna ❤️")
            return

    if not client:
        await update.message.reply_text("AI key set nahi hai, Admin se bolo check kare.")
        return

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"You are Dimpy, a friendly, caring helpful assistant for girls. Reply in same language as user. If user writes Hindi, reply in Hindi. If English, reply in English. Keep under 80 words. User: {user_text}"
        )
        await update.message.reply_text(response.text)
        
    except Exception as e:
        logging.error(f"GEMINI ERROR: {e}")
        await update.message.reply_text(f"Error: {e}")

# --- MAIN ---
def main():
    # Flask ko background me chalao
    Thread(target=run_flask, daemon=True).start()
    
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN missing. Render Environment me check karo.")
        return

    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("period", period_calc))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))
    
    print("Bot Starting... Polling mode")
    application.run_polling()

if __name__ == "__main__":
    main()
