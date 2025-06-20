from telegram import Update
from telegram.ext import ContextTypes
from ..state_manager import set_user_state, IDLE, AWAITING_OPTION

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - welcome user and set state to IDLE"""
    chat_id = update.message.chat_id
    set_user_state(chat_id, IDLE)
    await update.message.reply_text("¡Hola! Bienvenido al bot. Escribe /help para comenzar.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - show menu and set state to AWAITING_OPTION"""
    chat_id = update.message.chat_id
    set_user_state(chat_id, AWAITING_OPTION)
    await update.message.reply_text(
        "🤖 **Elige una opción escribiendo solo el número correspondiente:**\n\n"
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
        "16. Eliminar archivos de un ZIP\n"
        "17. Operaciones en masa dentro de un ZIP\n\n"
        "**✨ Inteligencia Artificial:**\n"
        "18. Hablar con un LLM (Gemini)\n"
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


