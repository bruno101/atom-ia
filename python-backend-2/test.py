from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API"))

audio_path = r"C:\Users\bruno.barros\Downloads\Pobreza por Pobreza.mp3"

print("Uploading file...")
with open(audio_path, 'rb') as f:
    audio_file = client.files.upload(file=f, config={'mime_type': 'audio/mpeg'})

print(f"File uploaded: {audio_file.name}")

print("Generating summary...")
response = client.models.generate_content(
    model='gemini-2.0-flash-lite',
    contents=["Summarize this audio in Portuguese", audio_file]
)

print("\nSummary:")
print(response.text)

print("\nDeleting file...")
client.files.delete(name=audio_file.name)
print("Done!")
