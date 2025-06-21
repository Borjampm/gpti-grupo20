from telegram import Update
from ..state_manager import (
    set_user_state, AWAITING_FIRST_PDF, AWAITING_MULTIPLE_PDFS,
    AWAITING_PDF_FOR_PAGE_DELETE, AWAITING_PDF_FOR_PAGE_EXTRACT,
    AWAITING_PDF_FOR_REORDER, AWAITING_MULTIPLE_FILES_FOR_ZIP,
    AWAITING_ZIP_TO_EXTRACT, AWAITING_ZIP_TO_LIST, AWAITING_ZIP_FOR_ADD,
    AWAITING_ZIP_FOR_REMOVE, AWAITING_ZIP_FOR_IMAGES_TO_PNG, AWAITING_ZIP_FOR_IMAGES_TO_JPEG,
    AWAITING_ZIP_FOR_PDF_CONCATENATION, AWAITING_IMAGE_TO_PNG, AWAITING_IMAGE_TO_JPEG
)
from ..gemini_client import generate_text
from ..utils import get_exit_info_message
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
    """Handle user option selection (either direct number or natural language)"""
    if user_message.isdigit():
        option = int(user_message)
        await execute_action(update, chat_id, option)
    else:
        await handle_intent_classification(update, chat_id)

async def execute_action(update: Update, chat_id: int, option: int):
    """Execute the specified action"""
    exit_info = get_exit_info_message()

    if option == 1:
        set_user_state(chat_id, AWAITING_FIRST_PDF, selected_option=1)
        await update.message.reply_text(f"📄 **Concatenar dos PDFs**\n\nEnvíame el primer archivo PDF.\n\n{exit_info}")
    elif option == 2:
        set_user_state(chat_id, AWAITING_MULTIPLE_PDFS, selected_option=2, pdf_paths=[])
        await update.message.reply_text(
            f"📄 **Concatenar múltiples PDFs**\n\n"
            f"Envíame los archivos PDF uno por uno. Cuando hayas enviado todos los archivos, escribe 'listo' para concatenarlos.\n\n{exit_info}"
        )
    elif option == 3:
        set_user_state(chat_id, AWAITING_PDF_FOR_PAGE_DELETE, selected_option=3)
        await update.message.reply_text(f"📄 **Eliminar páginas de PDF**\n\nEnvíame el archivo PDF del cual quieres eliminar páginas.\n\n{exit_info}")
    elif option == 4:
        set_user_state(chat_id, AWAITING_PDF_FOR_PAGE_EXTRACT, selected_option=4)
        await update.message.reply_text(f"📄 **Extraer páginas de PDF**\n\nEnvíame el archivo PDF del cual quieres extraer páginas.\n\n{exit_info}")
    elif option == 5:
        set_user_state(chat_id, AWAITING_PDF_FOR_REORDER, selected_option=5)
        await update.message.reply_text(f"📄 **Reordenar páginas de PDF**\n\nEnvíame el archivo PDF cuyas páginas quieres reordenar.\n\n{exit_info}")
    elif option == 6:
        set_user_state(chat_id, AWAITING_MULTIPLE_FILES_FOR_ZIP, selected_option=6)
        await update.message.reply_text(f"🗜️ **Crear ZIP con varios archivos**\n\nEnvíame los archivos que quieres incluir en el ZIP uno por uno. Cuando hayas enviado todos los archivos, escribe 'listo' para crear el ZIP.\n\n{exit_info}")
    elif option == 7:
        set_user_state(chat_id, AWAITING_ZIP_TO_EXTRACT, selected_option=7)
        await update.message.reply_text(f"🗜️ **Extraer ZIP**\n\nEnvíame el archivo ZIP que quieres extraer.\n\n{exit_info}")
    elif option == 8:
        set_user_state(chat_id, AWAITING_ZIP_TO_LIST, selected_option=8)
        await update.message.reply_text(f"🗜️ **Listar contenidos de ZIP**\n\nEnvíame el archivo ZIP del cual quieres ver el contenido.\n\n{exit_info}")
    elif option == 9:
        set_user_state(chat_id, AWAITING_ZIP_FOR_ADD, selected_option=9)
        await update.message.reply_text(f"🗜️ **Agregar archivos a ZIP**\n\nPrimero envíame el archivo ZIP al cual quieres agregar archivos.\n\n{exit_info}")
    elif option == 10:
        set_user_state(chat_id, AWAITING_ZIP_FOR_REMOVE, selected_option=10)
        await update.message.reply_text(f"🗜️ **Eliminar archivos de ZIP**\n\nEnvíame el archivo ZIP del cual quieres eliminar archivos.\n\n{exit_info}")
    elif option == 11:
        set_user_state(chat_id, AWAITING_ZIP_FOR_IMAGES_TO_PNG, selected_option=11)
        await update.message.reply_text(f"🗜️ **Convertir todas las imágenes a PNG dentro de un ZIP**\n\nEnvíame el archivo ZIP que contiene las imágenes que quieres convertir a PNG (detectaré automáticamente JPEG y SVG).\n\n{exit_info}")
    elif option == 12:
        set_user_state(chat_id, AWAITING_ZIP_FOR_IMAGES_TO_JPEG, selected_option=12)
        await update.message.reply_text(f"🗜️ **Convertir todas las imágenes a JPEG dentro de un ZIP**\n\nEnvíame el archivo ZIP que contiene las imágenes que quieres convertir a JPEG (detectaré automáticamente PNG y SVG).\n\n{exit_info}")
    elif option == 13:
        set_user_state(chat_id, AWAITING_ZIP_FOR_PDF_CONCATENATION, selected_option=13)
        await update.message.reply_text(f"🗜️ **Concatenar todos los PDFs dentro de un ZIP**\n\nEnvíame el archivo ZIP que contiene los archivos PDF que quieres concatenar.\n\n{exit_info}")
    elif option == 14:
        set_user_state(chat_id, AWAITING_IMAGE_TO_PNG, selected_option=14)
        await update.message.reply_text(f"🖼️ **Imagen → PNG**\n\nEnvíame la imagen que quieres convertir a PNG (detectaré automáticamente el formato: JPEG, SVG, PDF).\n\n{exit_info}")
    elif option == 15:
        set_user_state(chat_id, AWAITING_IMAGE_TO_JPEG, selected_option=15)
        await update.message.reply_text(f"🖼️ **Imagen → JPEG**\n\nEnvíame la imagen que quieres convertir a JPEG (detectaré automáticamente el formato: PNG, SVG, PDF).\n\n{exit_info}")
    else:
        await update.message.reply_text("Opción no válida. Por favor, elige un número del 1 al 15 o usa /manual para ver todas las opciones.")

async def handle_intent_classification(update: Update, chat_id: int):
    """Use Gemini to classify user intent and execute corresponding action"""
    user_message = update.message.text
    system_prompt = get_system_prompt()

    # Prepare the prompt for Gemini
    prompt = f"{system_prompt}\n\n<USER>\n{user_message}\n\n<ASSISTANT>"

    try:
        response = await generate_text(prompt)

        # Extract action number from response
        action_match = re.search(r"Acción:\s*(\d+)", response)
        if action_match:
            action_number = int(action_match.group(1))
            if 1 <= action_number <= 15:
                # Execute the identified action
                await execute_action(update, chat_id, action_number)
            else:
                await update.message.reply_text("No pude identificar una acción válida. Usa /manual para ver todas las opciones disponibles.")
        else:
            # If no action number found, send the Gemini response as is
            await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Error al procesar tu solicitud. Intenta de nuevo o usa /manual para seleccionar directamente.")

async def handle_idle_state(update: Update, chat_id: int):
    """Handle messages when user is in idle state - use intent classification"""
    await handle_intent_classification(update, chat_id)
