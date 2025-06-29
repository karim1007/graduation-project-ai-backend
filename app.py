from fastapi import FastAPI
from candidate_eval.app import router as router1
from folder2.app import router as router2
from folder3.app import router as router3

app = FastAPI()

# Include routers with optional prefixes
app.include_router(router1, prefix="/f1")
app.include_router(router2, prefix="/f2")
app.include_router(router3, prefix="/f3")
