from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from Test_Cheating_Detection.detection import process_candidate_exam
router = APIRouter()

VIDEO_DIR = "Test-Cheating-Detection/content"
os.makedirs(VIDEO_DIR, exist_ok=True)

@router.post("/upload-video/")
async def upload_video(file: UploadFile = File(...), candidate_name: str = Form(...)):
    # Validate extension
    allowed_extensions = {".mp4", ".mov", ".avi", ".mkv"}
    ext = os.path.splitext(file.filename)[-1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported video format.")

    # Save with candidate name and UUID
    save_path = os.path.join(VIDEO_DIR, f"{ext}")

    with open(save_path, "wb") as buffer:
        buffer.write(await file.read())

    return JSONResponse(content={
        "message": "Video uploaded successfully.",
        "candidate_name": candidate_name,
        "filename": file.filename,
        "saved_as": os.path.basename(save_path),
        "path": save_path
    })
