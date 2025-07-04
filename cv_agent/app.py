from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import uuid
import os
from cv_agent.cv_processor import extract_text_from_pdf, index_resume_to_pinecone
from cv_agent.agent import choose_best_candiate
from fastapi import APIRouter
from cv_agent.agent import generate_job_detailss
router = APIRouter()

@router.post("/upload-resume_to_pinecone/")
async def upload_pdf(
    file: UploadFile = File(...),
    id_key: str = Form(...)  # Form field required
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    temp_path = f"temp_{id_key}.pdf"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        text = extract_text_from_pdf(temp_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="PDF has no extractable text.")

        doc_id = index_resume_to_pinecone(doc_id=id_key, filename=file.filename, text=text)

        return JSONResponse(content={
            "message": "Resume uploaded and indexed successfully.",
            "pinecone_id": doc_id
        })

    finally:
        os.remove(temp_path)


@router.post("/choose_best_resume/")
async def choose_best_resume(request_body: dict):
    job_description = request_body.get("job_description")
    if not job_description:
        raise HTTPException(status_code=400, detail="Job description is required")
    summary = choose_best_candiate(job_description)

    return JSONResponse(content=
        summary
    )

@router.post("/generate_job_details/")
async def generate_job_details(request_body: dict):
    try:
        job_title = request_body.get("job_title")
        department = request_body.get("department")
        employment_type = request_body.get("employment_type")
        experience_level = request_body.get("experience_level")

        if not all([job_title, department, employment_type, experience_level]):
            raise HTTPException(status_code=400, detail="Missing required fields")

        result = generate_job_detailss(
            job_title=job_title,
            department=department,
            employment_type=employment_type,
            experience_level=experience_level
        )
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(router, host="0.0.0.0", port=8000)
