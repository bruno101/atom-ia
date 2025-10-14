import tempfile
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def transcribe_audio_with_gemini(audio_file):
    """Transcreve áudio usando Gemini API"""
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API"))
        
        with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as temp_file:
            temp_file.write(audio_file)
            temp_path = temp_file.name
        
        with open(temp_path, 'rb') as f:
            audio_upload = client.files.upload(file=f, config={'mime_type': 'audio/m4a'})
        
        prompt = "Transcreva o áudio fornecido. Retorne apenas o texto transcrito, sem formatação adicional."
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=[prompt, audio_upload]
        )
        
        client.files.delete(name=audio_upload.name)
        os.unlink(temp_path)
        
        return response.text.strip()
        
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except PermissionError:
                pass
        raise Exception(f"Erro ao transcrever áudio: {str(e)}")
