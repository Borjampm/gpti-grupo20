import os
from pdf2image import convert_from_path

def pdf_to_png(input_pdf_path, output_dir, dpi=200):
    """
    Converts each page of a PDF file to a PNG image.

    Args:
        input_pdf_path (str): Path to the input PDF file.
        output_dir (str): Directory to save the PNG images.
        dpi (int): Resolution for the output images (default: 200).

    Returns:
        list: List of output PNG file paths.
    """
    if not os.path.exists(input_pdf_path):
        print(f"Error: Input PDF '{input_pdf_path}' not found.")
        return []

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        images = convert_from_path(input_pdf_path, dpi=dpi)
        output_files = []
        base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
        for i, image in enumerate(images):
            output_file = os.path.join(output_dir, f"{base_name}_page_{i+1}.png")
            image.save(output_file, "PNG")
            output_files.append(output_file)
        print(f"Converted {len(output_files)} page(s) to PNG in '{output_dir}'.")
        return output_files
    except Exception as e:
        print(f"Error converting PDF to PNG: {e}")
        return []

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python pdf_to_png.py <input_pdf_path> <output_dir> [dpi]")
        sys.exit(1)
    input_pdf = sys.argv[1]
    output_dir = sys.argv[2]
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    pdf_to_png(input_pdf, output_dir, dpi)
