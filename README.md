# Telegram Bot - Menu-Based File Processing

## ✅ Features Implemented

- [x] Stateful conversation flow: The bot remembers where each user is in the conversation
- [x] **Natural Language Action Selection**: Users can describe what they want to do in natural language, and an LLM classifies their intent to determine the appropriate action
- [x] **Menu-based interaction**: Alternative manual mode with numbered options for direct action selection
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
- [x] **AI-Powered Intent Classification:**
  - [x] LLM (Gemma 3 27B Instruct) parses user requests and identifies appropriate actions
  - [x] Conversational flow continues until action is determined
  - [x] Falls back to manual mode if intent cannot be determined
- [x] **File Validation:**
  - [x] File type validation (PDF, PNG, JPEG, SVG, ZIP)
  - [x] File size validation (maximum 20 MB per file)

## ✅ Recent Features Implemented

- [x] **Advertising messages during file processing**:
  - Users receive processing updates like "🔄 Concatenando PDFs en el orden especificado"
  - Random promotional messages appear while files are being processed
  - Final processed files are delivered as usual
  - 8 different promotional messages rotate randomly to engage users
- [x] **AI-powered conversation flow**:
  - Natural language processing to understand user intents
  - Conversational interface that continues until action is determined
  - Smart fallback to manual mode when needed

## Bot Flow

### 🤖 AI-Powered Flow (Default)

1. **Start**: User sends `/start` command
   - Bot welcomes user and explains they can describe what they want to do
   - User state set to `IDLE`

2. **Automatic Natural Language Processing**: User sends ANY message
   - **No need to use `/help` first** - the bot automatically processes all messages
   - Bot sends user message to LLM (Gemma 3 27B Instruct) for intent classification
   - LLM analyzes the request and returns either:
     - `Acción: [number]` - if intent is clear, action is executed immediately
     - Conversational response - if clarification is needed
   - **Conversation continues** until LLM returns a clear action number
   - Once action is determined, flow proceeds to standard file processing

3. **Action Execution**: Following LLM classification
   - **PDF Operations (1-5)**: PDF manipulation functions
   - **Image Conversions (6-11)**: Various image format conversions
   - **ZIP Operations (12-17)**: ZIP file management functions
   - **AI Chat (18)**: Direct conversation with LLM

### 🔧 Manual Mode (Alternative)

1. **Manual Command**: User sends `/manual` command
   - Bot displays numbered menu with all 18 options
   - User state set to `AWAITING_OPTION`

2. **Direct Option Selection**: User sends "1" through "18"
   - Immediately proceeds to selected action without LLM classification
   - Same file processing flow as before

### 📋 File Processing Flow
Cada opción sigue un flujo guiado donde el bot:
- Valida tipo y tamaño de archivo (máx. 20 MB)
- Procesa el archivo según la operación seleccionada
- Puede mostrar un mensaje promocional mientras se procesa la solicitud
- Devuelve el resultado procesado
- Vuelve al estado IDLE para nueva interacción natural

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

### 🤖 AI-Powered Features
18. **Conversación con LLM (Gemini)** - Chat directo con Gemma 3 27B Instruct
    - **Intent Classification**: Automatically used to parse user requests in natural language
    - **Direct Chat**: Available as option 18 for direct conversation with the AI
    - **Conversational Flow**: Continues interaction until user intent is clearly determined

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

3. Create a `.env` file with your bot token and Gemini API key:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. Run the bot:
   ```bash
   python main.py
   ```

## Commands

- `/start` - Welcome message and introduction to natural language interaction
- `/help` - Display options menu with all 18 features (now includes AI option 18)
- `/about` - Information about the bot and its capabilities
- `/manual` - Access manual mode with numbered options for direct action selection

## Usage Examples

### 🤖 Natural Language Flow (Default)

#### PDF Operations via Natural Language
1. User: "Necesito unir dos PDFs en uno solo"
2. Bot: [LLM responds with "Acción: 1"]
3. User: [sends first PDF file]
4. User: [sends second PDF file]
5. Bot: [returns concatenated PDF]

#### Image Conversion via Natural Language
1. User: "Convierte esta imagen JPEG a PNG"
2. Bot: [LLM responds with "Acción: 6"]
3. User: [sends JPEG file]
4. Bot: [returns converted PNG file]

#### Complex Request with Clarification
1. User: "Quiero hacer algo con archivos"
2. Bot: [LLM asks for clarification]
3. User: "Extraer las páginas 2-5 de un PDF"
4. Bot: [LLM responds with "Acción: 4"]
5. User: [sends PDF file]
6. User: "2-5"
7. Bot: [returns PDF with extracted pages]

#### First Time User Experience
1. User: `/start`
2. Bot: [Welcome message explaining natural language interaction]
3. User: "Quiero convertir un PDF a imágenes PNG"
4. Bot: [LLM responds with "Acción: 9"]
5. User: [sends PDF file]
6. Bot: [returns all pages as PNG files]

### 🔧 Manual Mode Examples

#### PDF Concatenation (Option 1)
1. User: `/manual`
2. User: "1"
3. User: [sends first PDF file]
4. User: [sends second PDF file]
5. Bot: [returns concatenated PDF]

#### Multiple PDF Concatenation (Option 2)
1. User: `/manual`
2. User: "2"
3. User: [sends first PDF file]
4. User: [sends second PDF file]
5. User: [sends third PDF file]
6. User: "listo"
7. Bot: [returns concatenated PDF with all files]

#### Page Operations (Options 3-5)
1. User: `/manual`
2. User: "3" (for delete pages)
3. User: [sends PDF file]
4. User: "1,3,5-7" (specify pages to delete)
5. Bot: [returns PDF with specified pages removed]

#### Image Conversions (Options 6-11)
1. User: `/manual`
2. User: "6" (for JPEG to PNG)
3. User: [sends JPEG file]
4. Bot: [returns converted PNG file]

#### PDF to Image (Options 8-9)
1. User: `/manual`
2. User: "9" (for all pages to PNG)
3. User: [sends PDF file]
4. Bot: [returns each page as separate PNG files]

#### ZIP Creation (Option 12)
1. User: `/manual`
2. User: "12"
3. User: [sends first file]
4. User: [sends second file]
5. User: [sends third file]
6. User: "listo"
7. Bot: [returns ZIP file with all files]

#### ZIP Extraction (Option 13)
1. User: `/manual`
2. User: "13"
3. User: [sends ZIP file]
4. Bot: [extracts and sends each file individually]

#### Bulk Operations in ZIP (Option 17)
1. User: `/manual`
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


