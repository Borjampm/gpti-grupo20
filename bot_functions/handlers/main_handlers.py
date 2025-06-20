from telegram import Update
from ..state_manager import (
    set_user_state, AWAITING_FIRST_PDF, AWAITING_MULTIPLE_PDFS,
    AWAITING_PDF_FOR_PAGE_DELETE, AWAITING_PDF_FOR_PAGE_EXTRACT,
    AWAITING_PDF_FOR_REORDER, AWAITING_JPEG, AWAITING_PNG,
    AWAITING_PDF_TO_PNG_FIRST, AWAITING_PDF_TO_PNG_ALL, AWAITING_SVG_TO_PNG,
    AWAITING_SVG_TO_JPEG, AWAITING_MULTIPLE_FILES_FOR_ZIP,
    AWAITING_ZIP_TO_EXTRACT, AWAITING_ZIP_TO_LIST, AWAITING_ZIP_FOR_ADD,
    AWAITING_ZIP_FOR_REMOVE, AWAITING_ZIP_FOR_BULK
)
from ..gemini_client import generate_text
import os
import re

SYSTEM_PROMPT_FILE = "prompts/system_prompt.txt"

def get_system_prompt():
    """Reads the system prompt from the file for intent classification."""
    try:
        with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

async def handle_option_selection(update: Update, user_message: str, chat_id: int):
    """Handle when user is selecting an option"""
    try:
        option = int(user_message)
    except ValueError:
        await update.message.reply_text("Por favor, envía solo el número de la opción deseada.")
        return

    await execute_action(update, chat_id, option)

