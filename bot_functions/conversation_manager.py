from telegram import Update
from telegram.ext import ContextTypes
import os
import tempfile
from PyPDF2 import PdfWriter, PdfReader
import asyncio

# Global instance to manage conversation states
conversation_state = {}

# State constants
IDLE = "IDLE"
AWAITING_OPTION = "AWAITING_OPTION"
AWAITING_MESSAGE = "AWAITING_MESSAGE"
AWAITING_FIRST_PDF = "AWAITING_FIRST_PDF"
AWAITING_SECOND_PDF = "AWAITING_SECOND_PDF"

def get_user_state(chat_id):
    """Get the current state of a user"""
    return conversation_state.get(chat_id, {}).get('state', IDLE)

def set_user_state(chat_id, state, option=None, first_pdf_path=None):
    """Set the state of a user"""
    if chat_id not in conversation_state:
        conversation_state[chat_id] = {}
    conversation_state[chat_id]['state'] = state
    if option is not None:
        conversation_state[chat_id]['selected_option'] = option
    if first_pdf_path is not None:
        conversation_state[chat_id]['first_pdf_path'] = first_pdf_path

def get_user_option(chat_id):
    """Get the selected option of a user"""
    return conversation_state.get(chat_id, {}).get('selected_option')

def get_first_pdf_path(chat_id):
    """Get the first PDF path of a user"""
    return conversation_state.get(chat_id, {}).get('first_pdf_path')

def clear_user_data(chat_id):
    """Clear user data and temporary files"""
    if chat_id in conversation_state:
        # Clean up temporary files
        first_pdf = conversation_state[chat_id].get('first_pdf_path')
        if first_pdf and os.path.exists(first_pdf):
            os.remove(first_pdf)
        conversation_state[chat_id] = {}

