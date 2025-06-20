import os
from PIL import Image

def pngs_to_pdf(input_png_paths, output_pdf_path):
    """
    Converts one or more PNG images to a single PDF file.

    Args:
        input_png_paths (list): List of PNG file paths to convert.
        output_pdf_path (str): Path to save the output PDF file.

    Returns:
        bool: True if successful, False otherwise.
    """
    if not input_png_paths:
        print("No PNG files provided for conversion.")
        return False

    images = []
    for png_path in input_png_paths:
        if not os.path.exists(png_path):
            print(f"File not found: {png_path}")
            return False
        img = Image.open(png_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)

    try:
        images[0].save(output_pdf_path, save_all=True, append_images=images[1:])
        print(f"Saved PDF to '{output_pdf_path}' with {len(images)} page(s).")
        return True
    except Exception as e:
        print(f"Error converting PNGs to PDF: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python png_to_pdf.py <output_pdf_path> <input_png1> [<input_png2> ...]")
        sys.exit(1)
    output_pdf = sys.argv[1]
    input_pngs = sys.argv[2:]
    pngs_to_pdf(input_pngs, output_pdf)
