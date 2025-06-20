from telegram import Update
from telegram.ext import ContextTypes
from ..state_manager import set_user_state, IDLE
from ..gemini_client import generate_text
import os

SYSTEM_PROMPT_FILE = "system_prompt.txt"

def get_system_prompt():
    """Reads the system prompt from the file."""
    try:
        with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

async def handle_gemini_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user's prompt for Gemini"""
    chat_id = update.message.chat_id
    user_prompt = update.message.text

    await update.message.reply_text("✨ Procesando tu solicitud con Gemini...", parse_mode='Markdown')

    system_prompt_template = get_system_prompt()
    if not system_prompt_template:
        await update.message.reply_text("No se pudo encontrar el archivo de prompt del sistema.")
        set_user_state(chat_id, IDLE)
        return

    # Construct the full prompt
    full_prompt = system_prompt_template.replace("<Petición libre del usuario>", user_prompt)

    # Generate text using Gemini
    response_text = await generate_text(full_prompt)

    # Send the response
    await update.message.reply_text(response_text)

    # Reset user state
    set_user_state(chat_id, IDLE)
    await update.message.reply_text("¿En qué más puedo ayudarte? Escribe /help para ver las opciones.")
