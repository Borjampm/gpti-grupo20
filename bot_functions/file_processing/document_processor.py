import os
import tempfile
import pandas as pd
from docx import Document
from pptx import Presentation
import subprocess
import platform

async def convert_docx_to_pdf(docx_path: str, chat_id: int) -> str:
    """Convert DOCX file to PDF"""
    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"docx_to_pdf_{chat_id}.pdf")

        # Try different methods based on platform
        if platform.system() == "Windows":
            # Use docx2pdf library for Windows
            from docx2pdf import convert
            convert(docx_path, output_path)
        else:
            # Use LibreOffice for Linux/Mac
            try:
                subprocess.run([
                    'libreoffice', '--headless', '--convert-to', 'pdf',
                    '--outdir', temp_dir, docx_path
                ], check=True, capture_output=True)

                # LibreOffice creates file with same name but .pdf extension
                base_name = os.path.splitext(os.path.basename(docx_path))[0]
                libreoffice_output = os.path.join(temp_dir, f"{base_name}.pdf")

                if os.path.exists(libreoffice_output):
                    os.rename(libreoffice_output, output_path)
                else:
                    return None
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback: try using python-docx to extract text and create simple PDF
                return await _create_simple_pdf_from_docx(docx_path, chat_id)

        return output_path if os.path.exists(output_path) else None
    except Exception as e:
        print(f"Error converting DOCX to PDF: {e}")
        return None

async def _create_simple_pdf_from_docx(docx_path: str, chat_id: int) -> str:
    """Fallback method to create PDF from DOCX using text extraction"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter

        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"docx_to_pdf_simple_{chat_id}.pdf")

        # Extract text from DOCX
        doc = Document(docx_path)
        text_content = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text)

        # Create PDF
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        y_position = height - 50

        for line in text_content:
            if y_position < 50:  # Start new page
                c.showPage()
                y_position = height - 50

            # Wrap long lines
            words = line.split()
            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                if len(test_line) * 6 < width - 100:  # Rough character width estimation
                    current_line = test_line
                else:
                    if current_line:
                        c.drawString(50, y_position, current_line)
                        y_position -= 15
                    current_line = word

            if current_line:
                c.drawString(50, y_position, current_line)
                y_position -= 20

        c.save()
        return output_path
    except Exception as e:
        print(f"Error creating simple PDF from DOCX: {e}")
        return None

async def convert_pdf_to_docx(pdf_path: str, chat_id: int) -> str:
    """Convert PDF file to DOCX (basic text extraction)"""
    try:
        from PyPDF2 import PdfReader

        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"pdf_to_docx_{chat_id}.docx")

        # Extract text from PDF
        reader = PdfReader(pdf_path)
        text_content = []

        for page in reader.pages:
            text = page.extract_text()
            if text.strip():
                text_content.append(text)

        # Create DOCX document
        doc = Document()

        for page_text in text_content:
            # Split into paragraphs by double newlines or long lines
            paragraphs = page_text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    doc.add_paragraph(para.strip())

        doc.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error converting PDF to DOCX: {e}")
        return None

async def convert_csv_to_excel(csv_path: str, chat_id: int) -> str:
    """Convert CSV file to Excel"""
    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"csv_to_excel_{chat_id}.xlsx")

        # Read CSV and convert to Excel
        df = pd.read_csv(csv_path)
        df.to_excel(output_path, index=False)

        return output_path
    except Exception as e:
        print(f"Error converting CSV to Excel: {e}")
        return None

async def convert_excel_to_csv(excel_path: str, chat_id: int) -> str:
    """Convert Excel file to CSV"""
    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"excel_to_csv_{chat_id}.csv")

        # Read Excel and convert to CSV
        df = pd.read_excel(excel_path, sheet_name=0)  # Read first sheet
        df.to_csv(output_path, index=False)

        return output_path
    except Exception as e:
        print(f"Error converting Excel to CSV: {e}")
        return None

async def convert_pptx_to_pdf(pptx_path: str, chat_id: int) -> str:
    """Convert PowerPoint file to PDF"""
    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"pptx_to_pdf_{chat_id}.pdf")

        # Try different methods based on platform
        if platform.system() == "Windows":
            # Use comtypes for Windows
            try:
                import comtypes.client
                powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
                powerpoint.Visible = 1

                presentation = powerpoint.Presentations.Open(os.path.abspath(pptx_path))
                presentation.SaveAs(os.path.abspath(output_path), 32)  # 32 = PDF format
                presentation.Close()
                powerpoint.Quit()
            except:
                return await _create_simple_pdf_from_pptx(pptx_path, chat_id)
        else:
            # Use LibreOffice for Linux/Mac
            try:
                subprocess.run([
                    'libreoffice', '--headless', '--convert-to', 'pdf',
                    '--outdir', temp_dir, pptx_path
                ], check=True, capture_output=True)

                # LibreOffice creates file with same name but .pdf extension
                base_name = os.path.splitext(os.path.basename(pptx_path))[0]
                libreoffice_output = os.path.join(temp_dir, f"{base_name}.pdf")

                if os.path.exists(libreoffice_output):
                    os.rename(libreoffice_output, output_path)
                else:
                    return None
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback: create simple PDF from presentation text
                return await _create_simple_pdf_from_pptx(pptx_path, chat_id)

        return output_path if os.path.exists(output_path) else None
    except Exception as e:
        print(f"Error converting PPTX to PDF: {e}")
        return None

async def _create_simple_pdf_from_pptx(pptx_path: str, chat_id: int) -> str:
    """Fallback method to create PDF from PPTX using text extraction"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter

        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"pptx_to_pdf_simple_{chat_id}.pdf")

        # Extract text from PPTX
        prs = Presentation(pptx_path)
        slides_content = []

        for slide in prs.slides:
            slide_text = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text.append(shape.text.strip())
            if slide_text:
                slides_content.append('\n'.join(slide_text))

        # Create PDF
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter

        for i, slide_content in enumerate(slides_content):
            if i > 0:
                c.showPage()

            y_position = height - 50
            c.drawString(50, y_position, f"Slide {i + 1}")
            y_position -= 30

            lines = slide_content.split('\n')
            for line in lines:
                if y_position < 50:
                    c.showPage()
                    y_position = height - 50

                # Wrap long lines
                words = line.split()
                current_line = ""
                for word in words:
                    test_line = f"{current_line} {word}".strip()
                    if len(test_line) * 6 < width - 100:
                        current_line = test_line
                    else:
                        if current_line:
                            c.drawString(50, y_position, current_line)
                            y_position -= 15
                        current_line = word

                if current_line:
                    c.drawString(50, y_position, current_line)
                    y_position -= 15

        c.save()
        return output_path
    except Exception as e:
        print(f"Error creating simple PDF from PPTX: {e}")
        return None