async def execute_action(update: Update, chat_id: int, option: int):
    """Execute the specified action"""
    if option == 1:
        set_user_state(chat_id, AWAITING_FIRST_PDF, selected_option=1)
        await update.message.reply_text("📄 **Concatenar dos PDFs**\n\nEnvíame el primer archivo PDF.")
    elif option == 2:
        set_user_state(chat_id, AWAITING_MULTIPLE_PDFS, selected_option=2, pdf_paths=[])
        await update.message.reply_text(
            "📄 **Concatenar múltiples PDFs**\n\n"
            "Envíame los archivos PDF uno por uno. Cuando hayas enviado todos los archivos, escribe 'listo' para concatenarlos."
        )
    elif option == 3:
        set_user_state(chat_id, AWAITING_PDF_FOR_PAGE_DELETE, selected_option=3)
        await update.message.reply_text("📄 **Eliminar páginas de PDF**\n\nEnvíame el archivo PDF del cual quieres eliminar páginas.")
    elif option == 4:
        set_user_state(chat_id, AWAITING_PDF_FOR_PAGE_EXTRACT, selected_option=4)
        await update.message.reply_text("📄 **Extraer páginas de PDF**\n\nEnvíame el archivo PDF del cual quieres extraer páginas.")
    elif option == 5:
        set_user_state(chat_id, AWAITING_PDF_FOR_REORDER, selected_option=5)
        await update.message.reply_text("📄 **Reordenar páginas de PDF**\n\nEnvíame el archivo PDF cuyas páginas quieres reordenar.")
    elif option == 6:
        set_user_state(chat_id, AWAITING_JPEG, selected_option=6)
        await update.message.reply_text("🖼️ **JPEG → PNG**\n\nEnvíame el archivo JPEG que quieres convertir a PNG.")
    elif option == 7:
        set_user_state(chat_id, AWAITING_PNG, selected_option=7)
        await update.message.reply_text("🖼️ **PNG → JPEG**\n\nEnvíame el archivo PNG que quieres convertir a JPEG.")
    elif option == 8:
        set_user_state(chat_id, AWAITING_PDF_TO_PNG_FIRST, selected_option=8)
        await update.message.reply_text("🖼️ **PDF → PNG (primera página)**\n\nEnvíame el archivo PDF del cual quieres extraer la primera página como PNG.")
    elif option == 9:
        set_user_state(chat_id, AWAITING_PDF_TO_PNG_ALL, selected_option=9)
        await update.message.reply_text("🖼️ **PDF → PNG (todas las páginas)**\n\nEnvíame el archivo PDF del cual quieres extraer todas las páginas como PNG.")
    elif option == 10:
        set_user_state(chat_id, AWAITING_SVG_TO_PNG, selected_option=10)
        await update.message.reply_text("🖼️ **SVG → PNG**\n\nEnvíame el archivo SVG que quieres convertir a PNG.")
    elif option == 11:
        set_user_state(chat_id, AWAITING_SVG_TO_JPEG, selected_option=11)
        await update.message.reply_text("🖼️ **SVG → JPEG**\n\nEnvíame el archivo SVG que quieres convertir a JPEG.")
    elif option == 12:
        set_user_state(chat_id, AWAITING_MULTIPLE_FILES_FOR_ZIP, selected_option=12, file_paths=[])
        await update.message.reply_text(
            "🗜️ **Crear ZIP con varios archivos**\n\n"
            "Envíame los archivos uno por uno. Cuando hayas enviado todos los archivos, escribe 'listo' para crear el ZIP."
        )
    elif option == 13:
        set_user_state(chat_id, AWAITING_ZIP_TO_EXTRACT, selected_option=13)
        await update.message.reply_text("🗜️ **Extraer archivos de ZIP**\n\nEnvíame el archivo ZIP que quieres extraer.")
    elif option == 14:
        set_user_state(chat_id, AWAITING_ZIP_TO_LIST, selected_option=14)
        await update.message.reply_text("🗜️ **Listar contenidos de ZIP**\n\nEnvíame el archivo ZIP del cual quieres ver el contenido.")
    elif option == 15:
        set_user_state(chat_id, AWAITING_ZIP_FOR_ADD, selected_option=15)
        await update.message.reply_text("🗜️ **Agregar archivos a ZIP**\n\nPrimero envíame el archivo ZIP al cual quieres agregar archivos.")
    elif option == 16:
        set_user_state(chat_id, AWAITING_ZIP_FOR_REMOVE, selected_option=16)
        await update.message.reply_text("🗜️ **Eliminar archivos de ZIP**\n\nEnvíame el archivo ZIP del cual quieres eliminar archivos.")
    elif option == 17:
        set_user_state(chat_id, AWAITING_ZIP_FOR_BULK, selected_option=17)
        await update.message.reply_text("🗜️ **Operaciones en masa dentro de ZIP**\n\nEnvíame el archivo ZIP en el cual quieres realizar operaciones en masa.")
    else:
        await update.message.reply_text("Opción no válida. Por favor, elige un número del 1 al 17 o usa /manual para ver todas las opciones.")

async def handle_intent_classification(update: Update, chat_id: int):
    """Handle intent classification using LLM for IDLE state"""
    user_prompt = update.message.text

    # Get system prompt template
    system_prompt_template = get_system_prompt()
    if not system_prompt_template:
        await update.message.reply_text("No se pudo cargar el sistema de clasificación. Usa /manual para seleccionar una acción.")
        return

    # Construct the full prompt for intent classification
    full_prompt = system_prompt_template.replace("<Petición libre del usuario>", user_prompt)

    try:
        # Get LLM response for intent classification
        await update.message.reply_text("🤖 Analizando tu solicitud...")
        response_text = await generate_text(full_prompt)

        # Check if response contains "Acción: X" pattern
        action_match = re.search(r"Acción:\s*(\d+)", response_text)

        if action_match:
            action_number = int(action_match.group(1))
            if 1 <= action_number <= 17:
                # Execute the identified action
                await execute_action(update, chat_id, action_number)
                return
            else:
                await update.message.reply_text(f"Número de acción inválido: {action_number}. Usa /manual para ver las opciones disponibles.")
                return

        # If no clear action identified, continue conversation
        await update.message.reply_text(response_text)

    except Exception as e:
        print(f"Error in intent classification: {e}")
        await update.message.reply_text("Hubo un error procesando tu solicitud. Usa /manual para seleccionar una acción manualmente.")

async def handle_idle_state(update: Update, chat_id: int):
    """Handle when user is in idle state - now uses intent classification"""
    await handle_intent_classification(update, chat_id)
