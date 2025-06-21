from telegram import Update
from telegram.ext import ContextTypes
from ..state_manager import set_user_state, IDLE, AWAITING_OPTION
from ..utils import get_exit_info_message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - welcome user and set state to IDLE"""
    chat_id = update.message.chat_id
    set_user_state(chat_id, IDLE)
    await update.message.reply_text(
        "¡Hola! 👋 Bienvenido al bot de procesamiento de archivos.\n\n"
        "🤖 **Simplemente describe lo que quieres hacer** y yo entenderé tu solicitud:\n"
        "• \"Quiero unir dos PDFs\"\n"
        "• \"Convierte esta imagen a PNG\"\n"
        "• \"Extrae las páginas 2-5 de un PDF\"\n\n"
        "📋 O usa **/manual** para ver todas las opciones numeradas.\n"
        "ℹ️ Usa **/help** para ver la lista completa de funciones disponibles."
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - show available functions list only"""
    chat_id = update.message.chat_id
    # Don't change state - keep it as informational only
    await update.message.reply_text(
        "ℹ️ **Lista de funciones disponibles:**\n\n"
        "**📄 Operaciones con PDF:**\n"
        "1. Concatenar dos archivos PDF\n"
        "2. Concatenar múltiples archivos PDF\n"
        "3. Eliminar páginas específicas de un PDF\n"
        "4. Extraer páginas específicas de un PDF\n"
        "5. Reordenar páginas de un PDF\n\n"
        "**🗜️ Operaciones con ZIP:**\n"
        "6. Crear ZIP con varios archivos\n"
        "7. Extraer archivos de un ZIP\n"
        "8. Listar contenidos de un ZIP\n"
        "9. Agregar archivos a un ZIP existente\n"
        "10. Eliminar archivos de un ZIP\n\n"
        "**🗜️ Operaciones inteligentes en ZIP:**\n"
        "11. Convertir todas las imágenes a PNG en ZIP (detecta automáticamente: JPEG, SVG)\n"
        "12. Convertir todas las imágenes a JPEG en ZIP (detecta automáticamente: PNG, SVG)\n"
        "13. Concatenar todos los PDFs dentro de un ZIP\n\n"
        "**🖼️ Conversiones inteligentes:**\n"
        "14. Imagen → PNG (detecta automáticamente: JPEG, SVG, PDF)\n"
        "15. Imagen → JPEG (detecta automáticamente: PNG, SVG, PDF)\n\n"
        "**📄 Conversiones de documentos:**\n"
        "16. Documento Word (DOCX) → PDF\n"
        "17. PDF → Documento Word (DOCX)\n"
        "18. Archivo CSV → Excel (XLSX)\n"
        "19. Archivo Excel (XLSX/XLS) → CSV\n"
        "20. Presentación PowerPoint (PPTX/PPT) → PDF\n\n"
        "💡 **Para seleccionar directamente por número, usa /manual**"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    await update.message.reply_text(
        "🤖 **Bot de Procesamiento de Archivos**\n\n"
        "Soy un bot que puede procesar archivos PDF, imágenes, documentos y ZIP de diferentes maneras:\n"
        "• Combinar y manipular archivos PDF\n"
        "• Convertir entre formatos de imagen\n"
        "• Extraer imágenes desde PDFs\n"
        "• Convertir archivos SVG\n"
        "• Convertir documentos Word, Excel y PowerPoint\n"
        "• Crear y gestionar archivos ZIP\n"
        "• Realizar operaciones en masa dentro de ZIP\n\n"
        "**Límites:**\n"
        "• Tamaño máximo por archivo: 20 MB\n"
        "• Formatos soportados: PDF, PNG, JPEG, SVG, ZIP, DOCX, XLSX, XLS, CSV, PPTX, PPT\n\n"
        "Escribe /help para ver todas las opciones disponibles."
    )

async def manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /manual command - allows direct action selection"""
    chat_id = update.message.chat_id
    set_user_state(chat_id, AWAITING_OPTION)
    exit_info = get_exit_info_message()
    await update.message.reply_text(
        f"🔧 **Modo Manual**\n\n"
        f"Envía directamente el número de la acción que deseas realizar (1-20):\n\n"
        f"**📄 Operaciones con PDF:**\n"
        f"1. Concatenar dos archivos PDF\n"
        f"2. Concatenar múltiples archivos PDF\n"
        f"3. Eliminar páginas específicas de un PDF\n"
        f"4. Extraer páginas específicas de un PDF\n"
        f"5. Reordenar páginas de un PDF\n\n"
        f"**🗜️ Operaciones con ZIP:**\n"
        f"6. Crear ZIP con varios archivos\n"
        f"7. Extraer archivos de un ZIP\n"
        f"8. Listar contenidos de un ZIP\n"
        f"9. Agregar archivos a un ZIP existente\n"
        f"10. Eliminar archivos de un ZIP\n\n"
        f"**🗜️ Operaciones inteligentes en ZIP:**\n"
        f"11. Convertir todas las imágenes a PNG en ZIP (detecta automáticamente: JPEG, SVG)\n"
        f"12. Convertir todas las imágenes a JPEG en ZIP (detecta automáticamente: PNG, SVG)\n"
        f"13. Concatenar todos los PDFs dentro de un ZIP\n\n"
        f"**🖼️ Conversiones inteligentes:**\n"
        f"14. Imagen → PNG (detecta automáticamente: JPEG, SVG, PDF)\n"
        f"15. Imagen → JPEG (detecta automáticamente: PNG, SVG, PDF)\n\n"
        f"**📄 Conversiones de documentos:**\n"
        f"16. Documento Word (DOCX) → PDF\n"
        f"17. PDF → Documento Word (DOCX)\n"
        f"18. Archivo CSV → Excel (XLSX)\n"
        f"19. Archivo Excel (XLSX/XLS) → CSV\n"
        f"20. Presentación PowerPoint (PPTX/PPT) → PDF\n\n{exit_info}"
    )


