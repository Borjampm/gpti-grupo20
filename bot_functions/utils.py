from telegram import Update
import asyncio
import random
from .ad_messages import mensajes_promocionales

MAX_FILE_SIZE = 20 * 1024 * 1024

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

async def send_processing_and_ad_message(update: Update, processing_message: str, delay_seconds: float = 2.0):
    """Send processing message, then advertising message after a delay"""
    # Send initial processing message
    await update.message.reply_text(processing_message)

    # Wait a bit to simulate processing time
    await asyncio.sleep(delay_seconds)

    # Send random advertising message
    ad_message = random.choice(mensajes_promocionales)
    await update.message.reply_text(ad_message)
