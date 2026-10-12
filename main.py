import os
import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import google.generativeai as genai

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Dimpy AI Bot is Live 24/7!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey! I'm Dimpy's AI Bot. Ask me anything in English or Hindi!")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commands:\n/book\n/motivation\n/rules\n\nAap koi bhi sawal Hindi ya English me puch sakte ho!")

async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 Books change the way you see life. / Kitabe zindagi badal deti hai!")

async def motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Consistency is power! / Lagatar mehnat hi asli takat hai!")

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("1. No spam\n2. Growth talk only\n3. Respect everyone")

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        prompt = f"""
        You are Dimpy's family group AI assistant.
        RULE: Detect the user's language.
        - If user speaks Hindi/Hinglish, reply in Hindi (mix of Hindi + English is ok, friendly tone).
        - If user speaks English, reply in English.
        - Keep answer short, under 80 words, friendly.
        User says: {user_text}
        """
        response = await model.generate_content_async(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("Thoda busy hu, 10 sec baad try karo / Try again after 10 sec.")

bot_app = ApplicationBuilder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("help", help_cmd))
bot_app.add_handler(CommandHandler("book", book))
bot_app.add_handler(CommandHandler("motivation", motivation))
bot_app.add_handler(CommandHandler("rules", rules))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot_app.run_polling(stop_signals=None))

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
