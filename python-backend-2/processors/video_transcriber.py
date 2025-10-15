import tempfile
import os
import subprocess
from google import genai
from dotenv import load_dotenv
import imageio_ffmpeg

load_dotenv()

def transcribe_video_with_gemini(video_file):
    """Transcreve vídeo extraindo áudio e usando Gemini API"""
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API"))
        
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_file.write(video_file)
            temp_path = temp_file.name
        
        audio_path = temp_path.replace('.mp4', '.m4a')
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run([
            ffmpeg_exe, '-i', temp_path, '-vn', '-c:a', 'copy', '-y', audio_path
        ], check=True, capture_output=True)
        
        os.unlink(temp_path)
        
        with open(audio_path, 'rb') as f:
            audio_upload = client.files.upload(file=f, config={'mime_type': 'audio/m4a'})
        
        prompt = "Transcreva o áudio fornecido. Retorne apenas o texto transcrito, sem formatação adicional."
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=[prompt, audio_upload]
        )
        
        client.files.delete(name=audio_upload.name)
        os.unlink(audio_path)
        
        return response.text.strip()
        
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except PermissionError:
                pass
        if 'audio_path' in locals() and os.path.exists(audio_path):
            try:
                os.unlink(audio_path)
            except PermissionError:
                pass
        raise Exception(f"Erro ao transcrever vídeo: {str(e)}")
