import whisper
import tempfile
import shutil
from fastapi import UploadFile
import os
# Load Whisper model once at module level
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
