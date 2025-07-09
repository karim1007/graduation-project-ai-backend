import whisper
import tempfile
import shutil
from fastapi import UploadFile
import os
# Load Whisper model once at module level

from dotenv import load_dotenv
load_dotenv()
Eleven_API_KEY = os.getenv("ELEVEN_API_KEY")
model = whisper.load_model("base")  # or "small", "medium", "large"

# def transcribe_mp3(uploaded_file: UploadFile) -> str:
#     # Save the file to a temporary path
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
#         shutil.copyfileobj(uploaded_file.file, tmp)
#         temp_file_path = tmp.name

#     # Transcribe using Whisper
#     result = model.transcribe(temp_file_path)

#     # Optional: clean up temp file
#     os.remove(temp_file_path)

#     return result["text"]

def transcribe_mp3(video_path: str) -> str:
    model = whisper.load_model("base")  # or "small", "medium", "large"
    result = model.transcribe(video_path)
    return result["text"]


from elevenlabs.client import ElevenLabs
from elevenlabs import play
import base64

client = ElevenLabs(api_key=Eleven_API_KEY)

def synthesize_and_encode_audio(
    text: str,
    voice_id: str = "ThT5KcBeYPX3keUQqHPh",
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
) -> str:
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        output_format=output_format,
    )
    audio_bytes = b''.join(audio)
    encoded_audio = base64.b64encode(audio_bytes).decode("utf-8")
    return encoded_audio