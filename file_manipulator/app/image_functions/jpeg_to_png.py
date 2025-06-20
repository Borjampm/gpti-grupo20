import os
from PIL import Image

def jpeg_to_png(input_jpeg_paths, output_dir):
    """
    Converts one or more JPEG images to PNG format.

    Args:
        input_jpeg_paths (list): List of JPEG file paths to convert.
        output_dir (str): Directory to save the PNG images.

    Returns:
        list: List of output PNG file paths.
    """
    if not input_jpeg_paths:
        print("No JPEG files provided for conversion.")
        return []

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_files = []
    for jpeg_path in input_jpeg_paths:
        if not os.path.exists(jpeg_path):
            print(f"File not found: {jpeg_path}")
            continue
        try:
            img = Image.open(jpeg_path)
            base_name = os.path.splitext(os.path.basename(jpeg_path))[0]
            output_file = os.path.join(output_dir, f"{base_name}.png")
            img.save(output_file, "PNG")
            output_files.append(output_file)
            print(f"Converted '{jpeg_path}' to '{output_file}'")
        except Exception as e:
            print(f"Error converting '{jpeg_path}' to PNG: {e}")
    return output_files

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python jpeg_to_png.py <output_dir> <input_jpeg1> [<input_jpeg2> ...]")
        sys.exit(1)
    output_dir = sys.argv[1]
    input_jpegs = sys.argv[2:]
    jpeg_to_png(input_jpegs, output_dir)
