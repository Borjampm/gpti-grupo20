import os
import tempfile
import zipfile
import shutil
from PIL import Image
import cairosvg
from .pdf_processor import concatenate_multiple_pdfs

async def create_zip_from_files(file_paths: list, chat_id: int) -> str:
    """Create a ZIP file from multiple files"""
    try:
        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, f"created_{chat_id}.zip")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in file_paths:
                filename = os.path.basename(file_path)
                zip_file.write(file_path, filename)

        return zip_path
    except Exception as e:
        print(f"Error creating ZIP: {e}")
        return None

async def add_files_to_zip(zip_path: str, files_to_add: list, chat_id: int) -> str:
    """Add files to an existing ZIP"""
    try:
        temp_dir = tempfile.gettempdir()
        new_zip_path = os.path.join(temp_dir, f"updated_{chat_id}.zip")

        with zipfile.ZipFile(zip_path, 'r') as original_zip:
            with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                # Copy existing files
                for item in original_zip.namelist():
                    data = original_zip.read(item)
                    new_zip.writestr(item, data)

                # Add new files
                for file_path in files_to_add:
                    filename = os.path.basename(file_path)
                    new_zip.write(file_path, filename)

        return new_zip_path
    except Exception as e:
        print(f"Error adding files to ZIP: {e}")
        return None

async def remove_files_from_zip(zip_path: str, files_to_remove: list, chat_id: int) -> str:
    """Remove files from an existing ZIP"""
    try:
        temp_dir = tempfile.gettempdir()
        new_zip_path = os.path.join(temp_dir, f"filtered_{chat_id}.zip")

        with zipfile.ZipFile(zip_path, 'r') as original_zip:
            with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                for item in original_zip.namelist():
                    if item not in files_to_remove:
                        data = original_zip.read(item)
                        new_zip.writestr(item, data)

        return new_zip_path
    except Exception as e:
        print(f"Error removing files from ZIP: {e}")
        return None

async def perform_bulk_operation_with_order(zip_path: str, files: list, operation: int, chat_id: int, ordered_pdf_files: list) -> str:
    """Perform bulk operations on files in ZIP with custom PDF order"""
    try:
        temp_dir = tempfile.gettempdir()
        extract_dir = os.path.join(temp_dir, f"bulk_extract_{chat_id}")
        new_zip_path = os.path.join(temp_dir, f"bulk_processed_{chat_id}.zip")

        # Extract ZIP
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
            # For operation 3 (PDF concatenation), use the ordered list
            if operation == 3 and ordered_pdf_files:
                processed_files = []

                # Collect PDF files in the specified order
                for pdf_filename in ordered_pdf_files:
                    file_path = os.path.join(extract_dir, pdf_filename)
                    if os.path.exists(file_path):
                        processed_files.append(file_path)

                # Concatenate PDFs in order
                if len(processed_files) > 1:
                    try:
                        concatenated_path = await concatenate_multiple_pdfs(processed_files, chat_id)
                        if concatenated_path:
                            new_zip.write(concatenated_path, f"concatenated_pdfs_{chat_id}.pdf")
                            os.remove(concatenated_path)
                        else:
                            # If concatenation fails, add individual PDFs in order
                            for pdf_path in processed_files:
                                filename = os.path.basename(pdf_path)
                                new_zip.write(pdf_path, filename)
                    except Exception:
                        # If concatenation fails, add individual PDFs in order
                        for pdf_path in processed_files:
                            filename = os.path.basename(pdf_path)
                            new_zip.write(pdf_path, filename)

                # Add all non-PDF files (excluding metadata files)
                for filename in files:
                    # Skip macOS metadata files
                    if filename.startswith('__MACOSX/') or filename.startswith('._') or '/__MACOSX/' in filename or '/._' in filename:
                        continue

                    if not filename.lower().endswith('.pdf'):
                        file_path = os.path.join(extract_dir, filename)
                        if os.path.exists(file_path):
                            new_zip.write(file_path, filename)

        # Clean up extraction directory
        shutil.rmtree(extract_dir)

        return new_zip_path
    except Exception as e:
        print(f"Error in bulk operation with order: {e}")
        return None

