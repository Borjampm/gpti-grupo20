import os
import sys # We'll use this for path joining, and adapt exit calls
from .pdf_functions.pdf_merger import merge_pdfs
from .pdf_functions.pdf_page_deleter import delete_pdf_pages
from .pdf_functions.pdf_to_png import pdf_to_png
from .image_functions.png_to_pdf import pngs_to_pdf
from .image_functions.png_to_jpeg import png_to_jpeg
from .image_functions.jpeg_to_png import jpeg_to_png
# You can import other functions from other .py files in the 'app' directory similarly
# from .another_module import another_function

def run_pdf_merger_logic():
    """
    Handles the PDF merging process, including listing files,
    getting user input, and calling the merge_pdfs function.
    """
    print("\nPDF Merging selected.")

    source_directory = "files"  # Define the source directory for PDFs
    output_directory = "results"

    if not os.path.exists(source_directory) or not os.path.isdir(source_directory):
        print(f"Error: Source directory '{source_directory}' not found or is not a directory.")
        print(f"Please create a '{source_directory}' folder and place your PDF files inside it.")
        return

    available_pdfs = [f for f in os.listdir(source_directory) if f.lower().endswith(".pdf")]

    if not available_pdfs:
        print(f"No PDF files found in the '{source_directory}' directory.")
        return

    print("\nAvailable PDF files for merging:")
    for i, pdf_name in enumerate(available_pdfs):
        print(f"  {i + 1}. {pdf_name}")

    selected_files_indices = []
    pdf_list = []

    print("\nEnter the numbers of the PDF files you want to merge, separated by commas (e.g., 1,3,4).")
    print("Or type 'all' to select all files.")
    while True:
        try:
            user_input = input("Select files to merge: ").strip()
            if user_input.lower() == 'all':
                selected_files_indices = list(range(len(available_pdfs)))
                break

            selected_files_indices = [int(x.strip()) - 1 for x in user_input.split(',')]
            if not all(0 <= idx < len(available_pdfs) for idx in selected_files_indices):
                raise ValueError("Invalid selection. Please enter numbers from the list.")
            if len(set(selected_files_indices)) != len(selected_files_indices):
                raise ValueError("Duplicate selections are not allowed.")
            if len(selected_files_indices) < 2:
                print("You need to select at least two PDF files to merge.")
                continue
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please use comma-separated numbers from the list (e.g., 1,3,4) or 'all'.")

    if not selected_files_indices: # Handles case where loop is broken without selection (e.g. if adding a quit option later)
        print("No files selected for merging.")
        return

    for index in selected_files_indices:
        pdf_list.append(os.path.join(source_directory, available_pdfs[index]))

    if pdf_list:
        default_output_filename = "merged_output.pdf"
        prompt_text = f"Enter the name for the merged PDF file (default: {default_output_filename}) to be saved in '{output_directory}' folder: "
        output_pdf_name_input = input(prompt_text).strip()

        if not output_pdf_name_input:
            output_pdf_name_input = default_output_filename
            print(f"No output name provided. Using default: '{output_pdf_name_input}'")

        if not output_pdf_name_input.lower().endswith(".pdf"):
            output_pdf_name_input += ".pdf"

        # Ensure the results directory exists
        if not os.path.exists(output_directory):
            try:
                os.makedirs(output_directory)
                print(f"Created output directory: '{output_directory}'")
            except OSError as e:
                print(f"Error creating output directory '{output_directory}': {e}")
                return

        full_output_path = os.path.join(output_directory, output_pdf_name_input)

        print(f"Attempting to merge into: {full_output_path}") # Debug print
        if merge_pdfs(pdf_list, full_output_path):
            # Success message is printed by merge_pdfs
            pass
        else:
            # Error messages are printed by merge_pdfs
            print("Merging process encountered an error.")
    else:
        print("No PDF files were ultimately selected for merging.")


