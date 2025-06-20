import os
import tempfile
from telegram import Update
from ..state_manager import set_user_state, AWAITING_OPTION, IDLE
from ..utils import validate_file, send_processing_and_ad_message
from ..file_processing.image_processor import (
    jpeg_to_png, png_to_jpeg, pdf_to_png, svg_to_png, svg_to_jpeg
)

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

        await file.download_to_drive(input_path)

        await send_processing_and_ad_message(update, "🔄 Convirtiendo JPEG a PNG...")

        output_path = await jpeg_to_png(input_path, chat_id)

        with open(output_path, 'rb') as output_file:
            await update.message.reply_document(
                document=output_file,
                filename=f"converted_{file_name.rsplit('.', 1)[0]}.png",
                caption="✅ JPEG convertido a PNG exitosamente!"
            )

        os.remove(input_path)
        os.remove(output_path)
        set_user_state(chat_id, IDLE)
        await update.message.reply_text("¿En qué más puedo ayudarte?")

    except Exception as e:
        await update.message.reply_text(f"Error al convertir la imagen: {str(e)}")
        set_user_state(chat_id, IDLE)

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

        await file.download_to_drive(input_path)

        await send_processing_and_ad_message(update, "🔄 Convirtiendo PNG a JPEG...")

        output_path = await png_to_jpeg(input_path, chat_id)

        with open(output_path, 'rb') as output_file:
            await update.message.reply_document(
                document=output_file,
                filename=f"converted_{file_name.rsplit('.', 1)[0]}.jpg",
                caption="✅ PNG convertido a JPEG exitosamente!"
            )

        os.remove(input_path)
        os.remove(output_path)
        set_user_state(chat_id, IDLE)
        await update.message.reply_text("¿En qué más puedo ayudarte?")

    except Exception as e:
        await update.message.reply_text(f"Error al convertir la imagen: {str(e)}")
        set_user_state(chat_id, IDLE)

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
            await send_processing_and_ad_message(update, "🔄 Convirtiendo primera página de PDF a PNG...")
        else:
            await send_processing_and_ad_message(update, "🔄 Convirtiendo todas las páginas de PDF a PNG...")

        output_paths = await pdf_to_png(input_path, chat_id, first_page_only)

        if first_page_only:
            if output_paths:
                with open(output_paths[0], 'rb') as output_file:
                    await update.message.reply_document(
                        document=output_file,
                        filename=f"page_1_{file_name.rsplit('.', 1)[0]}.png",
                        caption="✅ Primera página convertida a PNG!"
                    )
                os.remove(output_paths[0])
        else:
            await update.message.reply_text(f"📄 Procesando {len(output_paths)} páginas...")
            for i, output_path in enumerate(output_paths, 1):
                with open(output_path, 'rb') as output_file:
                    await update.message.reply_document(
                        document=output_file,
                        filename=f"page_{i}_{file_name.rsplit('.', 1)[0]}.png",
                        caption=f"✅ Página {i} de {len(output_paths)}"
                    )
                os.remove(output_path)

        os.remove(input_path)
        set_user_state(chat_id, IDLE)
        await update.message.reply_text("¿En qué más puedo ayudarte?")

    except Exception as e:
        await update.message.reply_text(f"Error al convertir PDF: {str(e)}")
        set_user_state(chat_id, IDLE)

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

        await send_processing_and_ad_message(update, f"🔄 Convirtiendo SVG a {output_format.upper()}...")

        if output_format == "png":
            output_path = await svg_to_png(input_path, chat_id)
            output_filename = f"converted_{file_name.rsplit('.', 1)[0]}.png"
        else:
            output_path = await svg_to_jpeg(input_path, chat_id)
            output_filename = f"converted_{file_name.rsplit('.', 1)[0]}.jpg"

        with open(output_path, 'rb') as output_file:
            await update.message.reply_document(
                document=output_file,
                filename=output_filename,
                caption=f"✅ SVG convertido a {output_format.upper()} exitosamente!"
            )

        os.remove(input_path)
        os.remove(output_path)
        set_user_state(chat_id, IDLE)
        await update.message.reply_text("¿En qué más puedo ayudarte?")

    except Exception as e:
        await update.message.reply_text(f"Error al convertir SVG: {str(e)}")
        set_user_state(chat_id, IDLE)
