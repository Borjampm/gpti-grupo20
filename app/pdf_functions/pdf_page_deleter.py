import PyPDF2
import os
import sys

def delete_pdf_pages(input_pdf_path, output_pdf_path, pages_to_delete):
    """
    Deletes specified pages from a PDF file.

    Args:
        input_pdf_path (str): Path to the input PDF file.
        output_pdf_path (str): Path to save the modified PDF file.
        pages_to_delete (list): A list of page numbers (1-indexed) to delete.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(input_pdf_path)
        pdf_writer = PyPDF2.PdfWriter()
        num_pages = len(pdf_reader.pages)

        # Convert 1-indexed pages to 0-indexed and validate
        pages_to_delete_0_indexed = []
        for page_num in pages_to_delete:
            if not 1 <= page_num <= num_pages:
                print(f"Error: Page number {page_num} is out of range (1-{num_pages}).")
                return False
            pages_to_delete_0_indexed.append(page_num - 1)

        if not pages_to_delete_0_indexed:
            print("No pages specified for deletion.")
            # Or, copy all pages if no deletion is intended for empty list
            for page_num in range(num_pages):
                pdf_writer.add_page(pdf_reader.pages[page_num])
        else:
            for page_num in range(num_pages):
                if page_num not in pages_to_delete_0_indexed:
                    pdf_writer.add_page(pdf_reader.pages[page_num])

        if len(pdf_writer.pages) == 0 and num_pages > 0 and pages_to_delete_0_indexed:
             print(f"Warning: All pages were selected for deletion. The output PDF '{output_pdf_path}' will be empty.")


        # Ensure the directory for the output file exists
        output_dir = os.path.dirname(output_pdf_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_pdf_path, "wb") as output_file:
            pdf_writer.write(output_file)

        if len(pdf_writer.pages) == 0 and num_pages > 0 and pages_to_delete_0_indexed:
            print(f"Successfully created an empty PDF '{output_pdf_path}' as all pages were deleted.")
        elif not pages_to_delete_0_indexed and num_pages > 0 :
             print(f"No pages were deleted. Original content saved to '{output_pdf_path}'.")
        else:
            print(f"Successfully deleted pages from '{input_pdf_path}' and saved to '{output_pdf_path}'")
        return True

    except FileNotFoundError:
        print(f"Error: Input file not found - {input_pdf_path}")
        return False
    except PyPDF2.errors.PdfReadError:
        print(f"Error: Could not read PDF '{input_pdf_path}'. It might be corrupted or password-protected.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    print("PDF Page Deleter")

    source_directory = "files"
    output_directory = "results"

    if not os.path.exists(source_directory) or not os.path.isdir(source_directory):
        print(f"Error: Source directory '{source_directory}' not found.")
        sys.exit()

    available_pdfs = [f for f in os.listdir(source_directory) if f.lower().endswith(".pdf")]

    if not available_pdfs:
        print(f"No PDF files found in '{source_directory}'.")
        sys.exit()

    print("\nAvailable PDF files:")
    for i, pdf_name in enumerate(available_pdfs):
        print(f"  {i + 1}. {pdf_name}")

    selected_pdf_index = -1
    while True:
        try:
            user_input = input("Select a PDF file to modify (enter the number): ").strip()
            selected_pdf_index = int(user_input) - 1
            if not 0 <= selected_pdf_index < len(available_pdfs):
                raise ValueError("Invalid selection.")
            break
        except ValueError:
            print("Invalid input. Please enter a number from the list.")

    input_pdf_name = available_pdfs[selected_pdf_index]
    input_pdf_full_path = os.path.join(source_directory, input_pdf_name)

    try:
        pdf_reader_for_pages = PyPDF2.PdfReader(input_pdf_full_path)
        total_pages = len(pdf_reader_for_pages.pages)
        print(f"The selected PDF '{input_pdf_name}' has {total_pages} pages.")
    except Exception as e:
        print(f"Error reading PDF for page count: {e}")
        sys.exit()

    if total_pages == 0:
        print(f"The selected PDF '{input_pdf_name}' has no pages. Cannot delete pages from an empty PDF.")
        sys.exit()

    pages_to_delete_str = []
    while True:
        try:
            pages_input = input(f"Enter page numbers to delete, separated by commas (e.g., 1,3,5). Max page: {total_pages}: ").strip()
            if not pages_input:
                 print("No pages selected for deletion. The original file will be copied.")
                 pages_to_delete_str = []
                 break
            pages_to_delete_str = [x.strip() for x in pages_input.split(',')]
            pages_to_delete_int = []
            valid_input = True
            for p_str in pages_to_delete_str:
                if not p_str.isdigit():
                    raise ValueError("All inputs must be numbers.")
                p_int = int(p_str)
                if not (1 <= p_int <= total_pages):
                    raise ValueError(f"Page number {p_int} is out of range (1-{total_pages}).")
                if p_int in pages_to_delete_int:
                    raise ValueError(f"Duplicate page number {p_int} found in input.")
                pages_to_delete_int.append(p_int)

            if not pages_to_delete_int and pages_input: # Handles cases like "  ,"
                 raise ValueError("Invalid page number input.")

            pages_to_delete_str = pages_to_delete_int # Use validated integers
            break
        except ValueError as e:
            print(f"Invalid input: {e}")

    # Define the default output filename based on the original input name
    default_output_filename = f"edited_{input_pdf_name}"

    prompt_text = f"Enter the name for the modified PDF file (default: {default_output_filename}) to be saved in '{output_directory}': "
    output_pdf_name_input = input(prompt_text).strip()

    if not output_pdf_name_input:
        output_pdf_name_input = default_output_filename
        print(f"No output name provided. Using default: '{output_pdf_name_input}'")

    # Ensure the output filename ends with .pdf
    if not output_pdf_name_input.lower().endswith(".pdf"):
        output_pdf_name_input += ".pdf"

    full_output_path = os.path.join(output_directory, output_pdf_name_input)

    delete_pdf_pages(input_pdf_full_path, full_output_path, sorted(list(set(pages_to_delete_str)))) # ensure sorted unique pages