def run_pdf_page_deleter_logic():
    """
    Handles the PDF page deletion process, including listing files,
    getting user input, and calling the delete_pdf_pages function.
    """
    print("\nPDF Page Deletion selected.")

    source_directory = "files"  # Define the source directory for PDFs
    output_directory = "results"

    if not os.path.exists(source_directory) or not os.path.isdir(source_directory):
        print(f"Error: Source directory '{source_directory}' not found or is not a directory.")
        print(f"Please create a '{source_directory}' folder and place your PDF files inside it.")
        return

    available_pdfs = [f for f in os.listdir(source_directory) if f.lower().endswith(".pdf")]

    if not available_pdfs:
        print(f"No PDF files found in the '{source_directory}' directory.")
        return

    print("\nAvailable PDF files for page deletion:")
    for i, pdf_name in enumerate(available_pdfs):
        print(f"  {i + 1}. {pdf_name}")

    selected_pdf_index = -1
    while True:
        try:
            user_input = input("Select the PDF file to modify (enter the number): ").strip()
            selected_pdf_index = int(user_input) - 1
            if not 0 <= selected_pdf_index < len(available_pdfs):
                raise ValueError("Invalid selection. Please enter a number from the list.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter a number from the list.")

    input_pdf_name = available_pdfs[selected_pdf_index]
    input_pdf_full_path = os.path.join(source_directory, input_pdf_name)

    try:
        # Temporarily open with PyPDF2 to get page count
        import PyPDF2 # Local import for this check
        with open(input_pdf_full_path, 'rb') as f_in:
            reader = PyPDF2.PdfReader(f_in)
            num_pages = len(reader.pages)
        if num_pages == 0:
            print(f"The selected PDF '{input_pdf_name}' has 0 pages. Cannot delete pages.")
            return
        print(f"The selected PDF '{input_pdf_name}' has {num_pages} page(s).")
    except PyPDF2.errors.PdfReadError:
        print(f"Error: Could not read PDF '{input_pdf_name}'. It might be corrupted or password-protected.")
        return
    except Exception as e:
        print(f"Error reading PDF for page count: {e}")
        return

    pages_to_delete_list = []
    print(f"\nEnter the page numbers to delete from '{input_pdf_name}', separated by commas (e.g., 1,3,4). Max page: {num_pages}")
    print("If you enter no pages, a copy of the original file will be saved.")
    while True:
        try:
            user_input = input("Pages to delete: ").strip()
            if not user_input: # Allow empty input to mean no pages deleted
                pages_to_delete_list = []
                print("No pages selected for deletion. A copy of the original will be made.")
                break

            pages_str = [p.strip() for p in user_input.split(',')]
            pages_int = []
            for p_str in pages_str:
                if not p_str.isdigit():
                    raise ValueError("Invalid page number. All inputs must be numbers.")
                p = int(p_str)
                if not (1 <= p <= num_pages):
                    raise ValueError(f"Page number {p} is out of range (1-{num_pages}).")
                if p in pages_int: # Check for duplicates
                    raise ValueError(f"Duplicate page number {p} entered.")
                pages_int.append(p)

            pages_to_delete_list = sorted(list(set(pages_int))) # Store sorted unique pages
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please use comma-separated numbers from the list (e.g., 1,3,4). Max page: {num_pages}")

    # Define the default output filename based on the original input name and operation
    original_base_name = os.path.splitext(input_pdf_name)[0]
    default_output_filename = f"{original_base_name}_deleted_pages.pdf"

    prompt_text = f"Enter the name for the modified PDF file (default: {default_output_filename}) to be saved in '{output_directory}': "
    output_pdf_name_input = input(prompt_text).strip()

    if not output_pdf_name_input:
        output_pdf_name_input = default_output_filename
        print(f"Output file name not provided, using default: '{output_pdf_name_input}'")

    if not output_pdf_name_input.lower().endswith(".pdf"):
        output_pdf_name_input += ".pdf"

    # Ensure the results directory exists
    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory)
            print(f"Created output directory: '{output_directory}'")
        except OSError as e:
            print(f"Error creating output directory '{output_directory}': {e}")
            return

    full_output_path = os.path.join(output_directory, output_pdf_name_input)

    print(f"Attempting to delete pages and save to: {full_output_path}")
    if delete_pdf_pages(input_pdf_full_path, full_output_path, pages_to_delete_list):
        # Success message is printed by delete_pdf_pages
        pass
    else:
        # Error messages are printed by delete_pdf_pages
        print("Page deletion process encountered an error.")


