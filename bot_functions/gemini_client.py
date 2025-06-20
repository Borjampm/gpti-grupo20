import os
import google.generativeai as genai

# Configure the Gemini API client
try:
    client = genai.configure(api_key=os.environ["GEMINI_API_KEY"])
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
