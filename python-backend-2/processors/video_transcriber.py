import tempfile
import os
import subprocess
from google import genai
from dotenv import load_dotenv
import imageio_ffmpeg

load_dotenv()

def transcribe_video_with_gemini_stream(video_file):
    """Transcreve vídeo extraindo áudio e usando Gemini API com streaming"""
    print("[TRANSCRIBE] Iniciando transcrição de vídeo...")
    temp_path = None
    audio_path = None
    audio_upload = None
    client = None
    
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API"))
        print("[TRANSCRIBE] Cliente Gemini configurado")
        yield "Configurando cliente..."
        
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_file.write(video_file)
            temp_path = temp_file.name
        print(f"[TRANSCRIBE] Vídeo temporário criado: {temp_path}")
        yield "Vídeo preparado..."
        
        audio_path = temp_path.replace('.mp4', '.m4a')
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run([
            ffmpeg_exe, '-i', temp_path, '-vn', '-c:a', 'copy', '-y', audio_path
        ], check=True, capture_output=True)
        print(f"[TRANSCRIBE] Áudio extraído: {audio_path}")
        yield "Extraindo áudio..."
        
        os.unlink(temp_path)
        temp_path = None
        
        with open(audio_path, 'rb') as f:
            audio_upload = client.files.upload(file=f, config={'mime_type': 'audio/m4a'})
        print(f"[TRANSCRIBE] Upload concluído: {audio_upload.name}")
        yield "Upload concluído..."
        
        prompt = "Transcreva o áudio fornecido. Retorne apenas o texto transcrito, sem formatação adicional."
        
        print("[TRANSCRIBE] Iniciando geração de conteúdo com streaming...")
        yield "Iniciando transcrição..."
        
        response = client.models.generate_content_stream(
            model='gemini-2.0-flash-lite',
            contents=[prompt, audio_upload]
        )
        
        transcription = ""
        for chunk in response:
            if chunk.text:
                print(f"[TRANSCRIBE] Chunk recebido: {chunk.text[:50]}...")
                transcription += chunk.text
                yield chunk.text
        
        print("[TRANSCRIBE] Transcrição completa recebida")
        yield f"FINAL:{transcription.strip()}"
        
    except Exception as e:
        print(f"[TRANSCRIBE] Erro: {str(e)}")
        yield f"ERRO: {str(e)}"
    finally:
        if client and audio_upload:
            try:
                client.files.delete(name=audio_upload.name)
                print("[TRANSCRIBE] Arquivo remoto deletado")
            except:
                pass
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                print("[TRANSCRIBE] Vídeo temporário deletado")
            except PermissionError:
                pass
        if audio_path and os.path.exists(audio_path):
            try:
                os.unlink(audio_path)
                print("[TRANSCRIBE] Áudio temporário deletado")
            except PermissionError:
                pass
