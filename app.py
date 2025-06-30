from fastapi import FastAPI
from candiate_eval.app import router as router1
from question_and_answer_agent.app import router as router2
from interview_agent.app import router as router3
from Test_Cheating_Detection.app import router as router4
app = FastAPI()

# Include routers with optional prefixes
app.include_router(router1, prefix="/cv-agent")
app.include_router(router2, prefix="/exam-generation-agent")
app.include_router(router3, prefix="/interview-agent")
app.include_router(router4, prefix="/proctor-agent")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
