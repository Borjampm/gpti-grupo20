from telegram import Update
from telegram.ext import ContextTypes
from ..state_manager import set_user_state, IDLE, AWAITING_OPTION

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
        "**🖼️ Conversiones de imagen:**\n"
        "6. JPEG → PNG\n"
        "7. PNG → JPEG\n"
        "8. PDF → PNG (primera página)\n"
        "9. PDF → PNG (todas las páginas)\n"
        "10. SVG → PNG\n"
        "11. SVG → JPEG\n\n"
        "**🗜️ Operaciones con ZIP:**\n"
        "12. Crear ZIP con varios archivos\n"
        "13. Extraer archivos de un ZIP\n"
        "14. Listar contenidos de un ZIP\n"
        "15. Agregar archivos a un ZIP existente\n"
        "16. Eliminar archivos de un ZIP\n\n"
        "**🗜️ Operaciones masivas en ZIP:**\n"
        "17. Convertir todas las imágenes PNG a JPEG dentro de un ZIP\n"
        "18. Convertir todas las imágenes JPEG a PNG dentro de un ZIP\n"
        "19. Convertir todos los archivos SVG a PNG dentro de un ZIP\n"
        "20. Convertir todos los archivos SVG a JPEG dentro de un ZIP\n"
        "21. Concatenar todos los PDFs dentro de un ZIP\n\n"
        "💡 **Para seleccionar directamente por número, usa /manual**"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    await update.message.reply_text(
        "🤖 **Bot de Procesamiento de Archivos**\n\n"
        "Soy un bot que puede procesar archivos PDF, imágenes y ZIP de diferentes maneras:\n"
        "• Combinar y manipular archivos PDF\n"
        "• Convertir entre formatos de imagen\n"
        "• Extraer imágenes desde PDFs\n"
        "• Convertir archivos SVG\n"
        "• Crear y gestionar archivos ZIP\n"
        "• Realizar operaciones en masa dentro de ZIP\n\n"
        "**Límites:**\n"
        "• Tamaño máximo por archivo: 20 MB\n"
        "• Formatos soportados: PDF, PNG, JPEG, SVG, ZIP\n\n"
        "Escribe /help para ver todas las opciones disponibles."
    )

async def manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /manual command - allows direct action selection"""
    chat_id = update.message.chat_id
    set_user_state(chat_id, AWAITING_OPTION)
    await update.message.reply_text(
        "🔧 **Modo Manual**\n\n"
        "Envía directamente el número de la acción que deseas realizar (1-21):\n\n"
        "**📄 Operaciones con PDF:**\n"
        "1. Concatenar dos archivos PDF\n"
        "2. Concatenar múltiples archivos PDF\n"
        "3. Eliminar páginas específicas de un PDF\n"
        "4. Extraer páginas específicas de un PDF\n"
        "5. Reordenar páginas de un PDF\n\n"
        "**🖼️ Conversiones de imagen:**\n"
        "6. JPEG → PNG\n"
        "7. PNG → JPEG\n"
        "8. PDF → PNG (primera página)\n"
        "9. PDF → PNG (todas las páginas)\n"
        "10. SVG → PNG\n"
        "11. SVG → JPEG\n\n"
        "**🗜️ Operaciones con ZIP:**\n"
        "12. Crear ZIP con varios archivos\n"
        "13. Extraer archivos de un ZIP\n"
        "14. Listar contenidos de un ZIP\n"
        "15. Agregar archivos a un ZIP existente\n"
        "16. Eliminar archivos de un ZIP\n\n"
        "**🗜️ Operaciones masivas en ZIP:**\n"
        "17. Convertir todas las imágenes PNG a JPEG dentro de un ZIP\n"
        "18. Convertir todas las imágenes JPEG a PNG dentro de un ZIP\n"
        "19. Convertir todos los archivos SVG a PNG dentro de un ZIP\n"
        "20. Convertir todos los archivos SVG a JPEG dentro de un ZIP\n"
        "21. Concatenar todos los PDFs dentro de un ZIP\n"
    )


