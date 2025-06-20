import os
import tempfile
import zipfile
import shutil
from telegram import Update
from ..state_manager import (
    set_user_state, get_user_data, clear_user_data,
    AWAITING_OPTION, AWAITING_MULTIPLE_FILES_FOR_ZIP, AWAITING_FILES_TO_ADD,
    AWAITING_FILENAMES_TO_REMOVE, AWAITING_BULK_OPERATION, AWAITING_PDF_CONCATENATION_ORDER
)
from ..utils import validate_file, send_processing_and_ad_message, filter_valid_files
from ..file_processing.zip_processor import (
    create_zip_from_files, add_files_to_zip, remove_files_from_zip,
    perform_bulk_operation
)
from ..file_processing.zip_processor import perform_bulk_operation_with_order as pb_with_order

async def handle_multiple_files_for_zip(update: Update, chat_id: int):
    """Handle multiple file uploads for ZIP creation"""
    if update.message.text and update.message.text.lower() == "listo":
        file_paths = get_user_data(chat_id, 'file_paths', [])
        if len(file_paths) < 2:
            await update.message.reply_text("Necesitas enviar al menos 2 archivos para crear un ZIP.")
            return

        await send_processing_and_ad_message(update, f"🔄 Creando ZIP con {len(file_paths)} archivos...")

        try:
            zip_path = await create_zip_from_files(file_paths, chat_id)
            if zip_path:
                with open(zip_path, 'rb') as zip_file:
                    await update.message.reply_document(
                        document=zip_file,
                        filename=f"archivos_combinados_{chat_id}.zip",
                        caption="✅ ZIP creado exitosamente!"
                    )
                os.remove(zip_path)
            else:
                await update.message.reply_text("❌ Error al crear el ZIP.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error al crear el ZIP: {str(e)}")

        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)

        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")
        return

    if not update.message.document:
        await update.message.reply_text("Por favor, envía un archivo o escribe 'listo' cuando hayas terminado.")
        return

    is_valid, message = await validate_file(update, ['pdf', 'png', 'jpg', 'jpeg', 'svg', 'txt', 'docx', 'xlsx'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        file_path = os.path.join(temp_dir, f"zip_file_{chat_id}_{len(get_user_data(chat_id, 'file_paths', []))}_{file_name}")

        await file.download_to_drive(file_path)

        file_paths = get_user_data(chat_id, 'file_paths', [])
        file_paths.append(file_path)
        set_user_state(chat_id, AWAITING_MULTIPLE_FILES_FOR_ZIP, file_paths=file_paths)

        await update.message.reply_text(f"✅ Archivo {len(file_paths)} recibido: {file_name}\n\nEnvía más archivos o escribe 'listo' para crear el ZIP.")

    except Exception as e:
        await update.message.reply_text(f"Error al recibir el archivo: {str(e)}")

async def handle_zip_extraction(update: Update, chat_id: int):
    """Handle ZIP file extraction"""
    is_valid, message = await validate_file(update, ['zip'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        zip_path = os.path.join(temp_dir, f"zip_to_extract_{chat_id}_{file_name}")

        await file.download_to_drive(zip_path)

        await send_processing_and_ad_message(update, "🔄 Extrayendo archivos del ZIP...")

        extract_dir = os.path.join(temp_dir, f"extracted_{chat_id}")
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        files_sent = 0
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.startswith('._') or '__MACOSX' in root:
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as extracted_file:
                        await update.message.reply_document(
                            document=extracted_file,
                            filename=file,
                            caption=f"📄 Archivo extraído: {file}"
                        )
                    files_sent += 1
                except Exception as e:
                    await update.message.reply_text(f"❌ No se pudo enviar {file}: {str(e)}")

        await update.message.reply_text(f"✅ Extracción completada. {files_sent} archivos enviados.")

        os.remove(zip_path)
        shutil.rmtree(extract_dir)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error al extraer el ZIP: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_zip_listing(update: Update, chat_id: int):
    """Handle ZIP file content listing"""
    is_valid, message = await validate_file(update, ['zip'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        zip_path = os.path.join(temp_dir, f"zip_to_list_{chat_id}_{file_name}")

        await file.download_to_drive(zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            all_files = zip_ref.namelist()
            valid_files = filter_valid_files(all_files)
            info_list = []

            for file_name in valid_files:
                info = zip_ref.getinfo(file_name)
                size_mb = info.file_size / (1024 * 1024)
                info_list.append(f"📄 {file_name} ({size_mb:.2f} MB)")

        if info_list:
            content_text = "📋 **Contenido del ZIP:**\n\n" + "\n".join(info_list)
            content_text += f"\n\n📊 **Total: {len(valid_files)} archivos**"
        else:
            content_text = "📋 El archivo ZIP no contiene archivos válidos."

        await update.message.reply_text(content_text)

        os.remove(zip_path)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error al listar el contenido del ZIP: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_zip_for_add(update: Update, chat_id: int):
    """Handle ZIP file for adding files"""
    is_valid, message = await validate_file(update, ['zip'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        zip_path = os.path.join(temp_dir, f"zip_for_add_{chat_id}_{file_name}")

        await file.download_to_drive(zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            all_files = zip_ref.namelist()
            current_files = filter_valid_files(all_files)

        set_user_state(chat_id, AWAITING_FILES_TO_ADD, zip_path=zip_path, files_to_add=[])
        await update.message.reply_text(
            f"✅ ZIP recibido con {len(current_files)} archivos.\n\n"
            "Ahora envíame los archivos que quieres agregar uno por uno. "
            "Cuando hayas terminado, escribe 'listo'."
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error al procesar el ZIP: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_files_to_add(update: Update, chat_id: int):
    """Handle files to add to existing ZIP"""
    if update.message.text and update.message.text.lower() == "listo":
        files_to_add = get_user_data(chat_id, 'files_to_add', [])
        if not files_to_add:
            await update.message.reply_text("No has enviado ningún archivo para agregar.")
            return

        zip_path = get_user_data(chat_id, 'zip_path')

        await send_processing_and_ad_message(update, f"🔄 Agregando {len(files_to_add)} archivos al ZIP...")

        try:
            new_zip_path = await add_files_to_zip(zip_path, files_to_add, chat_id)
            if new_zip_path:
                with open(new_zip_path, 'rb') as new_zip_file:
                    await update.message.reply_document(
                        document=new_zip_file,
                        filename=f"zip_actualizado_{chat_id}.zip",
                        caption=f"✅ ZIP actualizado con {len(files_to_add)} archivos nuevos!"
                    )
                os.remove(new_zip_path)
            else:
                await update.message.reply_text("❌ Error al agregar archivos al ZIP.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error al agregar archivos: {str(e)}")

        if os.path.exists(zip_path):
            os.remove(zip_path)
        for file_path in files_to_add:
            if os.path.exists(file_path):
                os.remove(file_path)

        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")
        return

    if not update.message.document:
        await update.message.reply_text("Por favor, envía un archivo o escribe 'listo' cuando hayas terminado.")
        return

    is_valid, message = await validate_file(update, ['pdf', 'png', 'jpg', 'jpeg', 'svg', 'txt', 'docx', 'xlsx', 'zip'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        file_path = os.path.join(temp_dir, f"add_file_{chat_id}_{len(get_user_data(chat_id, 'files_to_add', []))}_{file_name}")

        await file.download_to_drive(file_path)

        files_to_add = get_user_data(chat_id, 'files_to_add', [])
        files_to_add.append(file_path)
        set_user_state(chat_id, AWAITING_FILES_TO_ADD, files_to_add=files_to_add)

        await update.message.reply_text(f"✅ Archivo recibido: {file_name}\n\nEnvía más archivos o escribe 'listo' para agregarlos al ZIP.")

    except Exception as e:
        await update.message.reply_text(f"Error al recibir el archivo: {str(e)}")

async def handle_zip_for_remove(update: Update, chat_id: int):
    """Handle ZIP file for removing files"""
    is_valid, message = await validate_file(update, ['zip'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        zip_path = os.path.join(temp_dir, f"zip_for_remove_{chat_id}_{file_name}")

        await file.download_to_drive(zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            all_files = zip_ref.namelist()
            current_files = filter_valid_files(all_files)

        if not current_files:
            await update.message.reply_text("❌ El ZIP está vacío.")
            os.remove(zip_path)
            set_user_state(chat_id, AWAITING_OPTION)
            return

        files_list = "\n".join([f"{i+1}. {file}" for i, file in enumerate(current_files)])

        set_user_state(chat_id, AWAITING_FILENAMES_TO_REMOVE, zip_path=zip_path, current_files=current_files)
        await update.message.reply_text(
            f"📋 **Archivos en el ZIP:**\n\n{files_list}\n\n"
            "Envía los números de los archivos que quieres eliminar, separados por comas (ej: 1,3,5) "
            "o envía los nombres exactos de los archivos separados por comas."
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error al procesar el ZIP: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_filenames_to_remove(update: Update, chat_id: int):
    """Handle filenames to remove from ZIP"""
    if not update.message.text:
        await update.message.reply_text("Por favor, envía los números o nombres de los archivos a eliminar.")
        return

    try:
        zip_path = get_user_data(chat_id, 'zip_path')
        current_files = get_user_data(chat_id, 'current_files', [])
        user_input = update.message.text.strip()

        files_to_remove = []

        if user_input.replace(',', '').replace(' ', '').isdigit():
            indices = [int(x.strip()) - 1 for x in user_input.split(',') if x.strip().isdigit()]
            for idx in indices:
                if 0 <= idx < len(current_files):
                    files_to_remove.append(current_files[idx])
        else:
            requested_files = [x.strip() for x in user_input.split(',')]
            for filename in requested_files:
                if filename in current_files:
                    files_to_remove.append(filename)

        if not files_to_remove:
            await update.message.reply_text("❌ No se encontraron archivos válidos para eliminar.")
            return

        await send_processing_and_ad_message(update, f"🔄 Eliminando {len(files_to_remove)} archivos del ZIP...")

        new_zip_path = await remove_files_from_zip(zip_path, files_to_remove, chat_id)
        if new_zip_path:
            with open(new_zip_path, 'rb') as new_zip_file:
                await update.message.reply_document(
                    document=new_zip_file,
                    filename=f"zip_actualizado_{chat_id}.zip",
                    caption=f"✅ ZIP actualizado. Eliminados {len(files_to_remove)} archivos."
                )
            os.remove(new_zip_path)
        else:
            await update.message.reply_text("❌ Error al eliminar archivos del ZIP.")

        if os.path.exists(zip_path):
            os.remove(zip_path)

        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error al eliminar archivos: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_zip_for_bulk(update: Update, chat_id: int):
    """Handle ZIP file for bulk operations"""
    is_valid, message = await validate_file(update, ['zip'])
    if not is_valid:
        await update.message.reply_text(message)
        return

    try:
        file = await update.message.document.get_file()
        temp_dir = tempfile.gettempdir()
        file_name = update.message.document.file_name
        zip_path = os.path.join(temp_dir, f"zip_for_bulk_{chat_id}_{file_name}")

        await file.download_to_drive(zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            all_files = zip_ref.namelist()
            current_files = filter_valid_files(all_files)

        if not current_files:
            await update.message.reply_text("❌ El ZIP no contiene archivos válidos.")
            os.remove(zip_path)
            set_user_state(chat_id, AWAITING_OPTION)
            return

        pdf_files = [f for f in current_files if f.lower().endswith('.pdf')]
        image_files = [f for f in current_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg'))]

        set_user_state(chat_id, AWAITING_BULK_OPERATION, zip_path=zip_path, current_files=current_files)

        options_text = (
            "🗜️ **Operaciones en masa disponibles:**\n\n"
            "1. **Convertir imágenes PNG → JPEG**\n"
            "2. **Convertir imágenes JPEG → PNG**\n"
            "3. **Convertir SVG → PNG**\n"
            "4. **Convertir SVG → JPEG**\n"
        )

        if len(pdf_files) > 1:
            options_text += "5. **Concatenar todos los PDFs**\n"

        options_text += f"\n📊 **Archivos detectados:**\n"
        options_text += f"• PDFs: {len(pdf_files)}\n"
        options_text += f"• Imágenes: {len(image_files)}\n"
        options_text += f"• Otros: {len(current_files) - len(pdf_files) - len(image_files)}\n\n"
        options_text += "Envía el número de la operación que quieres realizar:"

        await update.message.reply_text(options_text)

    except Exception as e:
        await update.message.reply_text(f"❌ Error al procesar el ZIP: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)

async def handle_bulk_operation(update: Update, chat_id: int):
    """Handle bulk operation selection and execution"""
    if not update.message.text or not update.message.text.strip().isdigit():
        await update.message.reply_text("Por favor, envía el número de la operación deseada.")
        return

    try:
        operation = int(update.message.text.strip())
        zip_path = get_user_data(chat_id, 'zip_path')
        current_files = get_user_data(chat_id, 'current_files', [])

        if operation == 5:
            pdf_files = [f for f in current_files if f.lower().endswith('.pdf')]

            if len(pdf_files) < 2:
                await update.message.reply_text("❌ Se necesitan al menos 2 archivos PDF para concatenar.")
                return
            elif len(pdf_files) == 2:
                await send_processing_and_ad_message(update, "🔄 Concatenando 2 archivos PDF...")
                new_zip_path = await perform_bulk_operation(zip_path, current_files, operation, chat_id)
            else:
                pdf_list = "\n".join([f"{i+1}. {pdf}" for i, pdf in enumerate(pdf_files)])

                set_user_state(chat_id, AWAITING_PDF_CONCATENATION_ORDER,
                             zip_path=zip_path,
                             current_files=current_files,
                             pdf_files=pdf_files,
                             operation=operation)

                await update.message.reply_text(
                    f"📋 **Se encontraron {len(pdf_files)} archivos PDF:**\n\n{pdf_list}\n\n"
                    f"📝 **Especifica el orden para concatenar los PDFs**\n"
                    f"Envía los números separados por comas (ejemplo: 2,1,3)\n"
                    f"Esto concatenará el archivo 2 primero, luego el 1, luego el 3."
                )
                return
        else:
            await send_processing_and_ad_message(update, "🔄 Realizando operación en masa...")
            new_zip_path = await perform_bulk_operation(zip_path, current_files, operation, chat_id)

        if new_zip_path:
            with open(new_zip_path, 'rb') as new_zip_file:
                await update.message.reply_document(
                    document=new_zip_file,
                    filename=f"zip_procesado_{chat_id}.zip",
                    caption="✅ Operación en masa completada!"
                )
            os.remove(new_zip_path)
        else:
            await update.message.reply_text("❌ Error al realizar la operación en masa.")

        if os.path.exists(zip_path):
            os.remove(zip_path)

        clear_user_data(chat_id)
        set_user_state(chat_id, AWAITING_OPTION)
        await update.message.reply_text("Puedes elegir otra opción o escribir /help para ver el menú.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error en la operación: {str(e)}")
        set_user_state(chat_id, AWAITING_OPTION)
