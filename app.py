from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cv_agent.app import router as router1
from question_and_answer_agent.app import router as router2
from interview_agent.app import router as router3
from Test_Cheating_Detection.app import router as router4
from candidate_agent.app import router as router5

app = FastAPI()

# Add CORS middleware before including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:3000"] for Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with optional prefixes
app.include_router(router1, prefix="/cv-agent")
app.include_router(router2, prefix="/exam-generation-agent")
app.include_router(router3, prefix="/interview-agent")
app.include_router(router4, prefix="/proctor-agent")
app.include_router(router5, prefix="/candidate-agent")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
