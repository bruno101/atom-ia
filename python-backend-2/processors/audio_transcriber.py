import tempfile
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def transcribe_audio_with_gemini_stream(audio_file):
    """Transcreve áudio usando Gemini API com streaming"""
    print("[TRANSCRIBE] Iniciando transcrição de áudio...")
    temp_path = None
    audio_upload = None
    client = None
    
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API"))
        print("[TRANSCRIBE] Cliente Gemini configurado")
        yield "Configurando cliente..."
        
        with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as temp_file:
            temp_file.write(audio_file)
            temp_path = temp_file.name
        print(f"[TRANSCRIBE] Arquivo temporário criado: {temp_path}")
        yield "Arquivo preparado..."
        
        with open(temp_path, 'rb') as f:
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
        final_text = transcription.strip()
        print(f"[TRANSCRIBE] Final text length: {len(final_text)}")
        print(f"[TRANSCRIBE] Final text preview: {final_text[:200]}...")
        yield f"FINAL:{final_text}"
        
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
                print("[TRANSCRIBE] Arquivo local deletado")
            except PermissionError:
                pass
