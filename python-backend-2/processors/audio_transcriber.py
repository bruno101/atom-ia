import tempfile
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def transcribe_audio_with_gemini(audio_file):
    """Transcreve áudio usando Gemini API"""
    try:
        genai.configure(api_key=os.getenv("GEMINI_API"))
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as temp_file:
            temp_file.write(audio_file)
            temp_path = temp_file.name
        
        audio_upload = genai.upload_file(temp_path)
        
        prompt = "Transcreva o áudio fornecido. Retorne apenas o texto transcrito, sem formatação adicional."
        
        response = model.generate_content([prompt, audio_upload])
        os.unlink(temp_path)
        
        return response.text.strip()
        
    except Exception as e:
        if 'temp_path' in locals():
            os.unlink(temp_path)
        raise Exception(f"Erro ao transcrever áudio: {str(e)}")
