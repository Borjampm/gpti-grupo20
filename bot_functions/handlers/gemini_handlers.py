from telegram import Update
from telegram.ext import ContextTypes
from ..state_manager import set_user_state, IDLE
from ..gemini_client import generate_text

async def handle_gemini_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user's prompt for Gemini"""
    chat_id = update.message.chat_id
    prompt = update.message.text

    await update.message.reply_text("✨ Procesando tu solicitud con Gemini...", parse_mode='Markdown')

    # Generate text using Gemini
    response_text = await generate_text(prompt)

    # Send the response
    await update.message.reply_text(response_text)

    # Reset user state
    set_user_state(chat_id, IDLE)
    await update.message.reply_text("¿En qué más puedo ayudarte? Escribe /help para ver las opciones.")