def run_pdf_to_png_logic():
    """
    Handles the PDF to PNG conversion process, including listing files,
    getting user input, and calling the pdf_to_png function.
    """
    print("\nPDF to PNG Conversion selected.")

    source_directory = "files"  # Define the source directory for PDFs
    output_directory = "results"

    if not os.path.exists(source_directory) or not os.path.isdir(source_directory):
        print(f"Error: Source directory '{source_directory}' not found or is not a directory.")
        print(f"Please create a '{source_directory}' folder and place your PDF files inside it.")
        return

    available_pdfs = [f for f in os.listdir(source_directory) if f.lower().endswith(".pdf")]

    if not available_pdfs:
        print(f"No PDF files found in the '{source_directory}' directory.")
        return

    print("\nAvailable PDF files for conversion:")
    for i, pdf_name in enumerate(available_pdfs):
        print(f"  {i + 1}. {pdf_name}")

    selected_pdf_index = -1
    while True:
        try:
            user_input = input("Select the PDF file to convert (enter the number): ").strip()
            selected_pdf_index = int(user_input) - 1
            if not 0 <= selected_pdf_index < len(available_pdfs):
                raise ValueError("Invalid selection. Please enter a number from the list.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter a number from the list.")

    input_pdf_name = available_pdfs[selected_pdf_index]
    input_pdf_full_path = os.path.join(source_directory, input_pdf_name)

    # Ask for DPI (optional)
    dpi = 200
    dpi_input = input("Enter DPI for output images (default 200): ").strip()
    if dpi_input:
        try:
            dpi = int(dpi_input)
        except ValueError:
            print("Invalid DPI input. Using default 200.")
            dpi = 200

    # Output directory for PNGs (inside results, named after PDF)
    base_name = os.path.splitext(input_pdf_name)[0]
    output_png_dir = os.path.join(output_directory, f"{base_name}_pngs")

    print(f"Converting '{input_pdf_name}' to PNG images in '{output_png_dir}'...")
    output_files = pdf_to_png(input_pdf_full_path, output_png_dir, dpi)
    if output_files:
        print(f"Successfully converted PDF to {len(output_files)} PNG file(s).")
    else:
        print("PDF to PNG conversion failed.")


