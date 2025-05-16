# ⚙️ File Manipulator – Technical Stack and Architecture

## Current Simplified Implementation (CLI for PDF Merging)

The current version is a command-line application structured within an `app` package.
1. The main entry point is `app/main.py`.
2. `app/main.py` provides a menu and orchestrates PDF and image manipulation processes.
3. It scans a local `files` directory for PDF, PNG, and JPEG files and prompts the user for selections and output details.
4. PDF merging logic is handled by `app/pdf_functions/pdf_merger.py` (using `PyPDF2`).
   PDF page deletion is handled by `app/pdf_functions/pdf_page_deleter.py` (using `PyPDF2`).
   PDF to PNG conversion is handled by `app/pdf_functions/pdf_to_png.py` (using `pdf2image` and `Pillow`).
   PNG to PDF conversion is handled by `app/image_functions/png_to_pdf.py` (using `Pillow`).
   PNG to JPEG and JPEG to PNG conversions are handled by `app/image_functions/png_to_jpeg.py` and `app/image_functions/jpeg_to_png.py` respectively (using `Pillow`).
5. The resulting processed files are saved to a local `results` directory, often in type-specific subdirectories.
6. Project dependencies are managed using `Poetry` (includes `PyPDF2`, `pdf2image`, `Pillow`).

(The following sections describe the target architecture for the full File Manipulator service.)

## Architecture (Target)

The File Manipulator is a stateless service component that:
1. Receives instructions via an internal API or message queue.
2. Fetches input files (cloud storage or memory).
3. Applies transformations using local tools and libraries.
4. Stores the result temporarily and returns a download URL.

---

## Tech Stack

### 🧠 Programming Language

- **Python 3.11+**

### 📦 Core Libraries

| Purpose                   | Library                    | Notes                                     |
|---------------------------|----------------------------|-------------------------------------------|
| PDF Manipulation          | `PyMuPDF` (fitz), `PyPDF2` | `PyPDF2` used for merge/delete in CLI. `pdf2image` (+ `Pillow`) for PDF to PNG. |
| Image Conversion/Resizing | `Pillow`, `opencv-python`  | `Pillow` used for PNG ↔ PDF, PNG ↔ JPEG. |
| SVG to PNG/JPG Conversion | `cairosvg`, `svglib`       |                                           |
| Temporary Files           | `tempfile`, `shutil`       |                                           |
| Metadata Sanitization     | `Piexif`, `ExifTool` (CLI) |                                           |

---

## Optional CLI Tools (for advanced use)

- `ImageMagick` – More powerful image manipulation
- `Ghostscript` – Better PDF compression/resizing
- `poppler-utils` – For PDF to image conversion
- `svgo` – Optimize SVGs

---

## File Handling (Current CLI)

- Input files (PDF, PNG, JPEG) are read from a local `files` directory.
- All processing is done locally by the script.
- Output files are saved to a local `results` directory, with subdirectories for some conversion types (e.g., `results/pdf_basename_pngs/`, `results/jpeg_from_png/`, `results/png_from_jpeg/`).
- No explicit temporary file handling is implemented in the current CLI beyond library defaults.

## File Handling (Target)

- Files retrieved from S3/GCS using pre-signed URLs
- All processing done in `/tmp` with auto-cleanup
- File size checks and MIME type validation before processing

---

## Security

- Use of isolated containers for each processing job (via Docker)
- Enforce MIME-type whitelisting
- Rate-limiting and logging of file operations
- Cleanup on error/failure

---

## Interfaces

### Current CLI Interaction
- User interacts with the `app/main.py` script (run as `python -m app.main`) via terminal prompts.
- The script presents a menu to choose functionalities (e.g., PDF merging, image conversions).
- For PDF merging, input files are selected from a scanned `files` directory.

### REST API (Target - Internal)
- **REST API** (internal): Accepts POST requests with:
  ```json
  {
    "action": "convert",
    "input_format": "png",
    "output_format": "jpeg",
    "files": ["https://example.com/input.png"]
  }
