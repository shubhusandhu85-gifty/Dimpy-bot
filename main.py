import os
import asyncio
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Dimpy Bot is Live!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Main finally live ho gaya!")

# Bot ko yaha banate hain
bot_app = ApplicationBuilder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
# --- apne baaki handlers yahi pe add kar dena ---

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # stop_signals=None is important for Render
    loop.run_until_complete(bot_app.run_polling(stop_signals=None))

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
