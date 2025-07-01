from langchain_together import ChatTogether
from langchain_core.messages import HumanMessage, SystemMessage
from candidate_agent.agent_tools import CandidateEvaluationAgent
from candidate_agent.config import TOGETHER_API_KEY
import logging
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ChatTogether model
chat_model = ChatTogether(
    together_api_key=TOGETHER_API_KEY,
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
)

# Initialize evaluation agent once (not per request)
evaluation_agent = CandidateEvaluationAgent(
    normalization_type="min_max",
    decision_threshold=6.0
)

def validate_candidate_data(candidate_data: Dict[str, Any]) -> bool:
    """Validate required fields in candidate data"""
    required_fields = [
        'resume_relevance_score',
        'skill_match', 
        'quiz_metrics',
        'proctoring_metrics',
        'interview_metrics'
    ]
    
    for field in required_fields:
        if field not in candidate_data:
            logger.error(f"Missing required field: {field}")
            return False
        
        if field == 'resume_relevance_score':
            if not isinstance(candidate_data[field], (int, float)) or not (0 <= candidate_data[field] <= 10):
                logger.error(f"resume_relevance_score must be a number between 0-10, got: {candidate_data[field]}")
                return False
        else:
            if not isinstance(candidate_data[field], list) or len(candidate_data[field]) == 0:
                logger.error(f"{field} must be a non-empty list, got: {candidate_data[field]}")
                return False
    
    return True

def evaluate_candidate_with_model(candidate_data: dict) -> Dict[str, Any]:
    """
    Enhanced candidate evaluation with error handling and validation
    """
    try:
        # Validate input data
        if not validate_candidate_data(candidate_data):
            return {
                "error": "Invalid input data. Please check all required fields.",
                "status": "error"
            }
        
        logger.info(f"Evaluating candidate with resume score: {candidate_data['resume_relevance_score']}")
        
        # Get algorithmic evaluation
        evaluation_result = evaluation_agent.evaluate(candidate_data)
        algorithmic_score = evaluation_result["score"]
        decision = evaluation_result["decision"]
        component_scores = evaluation_result["component_scores"]
        
        # Prepare enhanced prompt for LLM
        system_prompt = """You are an expert technical interviewer and HR specialist. 
        Analyze the candidate's performance across all evaluation metrics and provide:
        1. A detailed assessment of strengths and weaknesses
        2. A score from 1-10 that aligns with the algorithmic score
        3. Specific recommendations for next steps
        4. Risk factors to consider
        
        Be objective, specific, and actionable in your evaluation."""
        
        human_prompt = f"""
        **Candidate Evaluation Data:**
        
        Resume Relevance: {candidate_data['resume_relevance_score']}/10
        Quiz Accuracy: {candidate_data['quiz_metrics'][0]:.2f}
        Proctoring Suspicious Count: {candidate_data['proctoring_metrics'][0]:.2f}
        Interview Metrics:
        - Gaze Stability: {candidate_data['interview_metrics'][0]:.2f}
        - Expression Consistency: {candidate_data['interview_metrics'][1]:.2f}
        - Technical Depth: {candidate_data['interview_metrics'][2]:.2f}
        
        **Algorithmic Evaluation:**
        - Total Score: {algorithmic_score}/10
        - Decision: {decision}
        - Component Scores: {component_scores}
        
        Please provide a comprehensive evaluation that considers both the raw data and the algorithmic assessment.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        # Get LLM evaluation
        llm_result = chat_model.invoke(messages)
        
        # Return comprehensive result
        return {
            "status": "success",
            "algorithmic_score": algorithmic_score,
            "decision": decision,
            "component_scores": component_scores,
            "llm_evaluation": llm_result.content,
            "evaluation_summary": {
                "final_score": algorithmic_score,
                "recommendation": decision,
                "confidence": "high" if abs(algorithmic_score - 6.0) > 1.0 else "medium",
                "risk_factors": [
                    "Low proctoring compliance" if any(score < 0.5 for score in candidate_data['proctoring_metrics']) else None,
                    "Poor skill match" if any(score < 0.7 for score in candidate_data['skill_match']) else None,
                    "Weak interview performance" if any(score < 0.7 for score in candidate_data['interview_metrics']) else None
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}")
        return {
            "error": f"Evaluation failed: {str(e)}",
            "status": "error"
        } 