from telegram import Update
from ..state_manager import set_user_state, IDLE
from ..utils import validate_file, send_processing_and_ad_message
from ..file_processing.document_processor import (
    convert_docx_to_pdf, convert_pdf_to_docx,
    convert_csv_to_excel, convert_excel_to_csv,
    convert_pptx_to_pdf
)
import os

async def handle_docx_to_pdf(update: Update, chat_id: int):
    """Handle DOCX to PDF conversion"""
    # Validate file
    is_valid, message = await validate_file(update, ['docx'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        document = update.message.document
        file = await update.get_bot().get_file(document.file_id)

        # Download file
        temp_input_path = f"temp_docx_{chat_id}.docx"
        await file.download_to_drive(temp_input_path)

        # Send processing message
        await send_processing_and_ad_message(
            update,
            "🔄 Convirtiendo documento Word a PDF con preservación de formato...",
            2.0
        )

        # Convert DOCX to PDF
        output_path = await convert_docx_to_pdf(temp_input_path, chat_id)

        if output_path and os.path.exists(output_path):
            # Determine which method was used for appropriate caption
            caption = "✅ **Conversión completada**\n\n"

            # Check if docx2pdf is available to determine the method used
            try:
                from docx2pdf import convert
                caption += ("📄 Documento Word convertido a PDF con **formato preservado** usando docx2pdf.\n\n"
                           "✨ Esta conversión mantiene el formato original, incluyendo fuentes, estilos e imágenes.")
            except ImportError:
                caption += ("📄 Documento Word convertido a PDF usando método alternativo.\n\n"
                           "⚠️ **Nota**: Para una mejor preservación del formato, "
                           "instala la biblioteca docx2pdf: `pip install docx2pdf`")

            # Send the converted file
            with open(output_path, 'rb') as pdf_file:
                await update.message.reply_document(
                    document=pdf_file,
                    filename=f"{document.file_name.rsplit('.', 1)[0]}.pdf",
                    caption=caption
                )

            # Clean up
            os.remove(output_path)
        else:
            await update.message.reply_text(
                "❌ **Error en la conversión**\n\n"
                "No se pudo convertir el documento Word a PDF. "
                "Asegúrate de que el archivo no esté corrupto."
            )

        # Clean up input file
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

    except Exception as e:
        await update.message.reply_text(
            f"❌ **Error inesperado**\n\n"
            f"Ocurrió un error al procesar el archivo: {str(e)}"
        )

    # Reset state
    set_user_state(chat_id, IDLE)

async def handle_pdf_to_docx(update: Update, chat_id: int):
    """Handle PDF to DOCX conversion"""
    # Validate file
    is_valid, message = await validate_file(update, ['pdf'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        document = update.message.document
        file = await update.get_bot().get_file(document.file_id)

        # Download file
        temp_input_path = f"temp_pdf_{chat_id}.pdf"
        await file.download_to_drive(temp_input_path)

        # Send processing message
        await send_processing_and_ad_message(
            update,
            "🔄 Convirtiendo PDF a documento Word...",
            2.0
        )

        # Convert PDF to DOCX
        output_path = await convert_pdf_to_docx(temp_input_path, chat_id)

        if output_path and os.path.exists(output_path):
            # Send the converted file
            with open(output_path, 'rb') as docx_file:
                await update.message.reply_document(
                    document=docx_file,
                    filename=f"{document.file_name.rsplit('.', 1)[0]}.docx",
                    caption="✅ **Conversión completada**\n\nPDF convertido a documento Word.\n\n"
                           "⚠️ **Nota:** La conversión extrae solo el texto del PDF."
                )

            # Clean up
            os.remove(output_path)
        else:
            await update.message.reply_text(
                "❌ **Error en la conversión**\n\n"
                "No se pudo convertir el PDF a documento Word. "
                "Asegúrate de que el PDF contenga texto extraíble."
            )

        # Clean up input file
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

    except Exception as e:
        await update.message.reply_text(
            f"❌ **Error inesperado**\n\n"
            f"Ocurrió un error al procesar el archivo: {str(e)}"
        )

    # Reset state
    set_user_state(chat_id, IDLE)

async def handle_csv_to_excel(update: Update, chat_id: int):
    """Handle CSV to Excel conversion"""
    # Validate file
    is_valid, message = await validate_file(update, ['csv'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        document = update.message.document
        file = await update.get_bot().get_file(document.file_id)

        # Download file
        temp_input_path = f"temp_csv_{chat_id}.csv"
        await file.download_to_drive(temp_input_path)

        # Send processing message
        await send_processing_and_ad_message(
            update,
            "🔄 Convirtiendo CSV a Excel...",
            1.5
        )

        # Convert CSV to Excel
        output_path = await convert_csv_to_excel(temp_input_path, chat_id)

        if output_path and os.path.exists(output_path):
            # Send the converted file
            with open(output_path, 'rb') as excel_file:
                await update.message.reply_document(
                    document=excel_file,
                    filename=f"{document.file_name.rsplit('.', 1)[0]}.xlsx",
                    caption="✅ **Conversión completada**\n\nArchivo CSV convertido a Excel."
                )

            # Clean up
            os.remove(output_path)
        else:
            await update.message.reply_text(
                "❌ **Error en la conversión**\n\n"
                "No se pudo convertir el archivo CSV a Excel. "
                "Verifica que el archivo CSV tenga el formato correcto."
            )

        # Clean up input file
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

    except Exception as e:
        await update.message.reply_text(
            f"❌ **Error inesperado**\n\n"
            f"Ocurrió un error al procesar el archivo: {str(e)}"
        )

    # Reset state
    set_user_state(chat_id, IDLE)

async def handle_excel_to_csv(update: Update, chat_id: int):
    """Handle Excel to CSV conversion"""
    # Validate file
    is_valid, message = await validate_file(update, ['xlsx', 'xls'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        document = update.message.document
        file = await update.get_bot().get_file(document.file_id)

        # Download file
        temp_input_path = f"temp_excel_{chat_id}.{document.file_name.split('.')[-1]}"
        await file.download_to_drive(temp_input_path)

        # Send processing message
        await send_processing_and_ad_message(
            update,
            "🔄 Convirtiendo Excel a CSV...",
            1.5
        )

        # Convert Excel to CSV
        output_path = await convert_excel_to_csv(temp_input_path, chat_id)

        if output_path and os.path.exists(output_path):
            # Send the converted file
            with open(output_path, 'rb') as csv_file:
                await update.message.reply_document(
                    document=csv_file,
                    filename=f"{document.file_name.rsplit('.', 1)[0]}.csv",
                    caption="✅ **Conversión completada**\n\nArchivo Excel convertido a CSV.\n\n"
                           "⚠️ **Nota:** Solo se convierte la primera hoja del archivo Excel."
                )

            # Clean up
            os.remove(output_path)
        else:
            await update.message.reply_text(
                "❌ **Error en la conversión**\n\n"
                "No se pudo convertir el archivo Excel a CSV. "
                "Verifica que el archivo Excel no esté corrupto."
            )

        # Clean up input file
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

    except Exception as e:
        await update.message.reply_text(
            f"❌ **Error inesperado**\n\n"
            f"Ocurrió un error al procesar el archivo: {str(e)}"
        )

    # Reset state
    set_user_state(chat_id, IDLE)

async def handle_pptx_to_pdf(update: Update, chat_id: int):
    """Handle PowerPoint to PDF conversion"""
    # Validate file
    is_valid, message = await validate_file(update, ['pptx', 'ppt'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        document = update.message.document
        file = await update.get_bot().get_file(document.file_id)

        # Download file
        temp_input_path = f"temp_pptx_{chat_id}.{document.file_name.split('.')[-1]}"
        await file.download_to_drive(temp_input_path)

        # Send processing message
        await send_processing_and_ad_message(
            update,
            "🔄 Convirtiendo presentación PowerPoint a PDF con preservación de formato...",
            3.0
        )

        # Convert PPTX to PDF
        output_path = await convert_pptx_to_pdf(temp_input_path, chat_id)

        if output_path and os.path.exists(output_path):
            # Determine appropriate caption based on conversion method
            caption = "✅ **Conversión completada**\n\n"

            # Check if LibreOffice is available
            import subprocess
            libreoffice_available = False
            try:
                # Try both common LibreOffice command names
                for cmd in ['libreoffice', 'soffice']:
                    try:
                        result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            libreoffice_available = True
                            break
                    except FileNotFoundError:
                        continue

                if libreoffice_available:
                    caption += ("📄 Presentación PowerPoint convertida a PDF con **formato preservado** usando LibreOffice CLI.\n\n"
                               "✨ Esta conversión mantiene el diseño original, incluyendo slides, imágenes y formato.")
                else:
                    caption += ("📄 Presentación PowerPoint convertida a PDF usando método alternativo.\n\n"
                               "⚠️ **Nota**: Para una mejor preservación del formato, "
                               "instala LibreOffice: `apt-get install libreoffice` o `brew install --cask libreoffice`")
            except (subprocess.TimeoutExpired, Exception):
                caption += ("📄 Presentación PowerPoint convertida a PDF usando método alternativo.\n\n"
                           "⚠️ **Nota**: Para una mejor preservación del formato, "
                           "instala LibreOffice: `apt-get install libreoffice` o `brew install --cask libreoffice`")

            # Send the converted file
            with open(output_path, 'rb') as pdf_file:
                await update.message.reply_document(
                    document=pdf_file,
                    filename=f"{document.file_name.rsplit('.', 1)[0]}.pdf",
                    caption=caption
                )

            # Clean up
            os.remove(output_path)
        else:
            await update.message.reply_text(
                "❌ **Error en la conversión**\n\n"
                "No se pudo convertir la presentación PowerPoint a PDF. "
                "Asegúrate de que el archivo no esté corrupto."
            )

        # Clean up input file
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

    except Exception as e:
        await update.message.reply_text(
            f"❌ **Error inesperado**\n\n"
            f"Ocurrió un error al procesar el archivo: {str(e)}"
        )

    # Reset state
    set_user_state(chat_id, IDLE)
