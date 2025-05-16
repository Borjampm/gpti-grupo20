import PyPDF2
import sys
import os

def merge_pdfs(pdf_files, output_filename):
    """
    Merges a list of PDF files into a single output PDF file.

    Args:
        pdf_files (list): A list of paths to the PDF files to merge.
        output_filename (str): The name of the output merged PDF file.
    """
    merger = PyPDF2.PdfMerger()
    for pdf_file in pdf_files:
        try:
            merger.append(pdf_file)
        except FileNotFoundError:
            print(f"Error: File not found - {pdf_file}")
            return False
        except Exception as e:
            print(f"Error processing file {pdf_file}: {e}")
            return False

    try:
        # Ensure the directory for the output file exists
        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_filename, "wb") as output_file:
            merger.write(output_file)
        print(f"Successfully merged PDFs into '{output_filename}'")
        return True
    except Exception as e:
        print(f"Error writing output file '{output_filename}': {e}")
        return False
    finally:
        merger.close()

if __name__ == "__main__":
    print("PDF Merger")

    source_directory = "files" # Define the source directory for PDFs
    output_directory = "results"

    if not os.path.exists(source_directory) or not os.path.isdir(source_directory):
        print(f"Error: Source directory '{source_directory}' not found or is not a directory.")
        print(f"Please create a '{source_directory}' folder and place your PDF files inside it.")
        sys.exit()

    available_pdfs = [f for f in os.listdir(source_directory) if f.lower().endswith(".pdf")]

    if not available_pdfs:
        print(f"No PDF files found in the '{source_directory}' directory.")
        sys.exit()

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
            # Validate indices
            if not all(0 <= idx < len(available_pdfs) for idx in selected_files_indices):
                raise ValueError("Invalid selection. Please enter numbers from the list.")
            if len(set(selected_files_indices)) != len(selected_files_indices):
                raise ValueError("Duplicate selections are not allowed.") # Prevent duplicates
            if len(selected_files_indices) < 2:
                print("You need to select at least two PDF files to merge.")
                continue
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please use comma-separated numbers from the list (e.g., 1,3,4) or 'all'.")

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

        full_output_path = os.path.join(output_directory, output_pdf_name_input)
        # Ensure the results directory exists (moved from merge_pdfs to here for CLI case)
        if not os.path.exists(output_directory):
            try:
                os.makedirs(output_directory)
                print(f"Created output directory: '{output_directory}'")
            except OSError as e:
                print(f"Error creating output directory '{output_directory}': {e}")
                # Do not proceed if directory creation fails
                sys.exit() # Exit if running as script and directory creation fails

        merge_pdfs(pdf_list, full_output_path)
    else:
        print("No PDF files were selected for merging.")
