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
- [x] **ZIP Operations:**
  - [x] Create ZIP with multiple files
  - [x] Extract ZIP files
  - [x] List ZIP contents
  - [x] Add files to existing ZIP
  - [x] Remove files from existing ZIP
  - [x] Bulk operations within ZIP:
    - [x] Convert multiple images using all other supported operations
    - [x] Concatenate multiple PDFs in specified order
- [x] **File Validation:**
  - [x] File type validation (PDF, PNG, JPEG, SVG, ZIP)
  - [x] File size validation (maximum 20 MB per file)

## ✅ Recent Features Implemented

- [x] **Advertising messages during file processing**:
  - Users receive processing updates like "🔄 Concatenando PDFs en el orden especificado"
  - Random promotional messages appear while files are being processed
  - Final processed files are delivered as usual
  - 8 different promotional messages rotate randomly to engage users

## Bot Flow

1. **Start**: User sends `/start` command
   - Bot welcomes user and prompts to use `/help`
   - User state set to `IDLE`

2. **Help**: User sends `/help` command
   - Bot displays numbered menu con todas las 17 opciones
   - User state set to `AWAITING_OPTION`

3. **Option Selection**: User sends "1" through "11"
   - **PDF Operations (1-5)**: Varias funciones de manipulación de PDF
   - **Image Conversions (6-11)**: Varias conversiones de formatos de imagen
   - **ZIP Operations (12-17)**: Funciones de manejo de archivos ZIP

4. **File Processing Flow**:
   Cada opción sigue un flujo guiado donde el bot:
   - Valida tipo y tamaño de archivo (máx. 20 MB)
   - Procesa el archivo según la operación seleccionada
   - Puede mostrar un mensaje promocional mientras se procesa la solicitud (por ejemplo: "Muestra un mensaje promocional mientras se procesa la solicitud")
   - Devuelve el resultado procesado
   - Vuelve al menú de selección de opción
   - **ZIP Operations (12-17)** siguen el mismo patrón:
     1. Validar que sea ZIP y tamaño
     2. Recibir parámetros adicionales (acciones o listados)
     3. Ejecutar operación (crear, extraer, listar, agregar, eliminar o en masa)
     4. Enviar ZIP resultante
     5. Retornar al menú

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

### 🗜️ ZIP Operations
12. **Crear ZIP con varios archivos** - Combinar múltiples archivos en un ZIP
13. **Extraer ZIP** - Descomprimir un archivo ZIP enviado
14. **Listar contenidos de un ZIP** - Mostrar la lista de archivos dentro de un ZIP
15. **Agregar archivo a un ZIP existente** - Añadir uno o varios archivos a un ZIP recibido
16. **Eliminar archivo de un ZIP existente** - Quitar archivos específicos de un ZIP recibido
17. **Operaciones en masa dentro de un ZIP**:
    - Convertir múltiples imágenes (p. ej. PNG → SVG)
    - Concatenar múltiples PDFs según orden especificado
    - Renombrar en lote archivos
    - Aplicar marca de agua a múltiples archivos
    - Dividir múltiples PDFs en páginas individuales

## File Limitations

- **Maximum file size**: 20 MB per file
- **Supported formats**:
  - PDF files (.pdf)
  - Image files (.png, .jpg, .jpeg)
  - Vector graphics (.svg)
  - ZIP archives (.zip)


## 🔮 Future Enhancement Ideas

- Enhanced file validation with more detailed feedback
- Progress bars for long operations
- Support for additional file formats
- Batch processing with custom scripts
- Integration with cloud storage services

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
- `/help` - Display options menu with all 17 features
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

### ZIP Creation (Option 12)
1. User: `/help`
2. User: "12"
3. User: [sends first file]
4. User: [sends second file]
5. User: [sends third file]
6. User: "listo"
7. Bot: [returns ZIP file with all files]

### ZIP Extraction (Option 13)
1. User: `/help`
2. User: "13"
3. User: [sends ZIP file]
4. Bot: [extracts and sends each file individually]

### Bulk Operations in ZIP (Option 17)
1. User: `/help`
2. User: "17"
3. User: [sends ZIP file with multiple images]
4. User: "1" (for PNG to JPEG conversion)
5. Bot: [returns ZIP with all PNG files converted to JPEG]

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


