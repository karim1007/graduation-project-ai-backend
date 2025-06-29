from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from question_and_answer_agent.search_and_filter_agent import generate_questions
from fastapi import APIRouter

router = APIRouter()

@router.post("/generate-questions")
async def generate_question(request: Request):
    data = await request.json()
    job_description = data.get("job_description")
    num_questions = data.get("num_questions", 1)
    num_questions = int(num_questions) if isinstance(num_questions, str) else num_questions
    # Basic validation
    if not job_description or not isinstance(num_questions, int):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid input. Must provide job_description (str) and num_questions (int)."}
        )
    result = generate_questions(job_description, num_questions)
    return JSONResponse(content=result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(router, host="0.0.0.0", port=8000)