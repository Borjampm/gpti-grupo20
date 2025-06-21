import os
import tempfile
from PIL import Image
import cairosvg
from pdf2image import convert_from_path

async def transform_to_png(input_path: str, chat_id: int, source_extension: str) -> tuple[str, bool]:
    """
    Converts any supported image format to PNG.
    Returns (output_path, is_multiple_files) where is_multiple_files is True for PDF with multiple pages.
    """
    source_extension = source_extension.lower()

    if source_extension in ['jpg', 'jpeg']:
        # JPEG to PNG
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"png_output_{chat_id}.png")
        with Image.open(input_path) as img:
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            img.save(output_path, 'PNG')
        return output_path, False
    elif source_extension == 'svg':
        # SVG to PNG
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"svg_to_png_{chat_id}.png")
        cairosvg.svg2png(url=input_path, write_to=output_path, dpi=300)
        return output_path, False
    elif source_extension == 'pdf':
        # PDF to PNG (all pages)
        temp_dir = tempfile.gettempdir()
        output_paths = []
        images = convert_from_path(input_path, dpi=200)
        for i, image in enumerate(images, 1):
            output_path = os.path.join(temp_dir, f"pdf_to_png_{chat_id}_page_{i}.png")
            image.save(output_path, 'PNG')
            output_paths.append(output_path)
        return output_paths, True
    else:
        raise ValueError(f"Extensión no soportada para conversión a PNG: {source_extension}")

async def transform_to_jpeg(input_path: str, chat_id: int, source_extension: str) -> tuple[str, bool]:
    """
    Converts any supported image format to JPEG.
    Returns (output_path, is_multiple_files) where is_multiple_files is True for PDF with multiple pages.
    """
    source_extension = source_extension.lower()

    if source_extension == 'png':
        # PNG to JPEG
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"jpeg_output_{chat_id}.jpg")
        with Image.open(input_path) as img:
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode == 'P':
                img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=95)
        return output_path, False
    elif source_extension == 'svg':
        # SVG to JPEG
        temp_dir = tempfile.gettempdir()
        png_path = os.path.join(temp_dir, f"svg_to_png_temp_{chat_id}.png")
        output_path = os.path.join(temp_dir, f"svg_to_jpeg_{chat_id}.jpg")
        cairosvg.svg2png(url=input_path, write_to=png_path, dpi=300)
        with Image.open(png_path) as img:
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            img.save(output_path, 'JPEG', quality=95)
        os.remove(png_path)
        return output_path, False
    elif source_extension == 'pdf':
        # PDF to JPEG (all pages)
        temp_dir = tempfile.gettempdir()
        # First convert to PNG then to JPEG
        images = convert_from_path(input_path, dpi=200)
        jpeg_paths = []

        for i, image in enumerate(images, 1):
            jpeg_path = os.path.join(temp_dir, f"pdf_to_jpeg_{chat_id}_page_{i}.jpg")
            # Convert PIL image directly to JPEG
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            image.save(jpeg_path, 'JPEG', quality=95)
            jpeg_paths.append(jpeg_path)

        return jpeg_paths, True
    else:
        raise ValueError(f"Extensión no soportada para conversión a JPEG: {source_extension}")
