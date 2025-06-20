from telegram import Update
from ..state_manager import (
    set_user_state, AWAITING_FIRST_PDF, AWAITING_MULTIPLE_PDFS,
    AWAITING_PDF_FOR_PAGE_DELETE, AWAITING_PDF_FOR_PAGE_EXTRACT,
    AWAITING_PDF_FOR_REORDER, AWAITING_JPEG, AWAITING_PNG,
    AWAITING_PDF_TO_PNG_FIRST, AWAITING_PDF_TO_PNG_ALL, AWAITING_SVG_TO_PNG,
    AWAITING_SVG_TO_JPEG, AWAITING_MULTIPLE_FILES_FOR_ZIP,
    AWAITING_ZIP_TO_EXTRACT, AWAITING_ZIP_TO_LIST, AWAITING_ZIP_FOR_ADD,
    AWAITING_ZIP_FOR_REMOVE, AWAITING_ZIP_FOR_BULK, AWAITING_GEMINI_PROMPT
)

async def handle_option_selection(update: Update, user_message: str, chat_id: int):
    """Handle when user is selecting an option"""
    try:
        option = int(user_message)
    except ValueError:
        await update.message.reply_text("Por favor, envía solo el número de la opción deseada.")
        return

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
    elif option == 18:
        set_user_state(chat_id, AWAITING_GEMINI_PROMPT, selected_option=18)
        await update.message.reply_text("✨ **Hablar con un LLM (Gemini)**\n\nEnvíame tu pregunta o prompt.")
    else:
        await update.message.reply_text("Opción no válida. Por favor, elige un número del 1 al 18.")

async def handle_idle_state(update: Update, chat_id: int):
    """Handle when user is in idle state"""
    await update.message.reply_text("Escribe /help para ver las opciones disponibles.")
