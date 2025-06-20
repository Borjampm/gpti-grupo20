import os
from google import genai
from dotenv import load_dotenv

# Configure the Gemini API client
try:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
except KeyError:
    # Handle the case where the API key is not set
    client = None

async def generate_text(prompt: str) -> str:
    """Generate text using the Gemini model"""
    if not client:
        return "El servicio de Gemini no está configurado. Por favor, contacta al administrador del bot."
    try:
        response = client.models.generate_content(
            model="gemma-3-27b-it",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error generating text with Gemini: {e}")
        return "Lo siento, ha ocurrido un error al procesar tu solicitud con Gemini."
