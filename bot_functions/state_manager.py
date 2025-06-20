import os

# Global instance to manage conversation states
conversation_state = {}

# State constants
IDLE = "IDLE"
AWAITING_OPTION = "AWAITING_OPTION"
AWAITING_FIRST_PDF = "AWAITING_FIRST_PDF"
AWAITING_SECOND_PDF = "AWAITING_SECOND_PDF"
AWAITING_MULTIPLE_PDFS = "AWAITING_MULTIPLE_PDFS"
AWAITING_PDF_FOR_PAGE_DELETE = "AWAITING_PDF_FOR_PAGE_DELETE"
AWAITING_PAGE_NUMBERS_DELETE = "AWAITING_PAGE_NUMBERS_DELETE"
AWAITING_PDF_FOR_PAGE_EXTRACT = "AWAITING_PDF_FOR_PAGE_EXTRACT"
AWAITING_PAGE_NUMBERS_EXTRACT = "AWAITING_PAGE_NUMBERS_EXTRACT"
AWAITING_PDF_FOR_REORDER = "AWAITING_PDF_FOR_REORDER"
AWAITING_PAGE_ORDER = "AWAITING_PAGE_ORDER"
AWAITING_JPEG = "AWAITING_JPEG"
AWAITING_PNG = "AWAITING_PNG"
AWAITING_PDF_TO_PNG_FIRST = "AWAITING_PDF_TO_PNG_FIRST"
AWAITING_PDF_TO_PNG_ALL = "AWAITING_PDF_TO_PNG_ALL"
AWAITING_SVG_TO_PNG = "AWAITING_SVG_TO_PNG"
AWAITING_SVG_TO_JPEG = "AWAITING_SVG_TO_JPEG"

# ZIP operation states
AWAITING_MULTIPLE_FILES_FOR_ZIP = "AWAITING_MULTIPLE_FILES_FOR_ZIP"
AWAITING_ZIP_TO_EXTRACT = "AWAITING_ZIP_TO_EXTRACT"
AWAITING_ZIP_TO_LIST = "AWAITING_ZIP_TO_LIST"
AWAITING_ZIP_FOR_ADD = "AWAITING_ZIP_FOR_ADD"
AWAITING_FILES_TO_ADD = "AWAITING_FILES_TO_ADD"
AWAITING_ZIP_FOR_REMOVE = "AWAITING_ZIP_FOR_REMOVE"
AWAITING_FILENAMES_TO_REMOVE = "AWAITING_FILENAMES_TO_REMOVE"
AWAITING_ZIP_FOR_BULK = "AWAITING_ZIP_FOR_BULK"
AWAITING_BULK_OPERATION = "AWAITING_BULK_OPERATION"
AWAITING_PDF_CONCATENATION_ORDER = "AWAITING_PDF_CONCATENATION_ORDER"

# Gemini operation states - removed, LLM only used for intent classification

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
