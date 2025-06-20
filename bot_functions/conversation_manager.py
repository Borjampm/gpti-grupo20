from telegram import Update
from telegram.ext import ContextTypes
import os
import tempfile
from PyPDF2 import PdfWriter, PdfReader
from PIL import Image
import cairosvg
from pdf2image import convert_from_path
import asyncio
import re
import zipfile
import shutil
import random
from .ad_messages import mensajes_promocionales

# Global instance to manage conversation states
conversation_state = {}

# State constants
IDLE = "IDLE"
AWAITING_OPTION = "AWAITING_OPTION"
AWAITING_FIRST_PDF = "AWAITING_FIRST_PDF"
AWAITING_SECOND_PDF = "AWAITING_SECOND_PDF"
AWAITING_MULTIPLE_PDFS = "AWAITING_MULTIPLE_PDFS"
AWAITING_PDF_FOR_PAGE_DELETE = "AWAITING_PDF_FOR_PAGE_DELETE"
AWAITING_PAGE_NUMBERS_DELETE = "AWAITING_PAGE_NUMBERS_DELETE"
AWAITING_PDF_FOR_PAGE_EXTRACT = "AWAITING_PDF_FOR_PAGE_EXTRACT"
AWAITING_PAGE_NUMBERS_EXTRACT = "AWAITING_PAGE_NUMBERS_EXTRACT"
AWAITING_PDF_FOR_REORDER = "AWAITING_PDF_FOR_REORDER"
AWAITING_PAGE_ORDER = "AWAITING_PAGE_ORDER"
AWAITING_JPEG = "AWAITING_JPEG"
AWAITING_PNG = "AWAITING_PNG"
AWAITING_PDF_TO_PNG_FIRST = "AWAITING_PDF_TO_PNG_FIRST"
AWAITING_PDF_TO_PNG_ALL = "AWAITING_PDF_TO_PNG_ALL"
AWAITING_SVG_TO_PNG = "AWAITING_SVG_TO_PNG"
AWAITING_SVG_TO_JPEG = "AWAITING_SVG_TO_JPEG"

# ZIP operation states
AWAITING_MULTIPLE_FILES_FOR_ZIP = "AWAITING_MULTIPLE_FILES_FOR_ZIP"
AWAITING_ZIP_TO_EXTRACT = "AWAITING_ZIP_TO_EXTRACT"
AWAITING_ZIP_TO_LIST = "AWAITING_ZIP_TO_LIST"
AWAITING_ZIP_FOR_ADD = "AWAITING_ZIP_FOR_ADD"
AWAITING_FILES_TO_ADD = "AWAITING_FILES_TO_ADD"
AWAITING_ZIP_FOR_REMOVE = "AWAITING_ZIP_FOR_REMOVE"
AWAITING_FILENAMES_TO_REMOVE = "AWAITING_FILENAMES_TO_REMOVE"
AWAITING_ZIP_FOR_BULK = "AWAITING_ZIP_FOR_BULK"
AWAITING_BULK_OPERATION = "AWAITING_BULK_OPERATION"
AWAITING_PDF_CONCATENATION_ORDER = "AWAITING_PDF_CONCATENATION_ORDER"

# File size limit (20 MB)
MAX_FILE_SIZE = 20 * 1024 * 1024

# Advertising messages are imported from ad_messages.py

def get_user_state(chat_id):
    """Get the current state of a user"""
    return conversation_state.get(chat_id, {}).get('state', IDLE)

def set_user_state(chat_id, state, **kwargs):
    """Set the state of a user and store additional data"""
    if chat_id not in conversation_state:
        conversation_state[chat_id] = {}
    conversation_state[chat_id]['state'] = state
    for key, value in kwargs.items():
        conversation_state[chat_id][key] = value

def get_user_data(chat_id, key, default=None):
    """Get specific data for a user"""
    return conversation_state.get(chat_id, {}).get(key, default)

def clear_user_data(chat_id):
    """Clear user data and temporary files"""
    if chat_id in conversation_state:
        # Clean up temporary files
        data = conversation_state[chat_id]
        for key, value in data.items():
            if key.endswith('_path') and value and os.path.exists(value):
                os.remove(value)
            elif key in ['pdf_paths', 'file_paths', 'files_to_add'] and isinstance(value, list):
                for path in value:
                    if path and os.path.exists(path):
                        os.remove(path)
        conversation_state[chat_id] = {}

async def validate_file(update: Update, file_types: list, max_size: int = MAX_FILE_SIZE):
    """Validate file type and size"""
    document = update.message.document
    if not document:
        return False, "Por favor, envía un archivo."

    # Check file size
    if document.file_size > max_size:
        size_mb = max_size / (1024 * 1024)
        return False, f"El archivo es demasiado grande. El tamaño máximo permitido es {size_mb:.0f} MB."

    # Check file type
    file_name = document.file_name
    if not file_name:
        return False, "No se pudo determinar el tipo de archivo."

    file_extension = file_name.lower().split('.')[-1]
    if file_extension not in file_types:
        return False, f"Tipo de archivo no válido. Formatos permitidos: {', '.join(file_types)}"

    return True, "Archivo válido"

