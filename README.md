# Telegram Bot - Menu-Based Interaction (Feature Checklist)

## ✅ Features Implemented

- [x] Stateful conversation flow: The bot remembers where each user is in the conversation
- [x] Menu-based interaction: Users select numbered options to choose how their messages are processed
- [x] Spanish interface: All communication is in Spanish
- [x] Text processing: Print as-is or in UPPERCASE
- [x] PDF concatenation: Merge two PDF files

## 🛠️ Features To Be Implemented

- [ ] JPEG to PNG image transformation

## Bot Flow

1. **Start**: User sends `/start` command
   - Bot welcomes user and prompts to use `/help`
   - User state set to `IDLE`

2. **Help**: User sends `/help` command
   - Bot displays numbered menu with options:
     1. Print next message as-is
     2. Print next message in UPPERCASE
     3. Concatenate two PDF files
     4. Transform JPEG image to PNG
   - User state set to `AWAITING_OPTION`

3. **Option Selection**: User sends "1", "2", "3", or "4"
   - **Options 1-2**: Bot confirms selection and asks for message (state: `AWAITING_MESSAGE`)
   - **Option 3**: Bot asks for first PDF file (state: `AWAITING_FIRST_PDF`)
   - **Option 4**: Bot asks for JPEG image (state: `AWAITING_JPEG`)

4. **Message/File Processing**:
   - **Text messages**: Bot processes according to selected option and returns to menu
   - **PDF concatenation**:
     - User sends first PDF → Bot asks for second PDF (state: `AWAITING_SECOND_PDF`)
     - User sends second PDF → Bot concatenates and sends result
   - **JPEG to PNG** (not yet implemented):
     - User sends JPEG → Bot converts and sends back PNG file
     - Feature currently under development
   - User state reset to `AWAITING_OPTION`

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

3. Run the bot:
   ```bash
   python main.py
   ```

## Commands

- `/start` - Welcome message and introduction
- `/help` - Display options menu
- `/about` - Information about the bot

## Usage Examples (For Implemented Features)

### Text Processing Example

1. User: `/start`
   Bot: "¡Hola! Bienvenido al bot. Escribe /help para comenzar."

2. User: `/help`
   Bot: "¡Elige una opción escribiendo solo el número correspondiente:

   1. Imprimir el próximo mensaje
   2. Imprimir en MAYÚSCULAS el próximo mensaje
   3. Concatenar dos archivos PDF"

3. User: "2"
   Bot: "Elegiste la opción 2. Ahora envíame un mensaje para procesarlo."

4. User: "Hola mundo"
   Bot: "HOLA MUNDO"
   Bot: "Puedes enviar otro número de opción o escribir /help para ver el menú nuevamente."

### PDF Concatenation Example

1. User: `/help`
   Bot: "¡Elige una opción escribiendo solo el número correspondiente: ..."

2. User: "3"
   Bot: "Elegiste la opción 3. Ahora envíame el primer archivo PDF que quieres concatenar."

3. User: [sends first PDF file]
   Bot: "✅ Primer PDF recibido: document1.pdf
   Ahora envíame el segundo archivo PDF para concatenar."

4. User: [sends second PDF file]
   Bot: "✅ Segundo PDF recibido: document2.pdf
   🔄 Concatenando archivos PDF..."
   Bot: [sends concatenated PDF file] "✅ PDFs concatenados exitosamente!"
   Bot: "Puedes enviar otro número de opción o escribir /help para ver el menú nuevamente."

## Future Usage Example (JPEG to PNG)

*This section will be completed once the feature is implemented.*
