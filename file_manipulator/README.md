# PDF File Manipulator (CLI - PDF Merging)

This project currently provides a command-line interface (CLI) tool to merge multiple PDF files.

## Project Overview

The initial implementation focuses on a local PDF merging utility. Future development aims to expand this into a more comprehensive backend service for various file manipulations as described in `project-description.md` and `project-tech.md`.

## Current Features

- **Merge PDFs**: Select multiple PDF files from a local `files` directory and merge them into a single PDF.
- **Delete PDF Pages**: Select a PDF file from the `files` directory, specify pages to delete, and save it as a new file.
- **Convert PDF to PNG**: Select a PDF file and convert each page to a PNG image.
- **Convert PNG to PDF**: Select one or more PNG files and convert them into a single PDF document.
- **Convert PNG to JPEG**: Select one or more PNG files and convert them to JPEG format.
- **Convert JPEG to PNG**: Select one or more JPEG files and convert them to PNG format.

## Setup and Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management.

1.  **Install Poetry**:
    If you don't have Poetry installed, follow the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).

2.  **Clone the repository** (if you haven't already):
    ```bash
    # git clone <repository-url>
    # cd <repository-directory>
    ```

3.  **Install dependencies**:
    Navigate to the project root directory (where `pyproject.toml` is located) and run:
    ```bash
    poetry install
    ```
    This will create a virtual environment and install the necessary packages (e.g., `PyPDF2`).

## Usage

1.  **Prepare your files**:
    - Create a directory named `files` in the project root.
    - Place all the PDF, PNG, or JPEG files you want to potentially process into this `files` directory.

2.  **Run the application**:
    The main entry point for the application is `app/main.py`. Execute it using Poetry:
    ```bash
    poetry run python -m app.main
    ```

3.  **Follow the prompts**:
    - The script will present a menu. Select the appropriate option for the desired operation.
    - **For Merging PDFs**:
        - The script will list PDF files from the `files` directory.
        - Enter numbers for the files to merge (e.g., `1,3,4`) or `all`.
        - Provide an output name (default: `merged_output.pdf`).
    - **For Deleting PDF Pages**:
        - The script will list PDF files from the `files` directory.
        - Select the number corresponding to the PDF file to modify.
        - The script will display the total number of pages in the selected PDF.
        - Enter the page numbers to delete, separated by commas (e.g., `1,3,4`).
        - Provide an output name for the modified PDF (default: `<original_filename_without_extension>_deleted_pages.pdf`).
    - **For PDF to PNG Conversion**:
        - Select a PDF file.
        - Optionally, specify DPI for output images (default: 200).
        - PNG images (one per page) are saved in `results/<pdf_basename>_pngs/`.
    - **For PNG to PDF Conversion**:
        - Select one or more PNG files.
        - Provide an output name for the PDF (defaults based on input, e.g., `<first_png_basename>.pdf` or `<first_png_basename>_and_more.pdf`).
        - The resulting PDF is saved in the `results/` directory.
    - **For PNG to JPEG Conversion**:
        - Select one or more PNG files.
        - Optionally, specify JPEG quality (1-100, default: 85).
        - JPEG images are saved in `results/jpeg_from_png/`.
    - **For JPEG to PNG Conversion**:
        - Select one or more JPEG files.
        - PNG images are saved in `results/png_from_jpeg/`.

4.  **Find your processed files**:
    - The resulting PDF (merged or with deleted pages) will be saved in a directory named `results` (which will be created in the project root if it doesn't exist).

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                     # Main application entry point
│   └── pdf_functions/
│       ├── __init__.py
│       ├── pdf_merger.py           # Script for merging PDFs
│       └── pdf_page_deleter.py     # Script for deleting pages from PDFs
├── files/                          # Directory for input PDF, PNG, JPEG files
├── results/                        # Directory for output processed files
├── pyproject.toml                  # Poetry configuration and dependencies
├── poetry.lock             # Poetry lock file
├── project-description.md  # High-level project requirements
├── project-tech.md         # Technical stack and architecture details
└── README.md               # This file
```

## Future Development

Refer to `project-description.md` and `project-tech.md` for the planned expansion of this project into a full backend service with more file manipulation capabilities and a proper API.
