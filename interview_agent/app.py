from unittest import result
from fastapi import APIRouter, Request, File, UploadFile
from fastapi.responses import JSONResponse
from interview_agent.technical_depth_analysis import run_exam_pipeline
from interview_agent.speech_to_text import synthesize_and_encode_audio, transcribe_mp3
from interview_agent.emotion import analyze_emotional_state
from interview_agent.pixtral import analyze_with_pixtral_model
from interview_agent.report import analyze_video_workflow
import shutil
import os
router = APIRouter()

@router.post("/transcribe-audio")
async def transcribe_audio(file: UploadFile = File(...)):
    text = transcribe_mp3(file)

    return {"transcription": text}

@router.post("/text-to-speech")
async def text_to_speech(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text or not isinstance(text, str):
        return JSONResponse(
            status_code=400,
            content={"error": "A valid 'text' field is required."}
        )
    # Assuming you have a function called synthesize_speech(text) that returns audio bytes
    audio_bytes = synthesize_and_encode_audio(text)
    return JSONResponse(
        content={"audio": audio_bytes}
    )

@router.post("/evaluate-exam")
async def evaluate(request: Request):
    data = await request.json()
    
    question_list = data.get("question_list")
    answer_list = data.get("answer_list")
    golden_answer_list = data.get("golden_answer_list")
    
    # Basic validation
    if not all(isinstance(lst, list) for lst in [question_list, answer_list, golden_answer_list]):
        return JSONResponse(
            status_code=400,
            content={"error": "All inputs must be lists of strings."}
        )
    
    if not (len(question_list) == len(answer_list) == len(golden_answer_list)):
        return JSONResponse(
            status_code=400,
            content={"error": "All lists must have the same length."}
        )

    result = run_exam_pipeline(
        question_list=question_list,
        golden_answers_list=golden_answer_list,
        candidate_answers=answer_list
    )

    return JSONResponse(content=result)

@router.post("/emotional-analysis")
async def emotional_analysis(file: UploadFile = File(...)):
    # Save the uploaded video file to disk or process as needed
    contents = await file.read()
    file_location = "interview_agent/video.mp4"
    with open(file_location, "wb") as f:
        f.write(contents)
    video_path = file_location
    analyze_emotional_state(video_path, frame_interval=2)
    result= analyze_with_pixtral_model("interview_agent/output")
    shutil.rmtree("interview_agent/output", ignore_errors=True)
    os.remove(video_path)
    return JSONResponse(content={
        "message": "Emotional analysis completed successfully.",
        "result": result
    })


@router.post("/interview-analysis")
async def interview_analysis(file: UploadFile = File(...)):
    # Save the uploaded video file to disk or process as needed
    contents = await file.read()
    file_location = "interview_agent/video.mp4"
    with open(file_location, "wb") as f:
        f.write(contents)
    video_path = file_location
    result = analyze_video_workflow(video_path)
    shutil.rmtree("interview_agent/output", ignore_errors=True)
    os.remove(video_path)
    
    return JSONResponse(content={
        "message": "Interview analysis completed successfully.",
        "result": result
    })
