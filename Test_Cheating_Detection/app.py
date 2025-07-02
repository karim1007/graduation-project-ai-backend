import time
import shutil

from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from Test_Cheating_Detection.detection import process_candidate_exam
from Test_Cheating_Detection.generate_pics_from_videos import extract_frames
router = APIRouter()

VIDEO_DIR = "Test_Cheating_Detection\\videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

@router.post("/check-cheating/")
async def upload_video(file: UploadFile = File(...), candidate_name: str = Form(...)):
    # Validate extension
    allowed_extensions = {".mp4", ".mov", ".avi", ".mkv"}
    ext = os.path.splitext(file.filename)[-1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported video format.")
    vid= candidate_name + ext
    print(vid)
    # Save with candidate name and UUID
    save_path = os.path.join(VIDEO_DIR, f"{vid}")
    print(save_path)
    with open(save_path, "wb") as buffer:
        buffer.write(await file.read())
    candidate_directory = os.path.join("Test_Cheating_Detection\\frames", candidate_name)
    # Extract frames from the uploaded video
    extract_frames(save_path, candidate_directory, 2)
    time.sleep(2)
    res=process_candidate_exam(candidate_name)
    print(res)
    time.sleep(3)
    shutil.rmtree("Test_Cheating_Detection\\frames")
    os.remove(save_path)
    return JSONResponse(content=res)