async def conversation_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main conversation manager that handles user messages based on their state"""
    chat_id = update.message.chat_id
    current_state = get_user_state(chat_id)

    if current_state == AWAITING_OPTION:
        user_message = update.message.text
        await handle_option_selection(update, user_message, chat_id)
    elif current_state == AWAITING_MESSAGE:
        user_message = update.message.text
        await handle_message_processing(update, user_message, chat_id)
    elif current_state == AWAITING_FIRST_PDF:
        await handle_first_pdf_upload(update, chat_id)
    elif current_state == AWAITING_SECOND_PDF:
        await handle_second_pdf_upload(update, chat_id)
    else:  # IDLE or unknown state
        await handle_idle_state(update, chat_id)

async def handle_option_selection(update: Update, user_message: str, chat_id: int):
    """Handle when user is selecting an option (1, 2, or 3)"""
    if user_message == "1":
        set_user_state(chat_id, AWAITING_MESSAGE, option=1)
        await update.message.reply_text(
            "Elegiste la opción 1. Ahora envíame un mensaje para procesarlo."
        )
    elif user_message == "2":
        set_user_state(chat_id, AWAITING_MESSAGE, option=2)
        await update.message.reply_text(
            "Elegiste la opción 2. Ahora envíame un mensaje para procesarlo."
        )
    elif user_message == "3":
        set_user_state(chat_id, AWAITING_FIRST_PDF, option=3)
        await update.message.reply_text(
            "Elegiste la opción 3. Ahora envíame el primer archivo PDF que quieres concatenar."
        )
    else:
        await update.message.reply_text(
            "Esa no es una opción válida. Por favor, envía 1, 2 o 3."
        )

async def handle_message_processing(update: Update, user_message: str, chat_id: int):
    """Handle message processing based on selected option"""
    selected_option = get_user_option(chat_id)

    if selected_option == 1:
        # Option 1: Print message as-is
        print(user_message)
        await update.message.reply_text(user_message)
    elif selected_option == 2:
        # Option 2: Print message in uppercase
        await update.message.reply_text(user_message.upper())

    # Reset state to await new option
    set_user_state(chat_id, AWAITING_OPTION)
    await update.message.reply_text(
        "Puedes enviar otro número de opción o escribir /help para ver el menú nuevamente."
    )

async def handle_first_pdf_upload(update: Update, chat_id: int):
    """Handle the first PDF upload"""
    if not update.message.document:
        await update.message.reply_text(
            "Por favor, envía un archivo PDF. Asegúrate de que sea un documento válido."
        )
        return

    # Check if it's a PDF file
    file_name = update.message.document.file_name
    if not file_name or not file_name.lower().endswith('.pdf'):
        await update.message.reply_text(
            "Por favor, envía únicamente archivos PDF. El archivo debe tener extensión .pdf"
        )
        return

    try:
        # Download the file
        file = await update.message.document.get_file()

        # Create temporary file for the first PDF
        temp_dir = tempfile.gettempdir()
        first_pdf_path = os.path.join(temp_dir, f"first_pdf_{chat_id}_{file_name}")

        await file.download_to_drive(first_pdf_path)

        # Validate PDF file
        try:
            PdfReader(first_pdf_path)
        except Exception:
            os.remove(first_pdf_path)
            await update.message.reply_text(
                "El archivo no es un PDF válido. Por favor, envía un archivo PDF correcto."
            )
            return

        # Store the path and update state
        set_user_state(chat_id, AWAITING_SECOND_PDF, first_pdf_path=first_pdf_path)
        await update.message.reply_text(
            f"✅ Primer PDF recibido: {file_name}\n"
            "Ahora envíame el segundo archivo PDF para concatenar."
        )

    except Exception as e:
        await update.message.reply_text(
            f"Error al procesar el archivo: {str(e)}\n"
            "Por favor, intenta nuevamente con un archivo PDF válido."
        )

async def handle_second_pdf_upload(update: Update, chat_id: int):
    """Handle the second PDF upload and concatenation"""
    if not update.message.document:
        await update.message.reply_text(
            "Por favor, envía un archivo PDF. Asegúrate de que sea un documento válido."
        )
        return

    # Check if it's a PDF file
    file_name = update.message.document.file_name
    if not file_name or not file_name.lower().endswith('.pdf'):
        await update.message.reply_text(
            "Por favor, envía únicamente archivos PDF. El archivo debe tener extensión .pdf"
        )
        return

    try:
        # Download the second file
        file = await update.message.document.get_file()

        # Create temporary file for the second PDF
        temp_dir = tempfile.gettempdir()
        second_pdf_path = os.path.join(temp_dir, f"second_pdf_{chat_id}_{file_name}")

        await file.download_to_drive(second_pdf_path)

        # Validate PDF file
        try:
            PdfReader(second_pdf_path)
        except Exception:
            os.remove(second_pdf_path)
            await update.message.reply_text(
                "El archivo no es un PDF válido. Por favor, envía un archivo PDF correcto."
            )
            return

        await update.message.reply_text(
            f"✅ Segundo PDF recibido: {file_name}\n"
            "🔄 Concatenando archivos PDF..."
        )

        # Concatenate PDFs
        first_pdf_path = get_first_pdf_path(chat_id)
        output_path = await concatenate_pdfs(first_pdf_path, second_pdf_path, chat_id)

        if output_path:
            # Send the concatenated PDF
            with open(output_path, 'rb') as output_file:
                await update.message.reply_document(
                    document=output_file,
                    filename=f"concatenated_{chat_id}.pdf",
                    caption="✅ PDFs concatenados exitosamente!"
                )

            # Clean up temporary files
            os.remove(output_path)
        else:
            await update.message.reply_text(
                "❌ Error al concatenar los PDFs. Por favor, intenta nuevamente."
            )

        # Clean up temporary files
        if os.path.exists(second_pdf_path):
            os.remove(second_pdf_path)

        # Reset state and clear data
        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text(
            "Puedes enviar otro número de opción o escribir /help para ver el menú nuevamente."
        )

    except Exception as e:
        await update.message.reply_text(
            f"Error al procesar el archivo: {str(e)}\n"
            "Por favor, intenta nuevamente con archivos PDF válidos."
        )
        # Clean up on error
        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)

async def concatenate_pdfs(first_pdf_path: str, second_pdf_path: str, chat_id: int) -> str:
    """Concatenate two PDF files and return the output path"""
    try:
        # Create output path
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"concatenated_{chat_id}.pdf")

        # Create PDF writer
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

        # Write the concatenated PDF
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        return output_path

    except Exception as e:
        print(f"Error concatenating PDFs: {e}")
        return None

async def handle_idle_state(update: Update, chat_id: int):
    """Handle when user is in idle state"""
    await update.message.reply_text("Escribe /help para comenzar.")


