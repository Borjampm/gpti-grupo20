from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import os

from bot_functions.handlers import start, about, help
from bot_functions.conversation_manager import conversation_manager

load_dotenv()
app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

# Register command handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("about", about))

# Handle both text messages and document uploads
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_manager))
app.add_handler(MessageHandler(filters.ATTACHMENT, conversation_manager))

app.run_polling()
