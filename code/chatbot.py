import base64 #encode l'image en base64 pour transmission via l'API.
import requests #envoie des requêtes HTTP à l'API
import io #gère des flux en mémoire (pour lire l'image depuis un buffer)
from PIL import Image #Ouvre et vérifie la validité de l'image.
from dotenv import load_dotenv # charge des variables d'environnement depuis un fichier .env
import os
import logging #affiche des logs (informations, erreurs, etc.).

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
GROQ_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)
GROQ_API_KEY = os.getenv("GEMINI_API_KEY")


def process_image(image_path, query):
    """
    Process an image using the Groq API with the provided query.
    
    Args:
        image_path (str): Path to the image file
        query (str): The query text to send with the image
        
    Returns:
        dict: A dictionary containing either the answer or an error message
    """
    if not GROQ_API_KEY:
        logger.warning("GROQ API KEY is not set in the environment variables")
        return {"error": "API key not configured. Please contact the administrator."}
    
    #Read and encode the image
    try:
        with open(image_path, "rb") as image_file:
            image_content = image_file.read()
            encoded_image = base64.b64encode(image_content).decode("utf-8")
        
        # Verify image is valid
        try:  
            img = Image.open(io.BytesIO(image_content))
            img.verify()
        except Exception as e:
            logger.error(f"Invalid image format: {str(e)}")
            return {"error": f"Invalid image format: {str(e)}"} 
        
        # Create message structure for API with:
        # - text query
        # - base64 encoded image
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]
            }
        ]
        
        # Send POST request to API with:
        # - model selection
        # - message (text + image)
        # - max tokens for response
        # - authorization headers (with API key)
        # - 30 second timeout
        model = "meta-llama/llama-4-scout-17b-16e-instruct"
        try:
            response = requests.post(
                GROQ_API_URL,
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 1000
                },
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}", 
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                logger.info(f"Processed response from API")
                return {"answer": answer}
            else:
                error_msg = f"Error from API: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            return {"error": f"API request failed: {str(e)}"}
                
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return {"error": f"An unexpected error occurred: {str(e)}"}
