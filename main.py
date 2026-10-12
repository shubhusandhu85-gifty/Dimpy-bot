import os
import logging
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Dimpy Bot is Live!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Main Dimpy hu 😊")

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text or not client:
        return
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        prompt = "You are Dimpy, friendly assistant. Reply in same language. User: " + user_text
        
        models = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]
        reply = None
        last_err = ""
        for m in models:
            try:
                res = client.models.generate_content(model=m, contents=prompt)
                if res.text:
                    reply = res.text
                    break
            except Exception as e:
                last_err = str(e)
                continue
        
        if reply:
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text("Model error: " + last_err)
    except Exception as e:
        await update.message.reply_text("Error: " + str(e))

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    Thread(target=run_flask, daemon=True).start()
    if not BOT_TOKEN:
        print("BOT_TOKEN missing!")
        return
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))
    print("Bot Starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
