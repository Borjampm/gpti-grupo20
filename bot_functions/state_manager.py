import os

# Global instance to manage conversation states
conversation_state = {}

# State constants
IDLE = "IDLE"
AWAITING_OPTION = "AWAITING_OPTION"
AWAITING_CLARIFICATION = "AWAITING_CLARIFICATION"
AWAITING_FIRST_PDF = "AWAITING_FIRST_PDF"
AWAITING_SECOND_PDF = "AWAITING_SECOND_PDF"
AWAITING_MULTIPLE_PDFS = "AWAITING_MULTIPLE_PDFS"
AWAITING_PDF_FOR_PAGE_DELETE = "AWAITING_PDF_FOR_PAGE_DELETE"
AWAITING_PAGE_NUMBERS_DELETE = "AWAITING_PAGE_NUMBERS_DELETE"
AWAITING_PDF_FOR_PAGE_EXTRACT = "AWAITING_PDF_FOR_PAGE_EXTRACT"
AWAITING_PAGE_NUMBERS_EXTRACT = "AWAITING_PAGE_NUMBERS_EXTRACT"
AWAITING_PDF_FOR_REORDER = "AWAITING_PDF_FOR_REORDER"
AWAITING_PAGE_ORDER = "AWAITING_PAGE_ORDER"

# Generic image transformation states
AWAITING_IMAGE_TO_PNG = "AWAITING_IMAGE_TO_PNG"
AWAITING_IMAGE_TO_JPEG = "AWAITING_IMAGE_TO_JPEG"

# Document transformation states
AWAITING_DOCX_TO_PDF = "AWAITING_DOCX_TO_PDF"
AWAITING_PDF_TO_DOCX = "AWAITING_PDF_TO_DOCX"
AWAITING_CSV_TO_EXCEL = "AWAITING_CSV_TO_EXCEL"
AWAITING_EXCEL_TO_CSV = "AWAITING_EXCEL_TO_CSV"
AWAITING_PPTX_TO_PDF = "AWAITING_PPTX_TO_PDF"

# ZIP operation states
AWAITING_MULTIPLE_FILES_FOR_ZIP = "AWAITING_MULTIPLE_FILES_FOR_ZIP"
AWAITING_ZIP_TO_EXTRACT = "AWAITING_ZIP_TO_EXTRACT"
AWAITING_ZIP_TO_LIST = "AWAITING_ZIP_TO_LIST"
AWAITING_ZIP_FOR_ADD = "AWAITING_ZIP_FOR_ADD"
AWAITING_FILES_TO_ADD = "AWAITING_FILES_TO_ADD"
AWAITING_ZIP_FOR_REMOVE = "AWAITING_ZIP_FOR_REMOVE"
AWAITING_FILENAMES_TO_REMOVE = "AWAITING_FILENAMES_TO_REMOVE"

# Generic ZIP bulk operation states
AWAITING_ZIP_FOR_IMAGES_TO_PNG = "AWAITING_ZIP_FOR_IMAGES_TO_PNG"
AWAITING_ZIP_FOR_IMAGES_TO_JPEG = "AWAITING_ZIP_FOR_IMAGES_TO_JPEG"
AWAITING_ZIP_FOR_PDF_CONCATENATION = "AWAITING_ZIP_FOR_PDF_CONCATENATION"
AWAITING_PDF_CONCATENATION_ORDER = "AWAITING_PDF_CONCATENATION_ORDER"

# Legacy states - keeping for backward compatibility but will be removed
AWAITING_ZIP_FOR_BULK = "AWAITING_ZIP_FOR_BULK"
AWAITING_BULK_OPERATION = "AWAITING_BULK_OPERATION"

def get_user_state(chat_id):
    """Get the current state of a user"""
    return conversation_state.get(chat_id, {}).get('state', IDLE)

def set_user_state(chat_id, state, **kwargs):
    """Set the state of a user and store additional data"""
    if chat_id not in conversation_state:
        conversation_state[chat_id] = {}
    conversation_state[chat_id]['state'] = state
    for key, value in kwargs.items():
        conversation_state[chat_id][key] = value

def get_user_data(chat_id, key, default=None):
    """Get specific data for a user"""
    return conversation_state.get(chat_id, {}).get(key, default)

def clear_user_data(chat_id):
    """Clear user data and temporary files"""
    if chat_id in conversation_state:
        # Clean up temporary files
        data = conversation_state[chat_id]
        for key, value in data.items():
            if key.endswith('_path') and value and os.path.exists(value):
                os.remove(value)
            elif key in ['pdf_paths', 'file_paths', 'files_to_add'] and isinstance(value, list):
                for path in value:
                    if path and os.path.exists(path):
                        os.remove(path)
        conversation_state[chat_id] = {}

def set_conversation_history(chat_id, messages):
    """Set the conversation history for a user"""
    if chat_id not in conversation_state:
        conversation_state[chat_id] = {}
    conversation_state[chat_id]['conversation_history'] = messages

def get_conversation_history(chat_id):
    """Get the conversation history for a user"""
    return conversation_state.get(chat_id, {}).get('conversation_history', [])

def add_to_conversation_history(chat_id, role, message):
    """Add a message to the conversation history"""
    if chat_id not in conversation_state:
        conversation_state[chat_id] = {}
    if 'conversation_history' not in conversation_state[chat_id]:
        conversation_state[chat_id]['conversation_history'] = []
    conversation_state[chat_id]['conversation_history'].append({'role': role, 'message': message})

def clear_conversation_history(chat_id):
    """Clear the conversation history for a user"""
    if chat_id in conversation_state and 'conversation_history' in conversation_state[chat_id]:
        conversation_state[chat_id]['conversation_history'] = []
