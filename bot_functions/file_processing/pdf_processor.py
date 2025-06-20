import os
import tempfile
from PyPDF2 import PdfWriter, PdfReader

async def concatenate_two_pdfs(first_pdf_path: str, second_pdf_path: str, chat_id: int) -> str:
    """Concatenate two PDF files"""
    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"concatenated_{chat_id}.pdf")

        pdf_writer = PdfWriter()

        # Check if both files exist
        if not os.path.exists(first_pdf_path):
            print(f"First PDF file not found: {first_pdf_path}")
            return None
        if not os.path.exists(second_pdf_path):
            print(f"Second PDF file not found: {second_pdf_path}")
            return None

        # Add pages from first PDF
        try:
            with open(first_pdf_path, 'rb') as first_file:
                first_reader = PdfReader(first_file)
                for page in first_reader.pages:
                    pdf_writer.add_page(page)
        except Exception as e:
            print(f"Error reading first PDF: {e}")
            return None

        # Add pages from second PDF
        try:
            with open(second_pdf_path, 'rb') as second_file:
                second_reader = PdfReader(second_file)
                for page in second_reader.pages:
                    pdf_writer.add_page(page)
        except Exception as e:
            print(f"Error reading second PDF: {e}")
            return None

        # Write output
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        return output_path
    except Exception as e:
        print(f"Error concatenating PDFs: {e}")
        return None

async def concatenate_multiple_pdfs(pdf_paths: list, chat_id: int) -> str:
    """Concatenate multiple PDF files"""
    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"concatenated_multiple_{chat_id}.pdf")

        pdf_writer = PdfWriter()

        for pdf_path in pdf_paths:
            # Check if file exists and is accessible
            if not os.path.exists(pdf_path):
                print(f"PDF file not found: {pdf_path}")
                continue

            try:
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_reader = PdfReader(pdf_file)
                    # Add all pages from this PDF
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)
                print(f"Successfully processed: {pdf_path}")
            except Exception as e:
                print(f"Error reading PDF {pdf_path}: {e}")
                continue

        # Check if we have any pages to write
        if len(pdf_writer.pages) == 0:
            print("No valid pages found to concatenate")
            return None

        # Write output
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        return output_path
    except Exception as e:
        print(f"Error concatenating multiple PDFs: {e}")
        return None

async def delete_pdf_pages(pdf_path: str, pages_to_delete: list, chat_id: int) -> str:
    """Delete specific pages from PDF"""
    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"pages_deleted_{chat_id}.pdf")

        pdf_writer = PdfWriter()

        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)

            for page_num in range(1, total_pages + 1):
                if page_num not in pages_to_delete:
                    pdf_writer.add_page(pdf_reader.pages[page_num - 1])

        # Write output
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        return output_path
    except Exception as e:
        print(f"Error deleting PDF pages: {e}")
        return None

async def extract_pdf_pages(pdf_path: str, pages_to_extract: list, chat_id: int) -> str:
    """Extract specific pages from PDF"""
    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"pages_extracted_{chat_id}.pdf")

        pdf_writer = PdfWriter()

        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)

            for page_num in pages_to_extract:
                pdf_writer.add_page(pdf_reader.pages[page_num - 1])

        # Write output
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        return output_path
    except Exception as e:
        print(f"Error extracting PDF pages: {e}")
        return None

async def reorder_pdf_pages(pdf_path: str, page_order: list, chat_id: int) -> str:
    """Reorder pages in PDF according to specified order"""
    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"pages_reordered_{chat_id}.pdf")

        pdf_writer = PdfWriter()

        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)

            for page_num in page_order:
                pdf_writer.add_page(pdf_reader.pages[page_num - 1])

        # Write output
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        return output_path
    except Exception as e:
        print(f"Error reordering PDF pages: {e}")
        return None