def run_png_to_pdf_logic():
    """
    Handles the PNG to PDF conversion process, including listing files,
    getting user input, and calling the pngs_to_pdf function.
    """
    print("\nPNG to PDF Conversion selected.")

    source_directory = "files"  # Define the source directory for PNGs
    output_directory = "results"

    if not os.path.exists(source_directory) or not os.path.isdir(source_directory):
        print(f"Error: Source directory '{source_directory}' not found or is not a directory.")
        print(f"Please create a '{source_directory}' folder and place your PNG files inside it.")
        return

    available_pngs = [f for f in os.listdir(source_directory) if f.lower().endswith(".png")]

    if not available_pngs:
        print(f"No PNG files found in the '{source_directory}' directory.")
        return

    print("\nAvailable PNG files for conversion:")
    for i, png_name in enumerate(available_pngs):
        print(f"  {i + 1}. {png_name}")

    print("\nEnter the numbers of the PNG files you want to convert, separated by commas (e.g., 1,3,4). Or type 'all' to select all files.")
    selected_files_indices = []
    while True:
        try:
            user_input = input("Select files to convert: ").strip()
            if user_input.lower() == 'all':
                selected_files_indices = list(range(len(available_pngs)))
                break
            selected_files_indices = [int(x.strip()) - 1 for x in user_input.split(',')]
            if not all(0 <= idx < len(available_pngs) for idx in selected_files_indices):
                raise ValueError("Invalid selection. Please enter numbers from the list.")
            if len(set(selected_files_indices)) != len(selected_files_indices):
                raise ValueError("Duplicate selections are not allowed.")
            if len(selected_files_indices) < 1:
                print("You need to select at least one PNG file to convert.")
                continue
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please use comma-separated numbers from the list (e.g., 1,3,4) or 'all'.")

    png_list = [os.path.join(source_directory, available_pngs[index]) for index in selected_files_indices]

    # Set default output filename based on input(s)
    if len(png_list) == 1:
        first_basename = os.path.splitext(os.path.basename(png_list[0]))[0]
        default_output_filename = f"{first_basename}.pdf"
    else:
        first_basename = os.path.splitext(os.path.basename(png_list[0]))[0]
        default_output_filename = f"{first_basename}_and_more.pdf"

    prompt_text = f"Enter the name for the output PDF file (default: {default_output_filename}) to be saved in '{output_directory}' folder: "
    output_pdf_name_input = input(prompt_text).strip()

    if not output_pdf_name_input:
        output_pdf_name_input = default_output_filename
        print(f"No output name provided. Using default: '{output_pdf_name_input}'")

    if not output_pdf_name_input.lower().endswith(".pdf"):
        output_pdf_name_input += ".pdf"

    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory)
            print(f"Created output directory: '{output_directory}'")
        except OSError as e:
            print(f"Error creating output directory '{output_directory}': {e}")
            return

    full_output_path = os.path.join(output_directory, output_pdf_name_input)

    print(f"Converting {len(png_list)} PNG file(s) to PDF: {full_output_path}")
    if pngs_to_pdf(png_list, full_output_path):
        print("Successfully converted PNG(s) to PDF.")
    else:
        print("PNG to PDF conversion failed.")


def run_png_to_jpeg_logic():
    """
    Handles the PNG to JPEG conversion process, including listing files,
    getting user input, and calling the png_to_jpeg function.
    """
    print("\nPNG to JPEG Conversion selected.")

    source_directory = "files"  # Define the source directory for PNGs
    output_directory = "results"  # JPEGs will be saved here

    if not os.path.exists(source_directory) or not os.path.isdir(source_directory):
        print(f"Error: Source directory '{source_directory}' not found or is not a directory.")
        print(f"Please create a '{source_directory}' folder and place your PNG files inside it.")
        return

    available_pngs = [f for f in os.listdir(source_directory) if f.lower().endswith(".png")]

    if not available_pngs:
        print(f"No PNG files found in the '{source_directory}' directory.")
        return

    print("\nAvailable PNG files for conversion:")
    for i, png_name in enumerate(available_pngs):
        print(f"  {i + 1}. {png_name}")

    print("\nEnter the numbers of the PNG files you want to convert, separated by commas (e.g., 1,3,4). Or type 'all' to select all files.")
    selected_files_indices = []
    while True:
        try:
            user_input = input("Select files to convert: ").strip()
            if user_input.lower() == 'all':
                selected_files_indices = list(range(len(available_pngs)))
                break
            selected_files_indices = [int(x.strip()) - 1 for x in user_input.split(',')]
            if not all(0 <= idx < len(available_pngs) for idx in selected_files_indices):
                raise ValueError("Invalid selection. Please enter numbers from the list.")
            if len(set(selected_files_indices)) != len(selected_files_indices):
                raise ValueError("Duplicate selections are not allowed.")
            if len(selected_files_indices) < 1:
                print("You need to select at least one PNG file to convert.")
                continue
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please use comma-separated numbers from the list (e.g., 1,3,4) or 'all'.")

    png_list = [os.path.join(source_directory, available_pngs[index]) for index in selected_files_indices]

    # Ask for JPEG quality (optional)
    quality = 85
    quality_input = input("Enter JPEG quality (1-100, default 85): ").strip()
    if quality_input:
        try:
            quality = int(quality_input)
            if not (1 <= quality <= 100):
                raise ValueError
        except ValueError:
            print("Invalid quality input. Using default 85.")
            quality = 85

    # Output directory for JPEGs (inside results, named after conversion)
    output_jpeg_dir = os.path.join(output_directory, "jpeg_from_png")

    print(f"Converting {len(png_list)} PNG file(s) to JPEG in '{output_jpeg_dir}'...")
    output_files = png_to_jpeg(png_list, output_jpeg_dir, quality)
    if output_files:
        print(f"Successfully converted {len(output_files)} PNG file(s) to JPEG.")
    else:
        print("PNG to JPEG conversion failed.")


