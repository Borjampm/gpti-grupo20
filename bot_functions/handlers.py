from telegram import Update
from telegram.ext import ContextTypes
from .conversation_manager import set_user_state, IDLE, AWAITING_OPTION

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - welcome user and set state to IDLE"""
    chat_id = update.message.chat_id
    set_user_state(chat_id, IDLE)
    await update.message.reply_text("¡Hola! Bienvenido al bot. Escribe /help para comenzar.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - show menu and set state to AWAITING_OPTION"""
    chat_id = update.message.chat_id
    set_user_state(chat_id, AWAITING_OPTION)
    await update.message.reply_text(
        "¡Elige una opción escribiendo solo el número correspondiente:\n\n"
        "1. Imprimir el próximo mensaje\n"
        "2. Imprimir en MAYÚSCULAS el próximo mensaje\n"
        "3. Concatenar dos archivos PDF"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    await update.message.reply_text(
        "🤖 Soy un bot que puede procesar tus mensajes de diferentes maneras. "
        "Escribe /help para ver las opciones disponibles."
    )


