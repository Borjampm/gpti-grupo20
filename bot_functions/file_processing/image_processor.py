import os
import tempfile
from PIL import Image
import cairosvg
from pdf2image import convert_from_path

async def jpeg_to_png(input_path: str, chat_id: int) -> str:
    """Converts a JPEG image to PNG."""
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, f"png_output_{chat_id}.png")
    with Image.open(input_path) as img:
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        img.save(output_path, 'PNG')
    return output_path

async def png_to_jpeg(input_path: str, chat_id: int) -> str:
    """Converts a PNG image to JPEG."""
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
    return output_path

async def pdf_to_png(input_path: str, chat_id: int, first_page_only: bool) -> list[str]:
    """Converts PDF pages to PNG images."""
    temp_dir = tempfile.gettempdir()
    output_paths = []
    if first_page_only:
        images = convert_from_path(input_path, first_page=1, last_page=1, dpi=200)
        if images:
            output_path = os.path.join(temp_dir, f"pdf_to_png_{chat_id}.png")
            images[0].save(output_path, 'PNG')
            output_paths.append(output_path)
    else:
        images = convert_from_path(input_path, dpi=200)
        for i, image in enumerate(images, 1):
            output_path = os.path.join(temp_dir, f"pdf_to_png_{chat_id}_page_{i}.png")
            image.save(output_path, 'PNG')
            output_paths.append(output_path)
    return output_paths

async def svg_to_png(input_path: str, chat_id: int) -> str:
    """Converts an SVG image to PNG."""
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, f"svg_to_png_{chat_id}.png")
    cairosvg.svg2png(url=input_path, write_to=output_path, dpi=300)
    return output_path

async def svg_to_jpeg(input_path: str, chat_id: int) -> str:
    """Converts an SVG image to JPEG."""
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
    return output_path