def run_jpeg_to_png_logic():
    """
    Handles the JPEG to PNG conversion process, including listing files,
    getting user input, and calling the jpeg_to_png function.
    """
    print("\nJPEG to PNG Conversion selected.")

    source_directory = "files"  # Define the source directory for JPEGs
    output_directory = "results"  # PNGs will be saved here

    if not os.path.exists(source_directory) or not os.path.isdir(source_directory):
        print(f"Error: Source directory '{source_directory}' not found or is not a directory.")
        print(f"Please create a '{source_directory}' folder and place your JPEG files inside it.")
        return

    available_jpegs = [f for f in os.listdir(source_directory) if f.lower().endswith(".jpg") or f.lower().endswith(".jpeg")]

    if not available_jpegs:
        print(f"No JPEG files found in the '{source_directory}' directory.")
        return

    print("\nAvailable JPEG files for conversion:")
    for i, jpeg_name in enumerate(available_jpegs):
        print(f"  {i + 1}. {jpeg_name}")

    print("\nEnter the numbers of the JPEG files you want to convert, separated by commas (e.g., 1,3,4). Or type 'all' to select all files.")
    selected_files_indices = []
    while True:
        try:
            user_input = input("Select files to convert: ").strip()
            if user_input.lower() == 'all':
                selected_files_indices = list(range(len(available_jpegs)))
                break
            selected_files_indices = [int(x.strip()) - 1 for x in user_input.split(',')]
            if not all(0 <= idx < len(available_jpegs) for idx in selected_files_indices):
                raise ValueError("Invalid selection. Please enter numbers from the list.")
            if len(set(selected_files_indices)) != len(selected_files_indices):
                raise ValueError("Duplicate selections are not allowed.")
            if len(selected_files_indices) < 1:
                print("You need to select at least one JPEG file to convert.")
                continue
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please use comma-separated numbers from the list (e.g., 1,3,4) or 'all'.")

    jpeg_list = [os.path.join(source_directory, available_jpegs[index]) for index in selected_files_indices]

    # Output directory for PNGs (inside results, named after conversion)
    output_png_dir = os.path.join(output_directory, "png_from_jpeg")

    print(f"Converting {len(jpeg_list)} JPEG file(s) to PNG in '{output_png_dir}'...")
    output_files = jpeg_to_png(jpeg_list, output_png_dir)
    if output_files:
        print(f"Successfully converted {len(output_files)} JPEG file(s) to PNG.")
    else:
        print("JPEG to PNG conversion failed.")


def main():
    print("Main application script started.")
    while True:
        print("Choose a function to run:")
        print("1. Merge PDFs")
        print("2. Delete PDF Pages")
        print("3. Convert PDF to PNG")
        print("4. Convert PNG to PDF")
        print("5. Convert PNG to JPEG")
        print("6. Convert JPEG to PNG")
        print("7. Exit")

        choice = input("Enter your choice (1, 2, 3, 4, 5, 6, or 7): ")

        if choice == '1':
            run_pdf_merger_logic()
        elif choice == '2':
            run_pdf_page_deleter_logic()
        elif choice == '3':
            run_pdf_to_png_logic()
        elif choice == '4':
            run_png_to_pdf_logic()
        elif choice == '5':
            run_png_to_jpeg_logic()
        elif choice == '6':
            run_jpeg_to_png_logic()
        elif choice == '7':
            print("Exiting application. Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
