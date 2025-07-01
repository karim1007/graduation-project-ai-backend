from fastapi import FastAPI, HTTPException , APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from candidate_agent.code import evaluate_candidate_with_model
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router= APIRouter()

class CandidateData(BaseModel):
    resume_relevance_score: float = Field(..., ge=0, le=10, description="Resume relevance score (0-10)")
    quiz_accuracy: float = Field(..., ge=0, le=1, description="Quiz accuracy score (0-1)")
    proctor_suspicious_count: float = Field(..., ge=0, le=1, description="Proctoring suspicious count (0-1)")
    gaze_stability: float = Field(..., ge=0, le=1, description="Interview gaze stability score (0-1)")
    expression_consistency: float = Field(..., ge=0, le=1, description="Interview expression consistency score (0-1)")
    technical_depth_score: float = Field(..., ge=0, le=1, description="Interview technical depth score (0-1)")

@router.post("/evaluate_candidate/")
async def evaluate_candidate(candidate_data: CandidateData):
    """
    Enhanced endpoint to evaluate a candidate's profile with comprehensive analysis.
    
    Returns:
    - Algorithmic score and decision
    - LLM-generated detailed evaluation
    - Risk factors and confidence level
    - Component breakdown scores
    """
    try:
        logger.info("Received candidate evaluation request")
        
        # Convert Pydantic model to dict and restructure for the evaluation agent
        data_dict = candidate_data.model_dump()
        
        # Restructure data to match the expected format
        restructured_data = {
            "resume_relevance_score": data_dict["resume_relevance_score"],
            "skill_match": [0.5, 0.5],  # Default values since skills removed
            "quiz_metrics": [data_dict["quiz_accuracy"]],  # Only quiz accuracy
            "proctoring_metrics": [data_dict["proctor_suspicious_count"]],  # Only suspicious count
            "interview_metrics": [data_dict["gaze_stability"], data_dict["expression_consistency"], data_dict["technical_depth_score"]]
        }
        
        # Evaluate candidate
        result = evaluate_candidate_with_model(restructured_data)
        
        # Check for errors
        if result.get("status") == "error":
            logger.error(f"Evaluation failed: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        logger.info(f"Evaluation completed successfully. Score: {result.get('algorithmic_score')}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Candidate Evaluation API"}

@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Candidate Evaluation API",
        "version": "2.0.0",
        "endpoints": {
            "evaluate": "/evaluate_candidate/",
            "health": "/health",
            "docs": "/docs"
        }
    }
