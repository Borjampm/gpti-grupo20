import os
import tempfile
from telegram import Update
from ..state_manager import set_user_state, AWAITING_OPTION, IDLE
from ..utils import validate_file, send_processing_and_ad_message
from ..file_processing.image_processor import (
    transform_to_png, transform_to_jpeg
)

async def handle_generic_image_to_png(update: Update, chat_id: int):
    """Handle generic image conversion to PNG with automatic format detection"""
    # Support JPEG, SVG, and PDF files
    is_valid, message = await validate_file(update, ['jpg', 'jpeg', 'svg', 'pdf'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        input_path = os.path.join(temp_dir, f"input_{chat_id}_{file_name}")

        await file.download_to_drive(input_path)

        # Get file extension
        file_extension = file_name.lower().split('.')[-1]

        await send_processing_and_ad_message(update, f"🔄 Convirtiendo {file_extension.upper()} a PNG...")

        result, is_multiple = await transform_to_png(input_path, chat_id, file_extension)

        if is_multiple:
            # Multiple files (PDF pages)
            output_paths = result
            await update.message.reply_text(f"📄 Procesando {len(output_paths)} páginas...")
            for i, output_path in enumerate(output_paths, 1):
                with open(output_path, 'rb') as output_file:
                    await update.message.reply_document(
                        document=output_file,
                        filename=f"page_{i}_{file_name.rsplit('.', 1)[0]}.png",
                        caption=f"✅ Página {i} de {len(output_paths)}"
                    )
                os.remove(output_path)
        else:
            # Single file
            output_path = result
            with open(output_path, 'rb') as output_file:
                await update.message.reply_document(
                    document=output_file,
                    filename=f"converted_{file_name.rsplit('.', 1)[0]}.png",
                    caption=f"✅ {file_extension.upper()} convertido a PNG exitosamente!"
                )
            os.remove(output_path)

        os.remove(input_path)
        set_user_state(chat_id, IDLE)
        await update.message.reply_text("¿En qué más puedo ayudarte?")

    except ValueError as e:
        await update.message.reply_text(f"❌ {str(e)}")
        set_user_state(chat_id, IDLE)
    except Exception as e:
        await update.message.reply_text(f"Error al convertir la imagen: {str(e)}")
        set_user_state(chat_id, IDLE)

async def handle_generic_image_to_jpeg(update: Update, chat_id: int):
    """Handle generic image conversion to JPEG with automatic format detection"""
    # Support PNG, SVG, and PDF files
    is_valid, message = await validate_file(update, ['png', 'svg', 'pdf'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        input_path = os.path.join(temp_dir, f"input_{chat_id}_{file_name}")

        await file.download_to_drive(input_path)

        # Get file extension
        file_extension = file_name.lower().split('.')[-1]

        await send_processing_and_ad_message(update, f"🔄 Convirtiendo {file_extension.upper()} a JPEG...")

        result, is_multiple = await transform_to_jpeg(input_path, chat_id, file_extension)

        if is_multiple:
            # Multiple files (PDF pages)
            output_paths = result
            await update.message.reply_text(f"📄 Procesando {len(output_paths)} páginas...")
            for i, output_path in enumerate(output_paths, 1):
                with open(output_path, 'rb') as output_file:
                    await update.message.reply_document(
                        document=output_file,
                        filename=f"page_{i}_{file_name.rsplit('.', 1)[0]}.jpg",
                        caption=f"✅ Página {i} de {len(output_paths)}"
                    )
                os.remove(output_path)
        else:
            # Single file
            output_path = result
            with open(output_path, 'rb') as output_file:
                await update.message.reply_document(
                    document=output_file,
                    filename=f"converted_{file_name.rsplit('.', 1)[0]}.jpg",
                    caption=f"✅ {file_extension.upper()} convertido a JPEG exitosamente!"
                )
            os.remove(output_path)

        os.remove(input_path)
        set_user_state(chat_id, IDLE)
        await update.message.reply_text("¿En qué más puedo ayudarte?")

    except ValueError as e:
        await update.message.reply_text(f"❌ {str(e)}")
        set_user_state(chat_id, IDLE)
    except Exception as e:
        await update.message.reply_text(f"Error al convertir la imagen: {str(e)}")
        set_user_state(chat_id, IDLE)