async def conversation_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main conversation manager that handles user messages based on their state"""
    chat_id = update.message.chat_id
    current_state = get_user_state(chat_id)

    if current_state == AWAITING_OPTION:
        user_message = update.message.text
        await handle_option_selection(update, user_message, chat_id)
    elif current_state == AWAITING_FIRST_PDF:
        await handle_first_pdf_upload(update, chat_id)
    elif current_state == AWAITING_SECOND_PDF:
        await handle_second_pdf_upload(update, chat_id)
    elif current_state == AWAITING_MULTIPLE_PDFS:
        await handle_multiple_pdfs_upload(update, chat_id)
    elif current_state == AWAITING_PDF_FOR_PAGE_DELETE:
        await handle_pdf_for_page_operation(update, chat_id, "delete")
    elif current_state == AWAITING_PAGE_NUMBERS_DELETE:
        await handle_page_numbers_delete(update, chat_id)
    elif current_state == AWAITING_PDF_FOR_PAGE_EXTRACT:
        await handle_pdf_for_page_operation(update, chat_id, "extract")
    elif current_state == AWAITING_PAGE_NUMBERS_EXTRACT:
        await handle_page_numbers_extract(update, chat_id)
    elif current_state == AWAITING_PDF_FOR_REORDER:
        await handle_pdf_for_page_operation(update, chat_id, "reorder")
    elif current_state == AWAITING_PAGE_ORDER:
        await handle_page_order(update, chat_id)
    elif current_state == AWAITING_JPEG:
        await handle_jpeg_to_png(update, chat_id)
    elif current_state == AWAITING_PNG:
        await handle_png_to_jpeg(update, chat_id)
    elif current_state == AWAITING_PDF_TO_PNG_FIRST:
        await handle_pdf_to_png(update, chat_id, first_page_only=True)
    elif current_state == AWAITING_PDF_TO_PNG_ALL:
        await handle_pdf_to_png(update, chat_id, first_page_only=False)
    elif current_state == AWAITING_SVG_TO_PNG:
        await handle_svg_conversion(update, chat_id, "png")
    elif current_state == AWAITING_SVG_TO_JPEG:
        await handle_svg_conversion(update, chat_id, "jpeg")
    elif current_state == AWAITING_MULTIPLE_FILES_FOR_ZIP:
        await handle_multiple_files_for_zip(update, chat_id)
    elif current_state == AWAITING_ZIP_TO_EXTRACT:
        await handle_zip_extraction(update, chat_id)
    elif current_state == AWAITING_ZIP_TO_LIST:
        await handle_zip_listing(update, chat_id)
    elif current_state == AWAITING_ZIP_FOR_ADD:
        await handle_zip_for_add(update, chat_id)
    elif current_state == AWAITING_FILES_TO_ADD:
        await handle_files_to_add(update, chat_id)
    elif current_state == AWAITING_ZIP_FOR_REMOVE:
        await handle_zip_for_remove(update, chat_id)
    elif current_state == AWAITING_FILENAMES_TO_REMOVE:
        await handle_filenames_to_remove(update, chat_id)
    elif current_state == AWAITING_ZIP_FOR_BULK:
        await handle_zip_for_bulk(update, chat_id)
    elif current_state == AWAITING_BULK_OPERATION:
        await handle_bulk_operation(update, chat_id)
    elif current_state == AWAITING_PDF_CONCATENATION_ORDER:
        await handle_pdf_concatenation_order(update, chat_id)
    else:  # IDLE or unknown state
        await handle_idle_state(update, chat_id)

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
    else:
        await update.message.reply_text("Opción no válida. Por favor, elige un número del 1 al 17.")

async def handle_first_pdf_upload(update: Update, chat_id: int):
    """Handle the first PDF upload for two-PDF concatenation"""
    is_valid, message = await validate_file(update, ['pdf'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        first_pdf_path = os.path.join(temp_dir, f"first_pdf_{chat_id}_{file_name}")

        await file.download_to_drive(first_pdf_path)

        # Validate PDF
        try:
            reader = PdfReader(first_pdf_path)
            page_count = len(reader.pages)
        except Exception:
            os.remove(first_pdf_path)
            await update.message.reply_text("El archivo no es un PDF válido.")
            return

        set_user_state(chat_id, AWAITING_SECOND_PDF, first_pdf_path=first_pdf_path)
        await update.message.reply_text(
            f"✅ Primer PDF recibido: {file_name} ({page_count} páginas)\n"
            "Ahora envíame el segundo archivo PDF."
        )

    except Exception as e:
        await update.message.reply_text(f"Error al procesar el archivo: {str(e)}")

async def handle_second_pdf_upload(update: Update, chat_id: int):
    """Handle the second PDF upload and concatenation"""
    is_valid, message = await validate_file(update, ['pdf'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        second_pdf_path = os.path.join(temp_dir, f"second_pdf_{chat_id}_{file_name}")

        await file.download_to_drive(second_pdf_path)

        # Validate PDF
        try:
            reader = PdfReader(second_pdf_path)
            page_count = len(reader.pages)
        except Exception:
            os.remove(second_pdf_path)
            await update.message.reply_text("El archivo no es un PDF válido.")
            return

        await update.message.reply_text(f"✅ Segundo PDF recibido: {file_name} ({page_count} páginas)")

        # Send processing message and advertisement
        await send_processing_and_ad_message(update, "🔄 Concatenando dos archivos PDF...")

        # Concatenate PDFs
        first_pdf_path = get_user_data(chat_id, 'first_pdf_path')
        output_path = await concatenate_two_pdfs(first_pdf_path, second_pdf_path, chat_id)

        if output_path:
            with open(output_path, 'rb') as output_file:
                await update.message.reply_document(
                    document=output_file,
                    filename=f"concatenated_{chat_id}.pdf",
                    caption="✅ PDFs concatenados exitosamente!"
                )
            os.remove(output_path)
        else:
            await update.message.reply_text("❌ Error al concatenar los PDFs.")

        # Clean up
        os.remove(second_pdf_path)
        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except Exception as e:
        await update.message.reply_text(f"Error al procesar el archivo: {str(e)}")
        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_multiple_pdfs_upload(update: Update, chat_id: int):
    """Handle multiple PDF uploads for concatenation"""
    if update.message.text and update.message.text.lower() == 'listo':
        pdf_paths = get_user_data(chat_id, 'pdf_paths', [])
        if len(pdf_paths) < 2:
            await update.message.reply_text("Necesitas enviar al menos 2 archivos PDF antes de escribir 'listo'.")
            return

        # Send processing message and advertisement
        await send_processing_and_ad_message(update, f"🔄 Concatenando {len(pdf_paths)} archivos PDF en el orden especificado...")

        output_path = await concatenate_multiple_pdfs(pdf_paths, chat_id)
        if output_path:
            with open(output_path, 'rb') as output_file:
                await update.message.reply_document(
                    document=output_file,
                    filename=f"concatenated_multiple_{chat_id}.pdf",
                    caption=f"✅ {len(pdf_paths)} PDFs concatenados exitosamente!"
                )
            os.remove(output_path)
        else:
            await update.message.reply_text("❌ Error al concatenar los PDFs.")

        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")
        return

    is_valid, message = await validate_file(update, ['pdf'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        pdf_path = os.path.join(temp_dir, f"multi_pdf_{chat_id}_{len(get_user_data(chat_id, 'pdf_paths', []))}_{file_name}")

        await file.download_to_drive(pdf_path)

        # Validate PDF
        try:
            reader = PdfReader(pdf_path)
            page_count = len(reader.pages)
        except Exception:
            os.remove(pdf_path)
            await update.message.reply_text("El archivo no es un PDF válido.")
            return

        # Add to list
        pdf_paths = get_user_data(chat_id, 'pdf_paths', [])
        pdf_paths.append(pdf_path)
        set_user_state(chat_id, AWAITING_MULTIPLE_PDFS, pdf_paths=pdf_paths)

        await update.message.reply_text(
            f"✅ PDF {len(pdf_paths)} recibido: {file_name} ({page_count} páginas)\n"
            f"Total de archivos: {len(pdf_paths)}\n\n"
            "Envía otro PDF o escribe 'listo' para concatenar todos los archivos."
        )

    except Exception as e:
        await update.message.reply_text(f"Error al procesar el archivo: {str(e)}")

async def handle_pdf_for_page_operation(update: Update, chat_id: int, operation: str):
    """Handle PDF upload for page operations (delete, extract, reorder)"""
    is_valid, message = await validate_file(update, ['pdf'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        pdf_path = os.path.join(temp_dir, f"{operation}_pdf_{chat_id}_{file_name}")

        await file.download_to_drive(pdf_path)

        # Validate PDF and get page count
        try:
            reader = PdfReader(pdf_path)
            page_count = len(reader.pages)
        except Exception:
            os.remove(pdf_path)
            await update.message.reply_text("El archivo no es un PDF válido.")
            return

        set_user_state(chat_id, f"AWAITING_PAGE_NUMBERS_{operation.upper()}", pdf_path=pdf_path, page_count=page_count)

        if operation == "delete":
            await update.message.reply_text(
                f"✅ PDF recibido: {file_name} ({page_count} páginas)\n\n"
                f"Especifica qué páginas quieres eliminar. Puedes usar:\n"
                f"• Números individuales: 1,3,5\n"
                f"• Rangos: 1-3,5-7\n"
                f"• Combinaciones: 1,3-5,8\n\n"
                f"Páginas disponibles: 1-{page_count}"
            )
        elif operation == "extract":
            await update.message.reply_text(
                f"✅ PDF recibido: {file_name} ({page_count} páginas)\n\n"
                f"Especifica qué páginas quieres extraer. Puedes usar:\n"
                f"• Números individuales: 1,3,5\n"
                f"• Rangos: 1-3,5-7\n"
                f"• Combinaciones: 1,3-5,8\n\n"
                f"Páginas disponibles: 1-{page_count}"
            )
        elif operation == "reorder":
            set_user_state(chat_id, AWAITING_PAGE_ORDER, pdf_path=pdf_path, page_count=page_count)
            await update.message.reply_text(
                f"✅ PDF recibido: {file_name} ({page_count} páginas)\n\n"
                f"Especifica el nuevo orden de las páginas separadas por comas.\n"
                f"Por ejemplo: 3,1,2,4 (para poner la página 3 primero, luego 1, luego 2, luego 4)\n\n"
                f"Páginas disponibles: 1-{page_count}\n"
                f"Debes incluir todas las páginas en el nuevo orden."
            )

    except Exception as e:
        await update.message.reply_text(f"Error al procesar el archivo: {str(e)}")

def parse_page_numbers(page_string: str, max_pages: int):
    """Parse page numbers from string like '1,3-5,8' into a list of page numbers"""
    pages = set()
    parts = page_string.replace(' ', '').split(',')

    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            if start < 1 or end > max_pages or start > end:
                raise ValueError(f"Rango inválido: {part}")
            pages.update(range(start, end + 1))
        else:
            page = int(part)
            if page < 1 or page > max_pages:
                raise ValueError(f"Página inválida: {page}")
            pages.add(page)

    return sorted(list(pages))

async def handle_page_numbers_delete(update: Update, chat_id: int):
    """Handle page number specification for deletion"""
    if not update.message.text:
        await update.message.reply_text("Por favor, especifica los números de página.")
        return

    try:
        page_count = get_user_data(chat_id, 'page_count')
        pages_to_delete = parse_page_numbers(update.message.text, page_count)

        # Send processing message and advertisement
        await send_processing_and_ad_message(update, f"🔄 Eliminando páginas {', '.join(map(str, pages_to_delete))}...")

        pdf_path = get_user_data(chat_id, 'pdf_path')
        output_path = await delete_pdf_pages(pdf_path, pages_to_delete, chat_id)

        if output_path:
            with open(output_path, 'rb') as output_file:
                await update.message.reply_document(
                    document=output_file,
                    filename=f"pages_deleted_{chat_id}.pdf",
                    caption=f"✅ Páginas eliminadas: {', '.join(map(str, pages_to_delete))}"
                )
            os.remove(output_path)
        else:
            await update.message.reply_text("❌ Error al eliminar las páginas.")

        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except ValueError as e:
        await update.message.reply_text(f"Error en el formato de páginas: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"Error al procesar: {str(e)}")
        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_page_numbers_extract(update: Update, chat_id: int):
    """Handle page number specification for extraction"""
    if not update.message.text:
        await update.message.reply_text("Por favor, especifica los números de página.")
        return

    try:
        page_count = get_user_data(chat_id, 'page_count')
        pages_to_extract = parse_page_numbers(update.message.text, page_count)

        # Send processing message and advertisement
        await send_processing_and_ad_message(update, f"🔄 Extrayendo páginas {', '.join(map(str, pages_to_extract))}...")

        pdf_path = get_user_data(chat_id, 'pdf_path')
        output_path = await extract_pdf_pages(pdf_path, pages_to_extract, chat_id)

        if output_path:
            with open(output_path, 'rb') as output_file:
                await update.message.reply_document(
                    document=output_file,
                    filename=f"pages_extracted_{chat_id}.pdf",
                    caption=f"✅ Páginas extraídas: {', '.join(map(str, pages_to_extract))}"
                )
            os.remove(output_path)
        else:
            await update.message.reply_text("❌ Error al extraer las páginas.")

        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except ValueError as e:
        await update.message.reply_text(f"Error en el formato de páginas: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"Error al procesar: {str(e)}")
        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_page_order(update: Update, chat_id: int):
    """Handle page order specification for reordering"""
    if not update.message.text:
        await update.message.reply_text("Por favor, especifica el orden de las páginas.")
        return

    try:
        page_count = get_user_data(chat_id, 'page_count')
        order_parts = [int(x.strip()) for x in update.message.text.split(',')]

        # Validate that all pages are included exactly once
        if sorted(order_parts) != list(range(1, page_count + 1)):
            await update.message.reply_text(
                f"Debes incluir todas las páginas (1-{page_count}) exactamente una vez en el nuevo orden."
            )
            return

        # Send processing message and advertisement
        await send_processing_and_ad_message(update, f"🔄 Reordenando páginas según: {', '.join(map(str, order_parts))}...")

        pdf_path = get_user_data(chat_id, 'pdf_path')
        output_path = await reorder_pdf_pages(pdf_path, order_parts, chat_id)

        if output_path:
            with open(output_path, 'rb') as output_file:
                await update.message.reply_document(
                    document=output_file,
                    filename=f"pages_reordered_{chat_id}.pdf",
                    caption=f"✅ Páginas reordenadas: {', '.join(map(str, order_parts))}"
                )
            os.remove(output_path)
        else:
            await update.message.reply_text("❌ Error al reordenar las páginas.")

        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except ValueError:
        await update.message.reply_text("Por favor, usa solo números separados por comas (ej: 3,1,2,4).")
    except Exception as e:
        await update.message.reply_text(f"Error al procesar: {str(e)}")
        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_jpeg_to_png(update: Update, chat_id: int):
    """Handle JPEG to PNG conversion"""
    is_valid, message = await validate_file(update, ['jpg', 'jpeg'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        input_path = os.path.join(temp_dir, f"jpeg_input_{chat_id}_{file_name}")
        output_path = os.path.join(temp_dir, f"png_output_{chat_id}.png")

        await file.download_to_drive(input_path)

        # Send processing message and advertisement
        await send_processing_and_ad_message(update, "🔄 Convirtiendo JPEG a PNG...")

        # Convert JPEG to PNG
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (for JPEG with transparency issues)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            img.save(output_path, 'PNG')

        # Send converted file
        with open(output_path, 'rb') as output_file:
            await update.message.reply_document(
                document=output_file,
                filename=f"converted_{file_name.rsplit('.', 1)[0]}.png",
                caption="✅ JPEG convertido a PNG exitosamente!"
            )

        # Clean up
        os.remove(input_path)
        os.remove(output_path)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except Exception as e:
        await update.message.reply_text(f"Error al convertir la imagen: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_png_to_jpeg(update: Update, chat_id: int):
    """Handle PNG to JPEG conversion"""
    is_valid, message = await validate_file(update, ['png'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        input_path = os.path.join(temp_dir, f"png_input_{chat_id}_{file_name}")
        output_path = os.path.join(temp_dir, f"jpeg_output_{chat_id}.jpg")

        await file.download_to_drive(input_path)

        # Send processing message and advertisement
        await send_processing_and_ad_message(update, "🔄 Convirtiendo PNG a JPEG...")

        # Convert PNG to JPEG
        with Image.open(input_path) as img:
            # Convert RGBA to RGB (PNG with transparency to JPEG)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode == 'P':
                img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=95)

        # Send converted file
        with open(output_path, 'rb') as output_file:
            await update.message.reply_document(
                document=output_file,
                filename=f"converted_{file_name.rsplit('.', 1)[0]}.jpg",
                caption="✅ PNG convertido a JPEG exitosamente!"
            )

        # Clean up
        os.remove(input_path)
        os.remove(output_path)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except Exception as e:
        await update.message.reply_text(f"Error al convertir la imagen: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_pdf_to_png(update: Update, chat_id: int, first_page_only: bool):
    """Handle PDF to PNG conversion"""
    is_valid, message = await validate_file(update, ['pdf'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        input_path = os.path.join(temp_dir, f"pdf_input_{chat_id}_{file_name}")

        await file.download_to_drive(input_path)

        # Send processing message and advertisement
        if first_page_only:
            await send_processing_and_ad_message(update, "🔄 Convirtiendo primera página de PDF a PNG...")
        else:
            await send_processing_and_ad_message(update, "🔄 Convirtiendo todas las páginas de PDF a PNG...")

        # Convert PDF to images
        if first_page_only:
            images = convert_from_path(input_path, first_page=1, last_page=1, dpi=200)
            if images:
                output_path = os.path.join(temp_dir, f"pdf_to_png_{chat_id}.png")
                images[0].save(output_path, 'PNG')

                with open(output_path, 'rb') as output_file:
                    await update.message.reply_document(
                        document=output_file,
                        filename=f"page_1_{file_name.rsplit('.', 1)[0]}.png",
                        caption="✅ Primera página convertida a PNG!"
                    )
                os.remove(output_path)
        else:
            images = convert_from_path(input_path, dpi=200)
            await update.message.reply_text(f"📄 Procesando {len(images)} páginas...")

            for i, image in enumerate(images, 1):
                output_path = os.path.join(temp_dir, f"pdf_to_png_{chat_id}_page_{i}.png")
                image.save(output_path, 'PNG')

                with open(output_path, 'rb') as output_file:
                    await update.message.reply_document(
                        document=output_file,
                        filename=f"page_{i}_{file_name.rsplit('.', 1)[0]}.png",
                        caption=f"✅ Página {i} de {len(images)}"
                    )
                os.remove(output_path)

        # Clean up
        os.remove(input_path)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except Exception as e:
        await update.message.reply_text(f"Error al convertir PDF: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_svg_conversion(update: Update, chat_id: int, output_format: str):
    """Handle SVG to PNG/JPEG conversion"""
    is_valid, message = await validate_file(update, ['svg'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        input_path = os.path.join(temp_dir, f"svg_input_{chat_id}_{file_name}")

        await file.download_to_drive(input_path)

        # Send processing message and advertisement
        await send_processing_and_ad_message(update, f"🔄 Convirtiendo SVG a {output_format.upper()}...")

        if output_format == "png":
            output_path = os.path.join(temp_dir, f"svg_to_png_{chat_id}.png")
            cairosvg.svg2png(url=input_path, write_to=output_path, dpi=300)
            output_filename = f"converted_{file_name.rsplit('.', 1)[0]}.png"
        else:  # jpeg
            # Convert SVG to PNG first, then to JPEG
            png_path = os.path.join(temp_dir, f"svg_to_png_temp_{chat_id}.png")
            output_path = os.path.join(temp_dir, f"svg_to_jpeg_{chat_id}.jpg")

            cairosvg.svg2png(url=input_path, write_to=png_path, dpi=300)

            # Convert PNG to JPEG
            with Image.open(png_path) as img:
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                img.save(output_path, 'JPEG', quality=95)

            os.remove(png_path)
            output_filename = f"converted_{file_name.rsplit('.', 1)[0]}.jpg"

        # Send converted file
        with open(output_path, 'rb') as output_file:
            await update.message.reply_document(
                document=output_file,
                filename=output_filename,
                caption=f"✅ SVG convertido a {output_format.upper()} exitosamente!"
            )

        # Clean up
        os.remove(input_path)
        os.remove(output_path)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except Exception as e:
        await update.message.reply_text(f"Error al convertir SVG: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

# PDF processing functions
async def concatenate_two_pdfs(first_pdf_path: str, second_pdf_path: str, chat_id: int) -> str:
    """Concatenate two PDF files"""
    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"concatenated_{chat_id}.pdf")

        pdf_writer = PdfWriter()

        # Check if both files exist
        if not os.path.exists(first_pdf_path):
            print(f"First PDF file not found: {first_pdf_path}")
            return None
        if not os.path.exists(second_pdf_path):
            print(f"Second PDF file not found: {second_pdf_path}")
            return None

        # Add pages from first PDF
        try:
            with open(first_pdf_path, 'rb') as first_file:
                first_reader = PdfReader(first_file)
                for page in first_reader.pages:
                    pdf_writer.add_page(page)
        except Exception as e:
            print(f"Error reading first PDF: {e}")
            return None

        # Add pages from second PDF
        try:
            with open(second_pdf_path, 'rb') as second_file:
                second_reader = PdfReader(second_file)
                for page in second_reader.pages:
                    pdf_writer.add_page(page)
        except Exception as e:
            print(f"Error reading second PDF: {e}")
            return None

        # Write output
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        return output_path
    except Exception as e:
        print(f"Error concatenating PDFs: {e}")
        return None

async def concatenate_multiple_pdfs(pdf_paths: list, chat_id: int) -> str:
    """Concatenate multiple PDF files"""
    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"concatenated_multiple_{chat_id}.pdf")

        pdf_writer = PdfWriter()

        for pdf_path in pdf_paths:
            # Check if file exists and is accessible
            if not os.path.exists(pdf_path):
                print(f"PDF file not found: {pdf_path}")
                continue

            try:
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_reader = PdfReader(pdf_file)
                    # Add all pages from this PDF
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)
                print(f"Successfully processed: {pdf_path}")
            except Exception as e:
                print(f"Error reading PDF {pdf_path}: {e}")
                continue

        # Check if we have any pages to write
        if len(pdf_writer.pages) == 0:
            print("No valid pages found to concatenate")
            return None

        # Write output
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        return output_path
    except Exception as e:
        print(f"Error concatenating multiple PDFs: {e}")
        return None

async def delete_pdf_pages(pdf_path: str, pages_to_delete: list, chat_id: int) -> str:
    """Delete specific pages from PDF"""
    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"pages_deleted_{chat_id}.pdf")

        pdf_writer = PdfWriter()

        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)

            for page_num in range(1, total_pages + 1):
                if page_num not in pages_to_delete:
                    pdf_writer.add_page(pdf_reader.pages[page_num - 1])

        # Write output
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        return output_path
    except Exception as e:
        print(f"Error deleting PDF pages: {e}")
        return None

async def extract_pdf_pages(pdf_path: str, pages_to_extract: list, chat_id: int) -> str:
    """Extract specific pages from PDF"""
    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"pages_extracted_{chat_id}.pdf")

        pdf_writer = PdfWriter()

        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)

            for page_num in pages_to_extract:
                pdf_writer.add_page(pdf_reader.pages[page_num - 1])

        # Write output
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        return output_path
    except Exception as e:
        print(f"Error extracting PDF pages: {e}")
        return None

async def reorder_pdf_pages(pdf_path: str, page_order: list, chat_id: int) -> str:
    """Reorder pages in PDF according to specified order"""
    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"pages_reordered_{chat_id}.pdf")

        pdf_writer = PdfWriter()

        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)

            for page_num in page_order:
                pdf_writer.add_page(pdf_reader.pages[page_num - 1])

        # Write output
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        return output_path
    except Exception as e:
        print(f"Error reordering PDF pages: {e}")
        return None

# ZIP operation handlers
async def handle_multiple_files_for_zip(update: Update, chat_id: int):
    """Handle multiple file uploads for ZIP creation"""
    if update.message.text and update.message.text.lower() == "listo":
        file_paths = get_user_data(chat_id, 'file_paths', [])
        if len(file_paths) < 2:
            await update.message.reply_text("Necesitas enviar al menos 2 archivos para crear un ZIP.")
            return

        # Send processing message and advertisement
        await send_processing_and_ad_message(update, f"🔄 Creando ZIP con {len(file_paths)} archivos...")

        try:
            zip_path = await create_zip_from_files(file_paths, chat_id)
            if zip_path:
                with open(zip_path, 'rb') as zip_file:
                    await update.message.reply_document(
                        document=zip_file,
                        filename=f"archivos_combinados_{chat_id}.zip",
                        caption="✅ ZIP creado exitosamente!"
                    )
                os.remove(zip_path)
            else:
                await update.message.reply_text("❌ Error al crear el ZIP.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error al crear el ZIP: {str(e)}")

        # Clean up temporary files
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)

        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")
        return

    # Handle file upload
    if not update.message.document:
        await update.message.reply_text("Por favor, envía un archivo o escribe 'listo' cuando hayas terminado.")
        return

    is_valid, message = await validate_file(update, ['pdf', 'png', 'jpg', 'jpeg', 'svg', 'txt', 'docx', 'xlsx'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        file_path = os.path.join(temp_dir, f"zip_file_{chat_id}_{len(get_user_data(chat_id, 'file_paths', []))}_{file_name}")

        await file.download_to_drive(file_path)

        # Add to file paths list
        file_paths = get_user_data(chat_id, 'file_paths', [])
        file_paths.append(file_path)
        set_user_state(chat_id, AWAITING_MULTIPLE_FILES_FOR_ZIP, file_paths=file_paths)

        await update.message.reply_text(f"✅ Archivo {len(file_paths)} recibido: {file_name}\n\nEnvía más archivos o escribe 'listo' para crear el ZIP.")

    except Exception as e:
        await update.message.reply_text(f"Error al recibir el archivo: {str(e)}")

async def handle_zip_extraction(update: Update, chat_id: int):
    """Handle ZIP file extraction"""
    is_valid, message = await validate_file(update, ['zip'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        zip_path = os.path.join(temp_dir, f"zip_to_extract_{chat_id}_{file_name}")

        await file.download_to_drive(zip_path)

        # Send processing message and advertisement
        await send_processing_and_ad_message(update, "🔄 Extrayendo archivos del ZIP...")

        # Create extraction directory
        extract_dir = os.path.join(temp_dir, f"extracted_{chat_id}")
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            extracted_files = zip_ref.namelist()

        # Send each extracted file (only valid files)
        files_sent = 0
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                # Skip macOS metadata files
                if file.startswith('._') or '__MACOSX' in root:
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as extracted_file:
                        await update.message.reply_document(
                            document=extracted_file,
                            filename=file,
                            caption=f"📄 Archivo extraído: {file}"
                        )
                    files_sent += 1
                except Exception as e:
                    await update.message.reply_text(f"❌ No se pudo enviar {file}: {str(e)}")

        await update.message.reply_text(f"✅ Extracción completada. {files_sent} archivos enviados.")

        # Clean up
        os.remove(zip_path)
        shutil.rmtree(extract_dir)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error al extraer el ZIP: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_zip_listing(update: Update, chat_id: int):
    """Handle ZIP file content listing"""
    is_valid, message = await validate_file(update, ['zip'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        zip_path = os.path.join(temp_dir, f"zip_to_list_{chat_id}_{file_name}")

        await file.download_to_drive(zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            all_files = zip_ref.namelist()
            valid_files = filter_valid_files(all_files)
            info_list = []

            for file_name in valid_files:
                info = zip_ref.getinfo(file_name)
                size_mb = info.file_size / (1024 * 1024)
                info_list.append(f"📄 {file_name} ({size_mb:.2f} MB)")

        if info_list:
            content_text = "📋 **Contenido del ZIP:**\n\n" + "\n".join(info_list)
            content_text += f"\n\n📊 **Total: {len(valid_files)} archivos**"
        else:
            content_text = "📋 El archivo ZIP no contiene archivos válidos."

        await update.message.reply_text(content_text)

        # Clean up
        os.remove(zip_path)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error al listar el contenido del ZIP: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_zip_for_add(update: Update, chat_id: int):
    """Handle ZIP file for adding files"""
    is_valid, message = await validate_file(update, ['zip'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        zip_path = os.path.join(temp_dir, f"zip_for_add_{chat_id}_{file_name}")

        await file.download_to_drive(zip_path)

        # Validate ZIP file and filter valid files
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            all_files = zip_ref.namelist()
            current_files = filter_valid_files(all_files)

        set_user_state(chat_id, AWAITING_FILES_TO_ADD, zip_path=zip_path, files_to_add=[])
        await update.message.reply_text(
            f"✅ ZIP recibido con {len(current_files)} archivos.\n\n"
            "Ahora envíame los archivos que quieres agregar uno por uno. "
            "Cuando hayas terminado, escribe 'listo'."
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error al procesar el ZIP: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_files_to_add(update: Update, chat_id: int):
    """Handle files to add to existing ZIP"""
    if update.message.text and update.message.text.lower() == "listo":
        files_to_add = get_user_data(chat_id, 'files_to_add', [])
        if not files_to_add:
            await update.message.reply_text("No has enviado ningún archivo para agregar.")
            return

        zip_path = get_user_data(chat_id, 'zip_path')

        # Send processing message and advertisement
        await send_processing_and_ad_message(update, f"🔄 Agregando {len(files_to_add)} archivos al ZIP...")

        try:
            new_zip_path = await add_files_to_zip(zip_path, files_to_add, chat_id)
            if new_zip_path:
                with open(new_zip_path, 'rb') as new_zip_file:
                    await update.message.reply_document(
                        document=new_zip_file,
                        filename=f"zip_actualizado_{chat_id}.zip",
                        caption=f"✅ ZIP actualizado con {len(files_to_add)} archivos nuevos!"
                    )
                os.remove(new_zip_path)
            else:
                await update.message.reply_text("❌ Error al agregar archivos al ZIP.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error al agregar archivos: {str(e)}")

        # Clean up
        if os.path.exists(zip_path):
            os.remove(zip_path)
        for file_path in files_to_add:
            if os.path.exists(file_path):
                os.remove(file_path)

        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")
        return

    # Handle file upload
    if not update.message.document:
        await update.message.reply_text("Por favor, envía un archivo o escribe 'listo' cuando hayas terminado.")
        return

    is_valid, message = await validate_file(update, ['pdf', 'png', 'jpg', 'jpeg', 'svg', 'txt', 'docx', 'xlsx', 'zip'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        file_path = os.path.join(temp_dir, f"add_file_{chat_id}_{len(get_user_data(chat_id, 'files_to_add', []))}_{file_name}")

        await file.download_to_drive(file_path)

        # Add to files list
        files_to_add = get_user_data(chat_id, 'files_to_add', [])
        files_to_add.append(file_path)
        set_user_state(chat_id, AWAITING_FILES_TO_ADD, files_to_add=files_to_add)

        await update.message.reply_text(f"✅ Archivo recibido: {file_name}\n\nEnvía más archivos o escribe 'listo' para agregarlos al ZIP.")

    except Exception as e:
        await update.message.reply_text(f"Error al recibir el archivo: {str(e)}")

async def handle_zip_for_remove(update: Update, chat_id: int):
    """Handle ZIP file for removing files"""
    is_valid, message = await validate_file(update, ['zip'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        zip_path = os.path.join(temp_dir, f"zip_for_remove_{chat_id}_{file_name}")

        await file.download_to_drive(zip_path)

        # List current files and filter valid ones
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            all_files = zip_ref.namelist()
            current_files = filter_valid_files(all_files)

        if not current_files:
            await update.message.reply_text("❌ El ZIP está vacío.")
            os.remove(zip_path)
            set_user_state(chat_id, AWAITING_OPTION)
            return

        files_list = "\n".join([f"{i+1}. {file}" for i, file in enumerate(current_files)])

        set_user_state(chat_id, AWAITING_FILENAMES_TO_REMOVE, zip_path=zip_path, current_files=current_files)
        await update.message.reply_text(
            f"📋 **Archivos en el ZIP:**\n\n{files_list}\n\n"
            "Envía los números de los archivos que quieres eliminar, separados por comas (ej: 1,3,5) "
            "o envía los nombres exactos de los archivos separados por comas."
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error al procesar el ZIP: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_filenames_to_remove(update: Update, chat_id: int):
    """Handle filenames to remove from ZIP"""
    if not update.message.text:
        await update.message.reply_text("Por favor, envía los números o nombres de los archivos a eliminar.")
        return

    try:
        zip_path = get_user_data(chat_id, 'zip_path')
        current_files = get_user_data(chat_id, 'current_files', [])
        user_input = update.message.text.strip()

        files_to_remove = []

        # Check if input contains numbers (indices) or filenames
        if user_input.replace(',', '').replace(' ', '').isdigit():
            # Input contains indices
            indices = [int(x.strip()) - 1 for x in user_input.split(',') if x.strip().isdigit()]
            for idx in indices:
                if 0 <= idx < len(current_files):
                    files_to_remove.append(current_files[idx])
        else:
            # Input contains filenames
            requested_files = [x.strip() for x in user_input.split(',')]
            for filename in requested_files:
                if filename in current_files:
                    files_to_remove.append(filename)

        if not files_to_remove:
            await update.message.reply_text("❌ No se encontraron archivos válidos para eliminar.")
            return

        # Send processing message and advertisement
        await send_processing_and_ad_message(update, f"🔄 Eliminando {len(files_to_remove)} archivos del ZIP...")

        new_zip_path = await remove_files_from_zip(zip_path, files_to_remove, chat_id)
        if new_zip_path:
            with open(new_zip_path, 'rb') as new_zip_file:
                await update.message.reply_document(
                    document=new_zip_file,
                    filename=f"zip_actualizado_{chat_id}.zip",
                    caption=f"✅ ZIP actualizado. Eliminados {len(files_to_remove)} archivos."
                )
            os.remove(new_zip_path)
        else:
            await update.message.reply_text("❌ Error al eliminar archivos del ZIP.")

        # Clean up
        if os.path.exists(zip_path):
            os.remove(zip_path)

        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error al eliminar archivos: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

def filter_valid_files(file_list):
    """Filter out macOS metadata files and other invalid files"""
    valid_files = []
    for file_name in file_list:
        # Skip macOS metadata files
        if file_name.startswith('__MACOSX/') or file_name.startswith('._'):
            continue
        # Skip hidden files and directories
        if '/__MACOSX/' in file_name or '/._' in file_name:
            continue
        # Skip directories
        if file_name.endswith('/'):
            continue
        # Only include files with actual content
        if file_name.strip():
            valid_files.append(file_name)
    return valid_files

async def handle_zip_for_bulk(update: Update, chat_id: int):
    """Handle ZIP file for bulk operations"""
    is_valid, message = await validate_file(update, ['zip'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        zip_path = os.path.join(temp_dir, f"zip_for_bulk_{chat_id}_{file_name}")

        await file.download_to_drive(zip_path)

        # List current files and filter out metadata files
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            all_files = zip_ref.namelist()
            current_files = filter_valid_files(all_files)

        if not current_files:
            await update.message.reply_text("❌ El ZIP no contiene archivos válidos.")
            os.remove(zip_path)
            set_user_state(chat_id, AWAITING_OPTION)
            return

        # Categorize files
        pdf_files = [f for f in current_files if f.lower().endswith('.pdf')]
        image_files = [f for f in current_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg'))]

        set_user_state(chat_id, AWAITING_BULK_OPERATION, zip_path=zip_path, current_files=current_files)

        options_text = (
            "🗜️ **Operaciones en masa disponibles:**\n\n"
            "1. **Convertir imágenes PNG → JPEG**\n"
            "2. **Convertir imágenes JPEG → PNG**\n"
            "3. **Convertir SVG → PNG**\n"
            "4. **Convertir SVG → JPEG**\n"
        )

        if len(pdf_files) > 1:
            options_text += "5. **Concatenar todos los PDFs**\n"

        options_text += f"\n📊 **Archivos detectados:**\n"
        options_text += f"• PDFs: {len(pdf_files)}\n"
        options_text += f"• Imágenes: {len(image_files)}\n"
        options_text += f"• Otros: {len(current_files) - len(pdf_files) - len(image_files)}\n\n"
        options_text += "Envía el número de la operación que quieres realizar:"

        await update.message.reply_text(options_text)

    except Exception as e:
        await update.message.reply_text(f"❌ Error al procesar el ZIP: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_pdf_concatenation_order(update: Update, chat_id: int):
    """Handle PDF concatenation order specification in bulk operations"""
    if not update.message.text:
        await update.message.reply_text("Por favor, envía el orden de concatenación.")
        return

    try:
        user_input = update.message.text.strip()
        pdf_files = get_user_data(chat_id, 'pdf_files', [])
        zip_path = get_user_data(chat_id, 'zip_path')
        current_files = get_user_data(chat_id, 'current_files', [])
        operation = get_user_data(chat_id, 'operation')

        # Parse the order
        try:
            order_indices = [int(x.strip()) - 1 for x in user_input.split(',')]

            # Validate indices
            if len(order_indices) != len(pdf_files):
                await update.message.reply_text(
                    f"❌ Debes especificar exactamente {len(pdf_files)} números (uno para cada PDF)."
                )
                return

            if any(idx < 0 or idx >= len(pdf_files) for idx in order_indices):
                await update.message.reply_text(
                    f"❌ Los números deben estar entre 1 y {len(pdf_files)}."
                )
                return

            if len(set(order_indices)) != len(order_indices):
                await update.message.reply_text("❌ No puedes repetir números. Cada PDF debe aparecer exactamente una vez.")
                return

        except ValueError:
            await update.message.reply_text(
                "❌ Formato inválido. Usa números separados por comas (ejemplo: 2,1,3)."
            )
            return

        # Reorder PDF files according to user specification
        ordered_pdf_files = [pdf_files[i] for i in order_indices]

        # Send processing message and advertisement
        processing_message = (
            f"🔄 Concatenando PDFs en el orden especificado:\n" +
            "\n".join([f"{i+1}. {pdf}" for i, pdf in enumerate(ordered_pdf_files)])
        )
        await send_processing_and_ad_message(update, processing_message)

        # Perform the bulk operation with ordered PDFs
        new_zip_path = await perform_bulk_operation_with_order(zip_path, current_files, operation, chat_id, ordered_pdf_files)

        # Send result
        if new_zip_path:
            with open(new_zip_path, 'rb') as new_zip_file:
                await update.message.reply_document(
                    document=new_zip_file,
                    filename=f"zip_procesado_{chat_id}.zip",
                    caption="✅ PDFs concatenados en el orden especificado!"
                )
            os.remove(new_zip_path)
        else:
            await update.message.reply_text("❌ Error al concatenar los PDFs.")

        # Clean up
        if os.path.exists(zip_path):
            os.remove(zip_path)

        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error al procesar el orden: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_bulk_operation(update: Update, chat_id: int):
    """Handle bulk operation selection and execution"""
    if not update.message.text or not update.message.text.strip().isdigit():
        await update.message.reply_text("Por favor, envía el número de la operación deseada.")
        return

    try:
        operation = int(update.message.text.strip())
        zip_path = get_user_data(chat_id, 'zip_path')
        current_files = get_user_data(chat_id, 'current_files', [])

        # Special handling for PDF concatenation (operation 5)
        if operation == 5:
            # Find PDF files (already filtered in current_files)
            pdf_files = [f for f in current_files if f.lower().endswith('.pdf')]

            if len(pdf_files) < 2:
                await update.message.reply_text("❌ Se necesitan al menos 2 archivos PDF para concatenar.")
                return
            elif len(pdf_files) == 2:
                # If only 2 PDFs, proceed directly
                await send_processing_and_ad_message(update, "🔄 Concatenando 2 archivos PDF...")
                new_zip_path = await perform_bulk_operation(zip_path, current_files, operation, chat_id)
            else:
                # If more than 2 PDFs, ask for order
                pdf_list = "\n".join([f"{i+1}. {pdf}" for i, pdf in enumerate(pdf_files)])

                set_user_state(chat_id, AWAITING_PDF_CONCATENATION_ORDER,
                             zip_path=zip_path,
                             current_files=current_files,
                             pdf_files=pdf_files,
                             operation=operation)

                await update.message.reply_text(
                    f"📋 **Se encontraron {len(pdf_files)} archivos PDF:**\n\n{pdf_list}\n\n"
                    f"📝 **Especifica el orden para concatenar los PDFs**\n"
                    f"Envía los números separados por comas (ejemplo: 2,1,3)\n"
                    f"Esto concatenará el archivo 2 primero, luego el 1, luego el 3."
                )
                return
        else:
            # For other operations, proceed directly
            await send_processing_and_ad_message(update, "🔄 Realizando operación en masa...")
            new_zip_path = await perform_bulk_operation(zip_path, current_files, operation, chat_id)

        # Send result
        if new_zip_path:
            with open(new_zip_path, 'rb') as new_zip_file:
                await update.message.reply_document(
                    document=new_zip_file,
                    filename=f"zip_procesado_{chat_id}.zip",
                    caption="✅ Operación en masa completada!"
                )
            os.remove(new_zip_path)
        else:
            await update.message.reply_text("❌ Error al realizar la operación en masa.")

        # Clean up
        if os.path.exists(zip_path):
            os.remove(zip_path)

        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error en la operación: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

# ZIP utility functions
async def create_zip_from_files(file_paths: list, chat_id: int) -> str:
    """Create a ZIP file from multiple files"""
    try:
        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, f"created_{chat_id}.zip")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in file_paths:
                filename = os.path.basename(file_path)
                zip_file.write(file_path, filename)

        return zip_path
    except Exception as e:
        print(f"Error creating ZIP: {e}")
        return None

async def add_files_to_zip(zip_path: str, files_to_add: list, chat_id: int) -> str:
    """Add files to an existing ZIP"""
    try:
        temp_dir = tempfile.gettempdir()
        new_zip_path = os.path.join(temp_dir, f"updated_{chat_id}.zip")

        with zipfile.ZipFile(zip_path, 'r') as original_zip:
            with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                # Copy existing files
                for item in original_zip.namelist():
                    data = original_zip.read(item)
                    new_zip.writestr(item, data)

                # Add new files
                for file_path in files_to_add:
                    filename = os.path.basename(file_path)
                    new_zip.write(file_path, filename)

        return new_zip_path
    except Exception as e:
        print(f"Error adding files to ZIP: {e}")
        return None

async def remove_files_from_zip(zip_path: str, files_to_remove: list, chat_id: int) -> str:
    """Remove files from an existing ZIP"""
    try:
        temp_dir = tempfile.gettempdir()
        new_zip_path = os.path.join(temp_dir, f"filtered_{chat_id}.zip")

        with zipfile.ZipFile(zip_path, 'r') as original_zip:
            with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                for item in original_zip.namelist():
                    if item not in files_to_remove:
                        data = original_zip.read(item)
                        new_zip.writestr(item, data)

        return new_zip_path
    except Exception as e:
        print(f"Error removing files from ZIP: {e}")
        return None

async def perform_bulk_operation_with_order(zip_path: str, files: list, operation: int, chat_id: int, ordered_pdf_files: list) -> str:
    """Perform bulk operations on files in ZIP with custom PDF order"""
    try:
        temp_dir = tempfile.gettempdir()
        extract_dir = os.path.join(temp_dir, f"bulk_extract_{chat_id}")
        new_zip_path = os.path.join(temp_dir, f"bulk_processed_{chat_id}.zip")

        # Extract ZIP
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
            # For operation 5 (PDF concatenation), use the ordered list
            if operation == 5 and ordered_pdf_files:
                processed_files = []

                # Collect PDF files in the specified order
                for pdf_filename in ordered_pdf_files:
                    file_path = os.path.join(extract_dir, pdf_filename)
                    if os.path.exists(file_path):
                        processed_files.append(file_path)

                # Concatenate PDFs in order
                if len(processed_files) > 1:
                    try:
                        concatenated_path = await concatenate_multiple_pdfs(processed_files, chat_id)
                        if concatenated_path:
                            new_zip.write(concatenated_path, f"concatenated_pdfs_{chat_id}.pdf")
                            os.remove(concatenated_path)
                        else:
                            # If concatenation fails, add individual PDFs in order
                            for pdf_path in processed_files:
                                filename = os.path.basename(pdf_path)
                                new_zip.write(pdf_path, filename)
                    except Exception:
                        # If concatenation fails, add individual PDFs in order
                        for pdf_path in processed_files:
                            filename = os.path.basename(pdf_path)
                            new_zip.write(pdf_path, filename)

                # Add all non-PDF files (excluding metadata files)
                for filename in files:
                    # Skip macOS metadata files
                    if filename.startswith('__MACOSX/') or filename.startswith('._') or '/__MACOSX/' in filename or '/._' in filename:
                        continue

                    if not filename.lower().endswith('.pdf'):
                        file_path = os.path.join(extract_dir, filename)
                        if os.path.exists(file_path):
                            new_zip.write(file_path, filename)

        # Clean up extraction directory
        shutil.rmtree(extract_dir)

        return new_zip_path
    except Exception as e:
        print(f"Error in bulk operation with order: {e}")
        return None

async def perform_bulk_operation(zip_path: str, files: list, operation: int, chat_id: int) -> str:
    """Perform bulk operations on files in ZIP"""
    try:
        temp_dir = tempfile.gettempdir()
        extract_dir = os.path.join(temp_dir, f"bulk_extract_{chat_id}")
        new_zip_path = os.path.join(temp_dir, f"bulk_processed_{chat_id}.zip")

        # Extract ZIP
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Process files based on operation
        processed_files = []

        with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
            for filename in files:
                # Skip macOS metadata files
                if filename.startswith('__MACOSX/') or filename.startswith('._') or '/__MACOSX/' in filename or '/._' in filename:
                    continue

                file_path = os.path.join(extract_dir, filename)

                if not os.path.exists(file_path):
                    continue

                processed = False

                if operation == 1 and filename.lower().endswith('.png'):
                    # PNG to JPEG
                    try:
                        with Image.open(file_path) as img:
                            if img.mode in ('RGBA', 'LA'):
                                background = Image.new('RGB', img.size, (255, 255, 255))
                                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                                img = background
                            new_filename = filename.rsplit('.', 1)[0] + '.jpg'
                            new_file_path = os.path.join(extract_dir, new_filename)
                            img.save(new_file_path, 'JPEG', quality=95)
                            new_zip.write(new_file_path, new_filename)
                            processed = True
                    except Exception:
                        pass

                elif operation == 2 and filename.lower().endswith(('.jpg', '.jpeg')):
                    # JPEG to PNG
                    try:
                        with Image.open(file_path) as img:
                            new_filename = filename.rsplit('.', 1)[0] + '.png'
                            new_file_path = os.path.join(extract_dir, new_filename)
                            img.save(new_file_path, 'PNG')
                            new_zip.write(new_file_path, new_filename)
                            processed = True
                    except Exception:
                        pass

                elif operation == 3 and filename.lower().endswith('.svg'):
                    # SVG to PNG
                    try:
                        new_filename = filename.rsplit('.', 1)[0] + '.png'
                        new_file_path = os.path.join(extract_dir, new_filename)
                        cairosvg.svg2png(url=file_path, write_to=new_file_path, dpi=300)
                        new_zip.write(new_file_path, new_filename)
                        processed = True
                    except Exception:
                        pass

                elif operation == 4 and filename.lower().endswith('.svg'):
                    # SVG to JPEG
                    try:
                        png_path = os.path.join(extract_dir, f"temp_{filename}.png")
                        new_filename = filename.rsplit('.', 1)[0] + '.jpg'
                        new_file_path = os.path.join(extract_dir, new_filename)

                        cairosvg.svg2png(url=file_path, write_to=png_path, dpi=300)
                        with Image.open(png_path) as img:
                            if img.mode in ('RGBA', 'LA'):
                                background = Image.new('RGB', img.size, (255, 255, 255))
                                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                                img = background
                            img.save(new_file_path, 'JPEG', quality=95)

                        new_zip.write(new_file_path, new_filename)
                        os.remove(png_path)
                        processed = True
                    except Exception:
                        pass

                elif operation == 5 and filename.lower().endswith('.pdf'):
                    # Collect PDFs for concatenation
                    processed_files.append(file_path)
                    continue

                # If not processed, keep original file
                if not processed:
                    new_zip.write(file_path, filename)

            # Handle PDF concatenation if operation 5
            if operation == 5 and len(processed_files) > 1:
                try:
                    concatenated_path = await concatenate_multiple_pdfs(processed_files, chat_id)
                    if concatenated_path:
                        new_zip.write(concatenated_path, f"concatenated_pdfs_{chat_id}.pdf")
                        os.remove(concatenated_path)
                except Exception:
                    # If concatenation fails, add individual PDFs
                    for pdf_path in processed_files:
                        filename = os.path.basename(pdf_path)
                        new_zip.write(pdf_path, filename)

        # Clean up extraction directory
        shutil.rmtree(extract_dir)

        return new_zip_path
    except Exception as e:
        print(f"Error in bulk operation: {e}")
        return None

async def handle_idle_state(update: Update, chat_id: int):
    """Handle when user is in idle state"""
    await update.message.reply_text("Escribe /help para ver las opciones disponibles.")

async def send_processing_and_ad_message(update: Update, processing_message: str, delay_seconds: float = 2.0):
    """Send processing message, then advertising message after a delay"""
    # Send initial processing message
    await update.message.reply_text(processing_message)

    # Wait a bit to simulate processing time
    await asyncio.sleep(delay_seconds)

    # Send random advertising message
    ad_message = random.choice(mensajes_promocionales)
    await update.message.reply_text(ad_message)


