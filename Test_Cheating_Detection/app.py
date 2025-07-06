import time
import shutil

from fastapi import APIRouter, Form, UploadFile, File, HTTPException, FastAPI
from fastapi.responses import JSONResponse
import os
import uuid
from Test_Cheating_Detection.detection import process_candidate_exam
from Test_Cheating_Detection.generate_pics_from_videos import extract_frames
from fastapi.middleware.cors import CORSMiddleware

router = APIRouter()

VIDEO_DIR = "Test_Cheating_Detection\\videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

@router.post("/check-cheating/")
async def upload_video(file: UploadFile = File(...), candidate_name: str = Form(...)):
    # Validate extension
    allowed_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
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
    path = "Test_Cheating_Detection\\frames" if os.name == "nt" else "Test_Cheating_Detection/frames"
    candidate_directory = os.path.join(path, candidate_name)
    # Extract frames from the uploaded video
    extract_frames(save_path, candidate_directory, 2)
    time.sleep(2)
    res=process_candidate_exam(candidate_name)
    print(res)
    time.sleep(3)
    shutil.rmtree(path)
    os.remove(save_path)
    return JSONResponse(content=res)

app = FastAPI()
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
