from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from interview_agent.technical_depth_analysis import run_exam_pipeline
router = APIRouter()

@router.post("/evaluate")
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
