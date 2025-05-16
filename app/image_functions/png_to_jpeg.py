import os
from PIL import Image

def png_to_jpeg(input_png_paths, output_dir, quality=85):
    """
    Converts one or more PNG images to JPEG format.

    Args:
        input_png_paths (list): List of PNG file paths to convert.
        output_dir (str): Directory to save the JPEG images.
        quality (int): JPEG quality (default: 85).

    Returns:
        list: List of output JPEG file paths.
    """
    if not input_png_paths:
        print("No PNG files provided for conversion.")
        return []

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_files = []
    for png_path in input_png_paths:
        if not os.path.exists(png_path):
            print(f"File not found: {png_path}")
            continue
        try:
            img = Image.open(png_path)
            rgb_img = img.convert('RGB')
            base_name = os.path.splitext(os.path.basename(png_path))[0]
            output_file = os.path.join(output_dir, f"{base_name}.jpg")
            rgb_img.save(output_file, "JPEG", quality=quality)
            output_files.append(output_file)
            print(f"Converted '{png_path}' to '{output_file}'")
        except Exception as e:
            print(f"Error converting '{png_path}' to JPEG: {e}")
    return output_files

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python png_to_jpeg.py <output_dir> <input_png1> [<input_png2> ...]")
        sys.exit(1)
    output_dir = sys.argv[1]
    input_pngs = sys.argv[2:]
    png_to_jpeg(input_pngs, output_dir)
