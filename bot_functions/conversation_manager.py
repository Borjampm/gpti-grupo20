from telegram import Update
from telegram.ext import ContextTypes
from .state_manager import get_user_state, clear_user_data, set_user_state, AWAITING_OPTION, AWAITING_CLARIFICATION, AWAITING_FIRST_PDF, AWAITING_SECOND_PDF, AWAITING_MULTIPLE_PDFS, AWAITING_PDF_FOR_PAGE_DELETE, AWAITING_PAGE_NUMBERS_DELETE, AWAITING_PDF_FOR_PAGE_EXTRACT, AWAITING_PAGE_NUMBERS_EXTRACT, AWAITING_PDF_FOR_REORDER, AWAITING_PAGE_ORDER, AWAITING_MULTIPLE_FILES_FOR_ZIP, AWAITING_ZIP_TO_EXTRACT, AWAITING_ZIP_TO_LIST, AWAITING_ZIP_FOR_ADD, AWAITING_FILES_TO_ADD, AWAITING_ZIP_FOR_REMOVE, AWAITING_FILENAMES_TO_REMOVE, AWAITING_ZIP_FOR_BULK, AWAITING_BULK_OPERATION, AWAITING_PDF_CONCATENATION_ORDER, AWAITING_ZIP_FOR_IMAGES_TO_PNG, AWAITING_ZIP_FOR_IMAGES_TO_JPEG, AWAITING_ZIP_FOR_PDF_CONCATENATION, AWAITING_IMAGE_TO_PNG, AWAITING_IMAGE_TO_JPEG, AWAITING_DOCX_TO_PDF, AWAITING_PDF_TO_DOCX, AWAITING_CSV_TO_EXCEL, AWAITING_EXCEL_TO_CSV, AWAITING_PPTX_TO_PDF, IDLE, clear_conversation_history
from .utils import is_exit_command
from .handlers.main_handlers import handle_option_selection, handle_idle_state, handle_clarification_continuation
from .handlers.pdf_handlers import (
    handle_first_pdf_upload, handle_second_pdf_upload, handle_multiple_pdfs_upload,
    handle_pdf_for_page_operation, handle_page_numbers_delete, handle_page_numbers_extract,
    handle_page_order, handle_pdf_concatenation_order
)
from .handlers.image_handlers import (
    handle_generic_image_to_png, handle_generic_image_to_jpeg
)
from .handlers.document_handlers import (
    handle_docx_to_pdf, handle_pdf_to_docx, handle_csv_to_excel,
    handle_excel_to_csv, handle_pptx_to_pdf
)
from .handlers.zip_handlers import (
    handle_multiple_files_for_zip, handle_zip_extraction, handle_zip_listing,
    handle_zip_for_add, handle_files_to_add, handle_zip_for_remove,
    handle_filenames_to_remove, handle_zip_for_bulk, handle_bulk_operation,
    handle_zip_for_images_to_png, handle_zip_for_images_to_jpeg, handle_zip_for_pdf_concatenation
)


async def conversation_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main conversation manager that handles user messages based on their state"""
    chat_id = update.message.chat_id
    current_state = get_user_state(chat_id)

    # Check for exit command - interrupt any ongoing action except IDLE
    if current_state != IDLE and update.message.text and is_exit_command(update.message.text):
        clear_user_data(chat_id)
        clear_conversation_history(chat_id)
        set_user_state(chat_id, IDLE)
        await update.message.reply_text(
            "✅ **Acción cancelada**\n\n"
            "Has vuelto al chat normal. ¿En qué puedo ayudarte?"
        )
        return

    if current_state == AWAITING_OPTION:
        user_message = update.message.text
        await handle_option_selection(update, user_message, chat_id)
    elif current_state == AWAITING_CLARIFICATION:
        await handle_clarification_continuation(update, chat_id)
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
    elif current_state == AWAITING_ZIP_FOR_IMAGES_TO_PNG:
        await handle_zip_for_images_to_png(update, chat_id)
    elif current_state == AWAITING_ZIP_FOR_IMAGES_TO_JPEG:
        await handle_zip_for_images_to_jpeg(update, chat_id)
    elif current_state == AWAITING_ZIP_FOR_PDF_CONCATENATION:
        await handle_zip_for_pdf_concatenation(update, chat_id)
    elif current_state == AWAITING_IMAGE_TO_PNG:
        await handle_generic_image_to_png(update, chat_id)
    elif current_state == AWAITING_IMAGE_TO_JPEG:
        await handle_generic_image_to_jpeg(update, chat_id)
    elif current_state == AWAITING_DOCX_TO_PDF:
        await handle_docx_to_pdf(update, chat_id)
    elif current_state == AWAITING_PDF_TO_DOCX:
        await handle_pdf_to_docx(update, chat_id)
    elif current_state == AWAITING_CSV_TO_EXCEL:
        await handle_csv_to_excel(update, chat_id)
    elif current_state == AWAITING_EXCEL_TO_CSV:
        await handle_excel_to_csv(update, chat_id)
    elif current_state == AWAITING_PPTX_TO_PDF:
        await handle_pptx_to_pdf(update, chat_id)
    else:
        await handle_idle_state(update, chat_id)


