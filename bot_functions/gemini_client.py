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

async def generate_text(prompt: str, system_prompt: str = None) -> str:
    """Generate text using the Gemini model"""
    if not client:
        return "El servicio de Gemini no está configurado. Por favor, contacta al administrador del bot."
    try:
        # If system_prompt is provided, combine it with the user prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUsuario: {prompt}"
        else:
            full_prompt = prompt

        response = client.models.generate_content(
            model="gemma-3-27b-it",
            contents=full_prompt
        )
        return response.text
    except Exception as e:
        print(f"Error generating text with Gemini: {e}")
        return "Lo siento, ha ocurrido un error al procesar tu solicitud con Gemini."