async def perform_bulk_operation(zip_path: str, files: list, operation: int, chat_id: int) -> str:
    """Perform bulk operations on files in ZIP"""
    try:
        temp_dir = tempfile.gettempdir()
        extract_dir = os.path.join(temp_dir, f"bulk_extract_{chat_id}")
        new_zip_path = os.path.join(temp_dir, f"bulk_processed_{chat_id}.zip")

        # Extract ZIP
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Process files based on operation
        processed_files = []

        with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
            for filename in files:
                # Skip macOS metadata files
                if filename.startswith('__MACOSX/') or filename.startswith('._') or '/__MACOSX/' in filename or '/._' in filename:
                    continue

                file_path = os.path.join(extract_dir, filename)

                if not os.path.exists(file_path):
                    continue

                processed = False

                if operation == 1:
                    # Convert all images to PNG (JPEG and SVG)
                    file_ext = filename.lower().split('.')[-1]

                    if file_ext in ['jpg', 'jpeg']:
                        # JPEG to PNG
                        try:
                            with Image.open(file_path) as img:
                                if img.mode in ('RGBA', 'LA'):
                                    background = Image.new('RGB', img.size, (255, 255, 255))
                                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                                    img = background
                                new_filename = filename.rsplit('.', 1)[0] + '.png'
                                new_file_path = os.path.join(extract_dir, new_filename)
                                img.save(new_file_path, 'PNG')
                                new_zip.write(new_file_path, new_filename)
                                processed = True
                        except Exception:
                            pass

                    elif file_ext == 'svg':
                        # SVG to PNG
                        try:
                            new_filename = filename.rsplit('.', 1)[0] + '.png'
                            new_file_path = os.path.join(extract_dir, new_filename)
                            cairosvg.svg2png(url=file_path, write_to=new_file_path, dpi=300)
                            new_zip.write(new_file_path, new_filename)
                            processed = True
                        except Exception:
                            pass

                elif operation == 2:
                    # Convert all images to JPEG (PNG and SVG)
                    file_ext = filename.lower().split('.')[-1]

                    if file_ext == 'png':
                        # PNG to JPEG
                        try:
                            with Image.open(file_path) as img:
                                if img.mode in ('RGBA', 'LA'):
                                    background = Image.new('RGB', img.size, (255, 255, 255))
                                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                                    img = background
                                elif img.mode == 'P':
                                    img = img.convert('RGB')
                                new_filename = filename.rsplit('.', 1)[0] + '.jpg'
                                new_file_path = os.path.join(extract_dir, new_filename)
                                img.save(new_file_path, 'JPEG', quality=95)
                                new_zip.write(new_file_path, new_filename)
                                processed = True
                        except Exception:
                            pass

                    elif file_ext == 'svg':
                        # SVG to JPEG
                        try:
                            png_path = os.path.join(extract_dir, f"temp_{filename}.png")
                            new_filename = filename.rsplit('.', 1)[0] + '.jpg'
                            new_file_path = os.path.join(extract_dir, new_filename)

                            cairosvg.svg2png(url=file_path, write_to=png_path, dpi=300)
                            with Image.open(png_path) as img:
                                if img.mode in ('RGBA', 'LA'):
                                    background = Image.new('RGB', img.size, (255, 255, 255))
                                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                                    img = background
                                img.save(new_file_path, 'JPEG', quality=95)

                            new_zip.write(new_file_path, new_filename)
                            os.remove(png_path)
                            processed = True
                        except Exception:
                            pass

                elif operation == 3 and filename.lower().endswith('.pdf'):
                    # Collect PDFs for concatenation (renumbered from 5 to 3)
                    processed_files.append(file_path)
                    continue

                # If not processed, keep original file
                if not processed:
                    new_zip.write(file_path, filename)

            # Handle PDF concatenation if operation 3
            if operation == 3 and len(processed_files) > 1:
                try:
                    concatenated_path = await concatenate_multiple_pdfs(processed_files, chat_id)
                    if concatenated_path:
                        new_zip.write(concatenated_path, f"concatenated_pdfs_{chat_id}.pdf")
                        os.remove(concatenated_path)
                except Exception:
                    # If concatenation fails, add individual PDFs
                    for pdf_path in processed_files:
                        filename = os.path.basename(pdf_path)
                        new_zip.write(pdf_path, filename)

        # Clean up extraction directory
        shutil.rmtree(extract_dir)

        return new_zip_path
    except Exception as e:
        print(f"Error in bulk operation: {e}")
        return None
