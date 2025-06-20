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

# File size limit (20 MB)
MAX_FILE_SIZE = 20 * 1024 * 1024

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
            elif key == 'pdf_paths' and isinstance(value, list):
                for path in value:
                    if os.path.exists(path):
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
    else:
        await update.message.reply_text("Opción no válida. Por favor, elige un número del 1 al 11.")

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

        await update.message.reply_text(
            f"✅ Segundo PDF recibido: {file_name} ({page_count} páginas)\n"
            "🔄 Concatenando archivos..."
        )

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

        await update.message.reply_text(f"🔄 Concatenando {len(pdf_paths)} archivos PDF...")

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

        await update.message.reply_text(f"🔄 Eliminando páginas {', '.join(map(str, pages_to_delete))}...")

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

        await update.message.reply_text(f"🔄 Extrayendo páginas {', '.join(map(str, pages_to_extract))}...")

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

        await update.message.reply_text(f"🔄 Reordenando páginas según: {', '.join(map(str, order_parts))}...")

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
        await update.message.reply_text("🔄 Convirtiendo JPEG a PNG...")

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
        await update.message.reply_text("🔄 Convirtiendo PNG a JPEG...")

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

        if first_page_only:
            await update.message.reply_text("🔄 Convirtiendo primera página de PDF a PNG...")
        else:
            await update.message.reply_text("🔄 Convirtiendo todas las páginas de PDF a PNG...")

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
        await update.message.reply_text(f"🔄 Convirtiendo SVG a {output_format.upper()}...")

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

        # Add pages from first PDF
        with open(first_pdf_path, 'rb') as first_file:
            first_reader = PdfReader(first_file)
            for page in first_reader.pages:
                pdf_writer.add_page(page)

        # Add pages from second PDF
        with open(second_pdf_path, 'rb') as second_file:
            second_reader = PdfReader(second_file)
            for page in second_reader.pages:
                pdf_writer.add_page(page)

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
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)

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

async def handle_idle_state(update: Update, chat_id: int):
    """Handle when user is in idle state"""
    await update.message.reply_text("Escribe /help para ver las opciones disponibles.")


