# Telegram Bot - Menu-Based File Processing

## ✅ Features Implemented

- [x] Stateful conversation flow: The bot remembers where each user is in the conversation
- [x] Menu-based interaction: Users select numbered options to choose how their messages are processed
- [x] Spanish interface: All communication is in Spanish
- [x] **PDF Operations:**
  - [x] Concatenate two PDF files
  - [x] Concatenate multiple PDF files
  - [x] Delete specific pages from PDF
  - [x] Extract specific pages from PDF
  - [x] Reorder pages in PDF
- [x] **Image Conversions:**
  - [x] JPEG ⇄ PNG conversion
  - [x] PDF → PNG (first page or all pages)
  - [x] SVG → PNG or JPEG conversion
- [x] **File Validation:**
  - [x] File type validation (PDF, PNG, JPEG, SVG)
  - [x] File size validation (maximum 20 MB per file)

## Bot Flow

1. **Start**: User sends `/start` command
   - Bot welcomes user and prompts to use `/help`
   - User state set to `IDLE`

2. **Help**: User sends `/help` command
   - Bot displays numbered menu with all 11 options
   - User state set to `AWAITING_OPTION`

3. **Option Selection**: User sends "1" through "11"
   - **PDF Operations (1-5)**: Various PDF manipulation features
   - **Image Conversions (6-11)**: Various image format conversions

4. **File Processing Flow**:
   Each option follows a guided flow where the bot:
   - Validates file type and size (max 20 MB)
   - Processes the file according to the selected operation
   - Returns the processed result
   - Returns to option selection menu

## Available Options

### 📄 PDF Operations
1. **Concatenate two PDFs** - Combine exactly two PDF files
2. **Concatenate multiple PDFs** - Combine 2 or more PDF files (send files one by one, then type "listo")
3. **Delete pages from PDF** - Remove specific pages (e.g., "1,3,5" or "1-3,7-9")
4. **Extract pages from PDF** - Create new PDF with only specified pages
5. **Reorder pages in PDF** - Rearrange pages in custom order (e.g., "3,1,2,4")

### 🖼️ Image Conversions
6. **JPEG → PNG** - Convert JPEG images to PNG format
7. **PNG → JPEG** - Convert PNG images to JPEG format (with white background for transparency)
8. **PDF → PNG (first page)** - Extract first page of PDF as PNG image
9. **PDF → PNG (all pages)** - Extract all pages of PDF as separate PNG images
10. **SVG → PNG** - Convert SVG vector graphics to PNG format
11. **SVG → JPEG** - Convert SVG vector graphics to JPEG format

## File Limitations

- **Maximum file size**: 20 MB per file
- **Supported formats**:
  - PDF files (.pdf)
  - Image files (.png, .jpg, .jpeg)
  - Vector graphics (.svg)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Additional system requirements**:
   - For PDF to image conversion: `poppler-utils`
     ```bash
     # Ubuntu/Debian
     sudo apt-get install poppler-utils

     # macOS
     brew install poppler

     # Windows
     # Download poppler binaries and add to PATH
     ```

3. Create a `.env` file with your bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

4. Run the bot:
   ```bash
   python main.py
   ```

## Commands

- `/start` - Welcome message and introduction
- `/help` - Display options menu with all 11 features
- `/about` - Information about the bot and its capabilities

## Usage Examples

### PDF Concatenation (Option 1)
1. User: `/help`
2. User: "1"
3. User: [sends first PDF file]
4. User: [sends second PDF file]
5. Bot: [returns concatenated PDF]

### Multiple PDF Concatenation (Option 2)
1. User: `/help`
2. User: "2"
3. User: [sends first PDF file]
4. User: [sends second PDF file]
5. User: [sends third PDF file]
6. User: "listo"
7. Bot: [returns concatenated PDF with all files]

### Page Operations (Options 3-5)
1. User: `/help`
2. User: "3" (for delete pages)
3. User: [sends PDF file]
4. User: "1,3,5-7" (specify pages to delete)
5. Bot: [returns PDF with specified pages removed]

### Image Conversions (Options 6-11)
1. User: `/help`
2. User: "6" (for JPEG to PNG)
3. User: [sends JPEG file]
4. Bot: [returns converted PNG file]

### PDF to Image (Options 8-9)
1. User: `/help`
2. User: "9" (for all pages to PNG)
3. User: [sends PDF file]
4. Bot: [returns each page as separate PNG files]

## Error Handling

The bot includes comprehensive error handling for:
- Invalid file types
- Oversized files (>20MB)
- Corrupted files
- Invalid page number specifications
- Processing errors

## Technical Features

- **File validation**: Automatic checking of file type and size
- **Temporary file management**: Automatic cleanup of temporary files
- **Page parsing**: Flexible page specification (individual numbers, ranges, combinations)
- **Image processing**: High-quality conversions with proper transparency handling
- **Memory efficient**: Processes files without keeping them in memory unnecessarily


