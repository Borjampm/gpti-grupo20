import os
import tempfile
from telegram import Update
from PyPDF2 import PdfReader
from ..state_manager import set_user_state, get_user_data, clear_user_data, AWAITING_SECOND_PDF, AWAITING_MULTIPLE_PDFS, AWAITING_PAGE_NUMBERS_DELETE, AWAITING_PAGE_NUMBERS_EXTRACT, AWAITING_PAGE_ORDER, AWAITING_OPTION, AWAITING_PDF_CONCATENATION_ORDER, IDLE
from ..utils import validate_file, send_processing_and_ad_message, parse_page_numbers
from ..file_processing.pdf_processor import (
    concatenate_two_pdfs, concatenate_multiple_pdfs, delete_pdf_pages,
    extract_pdf_pages, reorder_pdf_pages
)
from ..file_processing.zip_processor import perform_bulk_operation_with_order

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
        set_user_state(chat_id, IDLE)
        await update.message.reply_text("¿En qué más puedo ayudarte?")

    except Exception as e:
        await update.message.reply_text(f"Error al procesar el archivo: {str(e)}")
        clear_user_data(chat_id)
        set_user_state(chat_id, IDLE)

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
        set_user_state(chat_id, IDLE)
        await update.message.reply_text("¿En qué más puedo ayudarte?")
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
        set_user_state(chat_id, IDLE)
        await update.message.reply_text("¿En qué más puedo ayudarte?")

    except ValueError as e:
        await update.message.reply_text(f"Error en el formato de páginas: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"Error al procesar: {str(e)}")
        clear_user_data(chat_id)
        set_user_state(chat_id, IDLE)

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
        set_user_state(chat_id, IDLE)
        await update.message.reply_text("¿En qué más puedo ayudarte?")

    except ValueError as e:
        await update.message.reply_text(f"Error en el formato de páginas: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"Error al procesar: {str(e)}")
        clear_user_data(chat_id)
        set_user_state(chat_id, IDLE)

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
        set_user_state(chat_id, IDLE)
        await update.message.reply_text("¿En qué más puedo ayudarte?")

    except ValueError:
        await update.message.reply_text("Por favor, usa solo números separados por comas (ej: 3,1,2,4).")
    except Exception as e:
        await update.message.reply_text(f"Error al procesar: {str(e)}")
        clear_user_data(chat_id)
        set_user_state(chat_id, IDLE)

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
        set_user_state(chat_id, IDLE)
        await update.message.reply_text("¿En qué más puedo ayudarte?")

    except Exception as e:
        await update.message.reply_text(f"❌ Error al procesar el orden: {str(e)}")
        set_user_state(chat_id, IDLE)
