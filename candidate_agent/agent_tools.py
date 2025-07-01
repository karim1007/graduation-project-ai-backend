# class CandidateEvaluationAgent:
#     def __init__(self, weight_technical=0.5, weight_soft_skills=0.3, weight_experience=0.1, weight_proctoring=0.1):
#         self.weights = {
#             "technical": weight_technical,
#             "soft_skills": weight_soft_skills,
#             "experience": weight_experience,
#             "proctoring": weight_proctoring
#         }

#     def evaluate(self, candidate_data):
#         # Ensure all values are numeric (float or int) and properly handle False/True as 0/1
#         technical_score = float(candidate_data.get('technical', 0))  
#         soft_skills_score = float(candidate_data.get('soft_skills', 0))  
#         experience_score = float(candidate_data.get('experience', 0))  
#         proctoring_score = 1 if candidate_data.get('proctoring', False) else 0  

#         # Optional: Add logging to check if values are normalized correctly
#         print(f"Normalized Scores - Technical: {technical_score}, Soft Skills: {soft_skills_score}, Experience: {experience_score}, Proctoring: {proctoring_score}")

#         # Calculate the total score using weighted sum
#         total_score = (
#             technical_score * self.weights["technical"] +
#             soft_skills_score * self.weights["soft_skills"] +
#             experience_score * self.weights["experience"] +
#             proctoring_score * self.weights["proctoring"]
#         )

#         # Round the total score to 2 decimal places
#         total_score = round(total_score, 2)
#         return total_score
import numpy as np

class CandidateEvaluationAgent:
    def __init__(self, 
                 weight_resume_relevance=0.1, 
                 weight_skill_match=0.1, 
                 weight_quiz=0.1, 
                 weight_proctoring=0.1,
                 weight_interview=0.4, 
                 normalization_type="min_max",
                 decision_threshold=6.0):  # Added decision threshold parameter 
        # Set weights for the features
        self.weights = {
            "resume_relevance": weight_resume_relevance,
            "skill_match": weight_skill_match,
            "quiz": weight_quiz,
            "proctoring": weight_proctoring,
            "interview": weight_interview
        }
        self.normalization_type = normalization_type
        self.decision_threshold = decision_threshold  

   

    def normalize_data(self, candidate_data):
        """
        No normalization: just return the values as-is, with resume_relevance_score divided by 10.
        """
        normalized_scores = []
        # Resume relevance (0-10 scale, convert to 0-1)
        normalized_scores.append(candidate_data['resume_relevance_score'] / 10.0)
        # Skill match (already 0-1)
        normalized_scores.extend(candidate_data['skill_match'])
        # Quiz metrics (already 0-1)
        normalized_scores.extend(candidate_data['quiz_metrics'])
        # Proctoring metrics (already 0-1)
        normalized_scores.extend(candidate_data['proctoring_metrics'])
        # Interview metrics (already 0-1)
        normalized_scores.extend(candidate_data['interview_metrics'])
        return np.array(normalized_scores)

    def make_decision(self, score):
        """
        Decision logic to determine whether the candidate is shortlisted or rejected.
        Uses the final scaled score (0-10 range) to make the decision.
        """
        # Score is already in 0-10 range from evaluate() method
        if score >= self.decision_threshold:
            return "Shortlisted"
        else:
            return "Rejected"

    def evaluate(self, candidate_data):
        """
        This function evaluates the candidate's profile and generates a score using weighted sums,
        after applying the specified normalization to the features.
        """
        # Normalize the candidate data (all the features)
        normalized_scores = self.normalize_data(candidate_data)
        
        # Calculate weighted scores for each feature group
        resume_score = normalized_scores[0] * 10 * self.weights["resume_relevance"]  # Scale to 0-10
        
        # Calculate skill match score (average of normalized skill match scores)
        skill_match_scores = normalized_scores[1:len(candidate_data['skill_match'])+1]
        skill_match_score = np.mean(skill_match_scores) * 10 * self.weights["skill_match"]
        
        # Calculate quiz score (average of normalized quiz metrics)
        quiz_start_idx = len(candidate_data['skill_match']) + 1
        quiz_end_idx = quiz_start_idx + len(candidate_data['quiz_metrics'])
        quiz_scores = normalized_scores[quiz_start_idx:quiz_end_idx]
        quiz_score = np.mean(quiz_scores) * 10 * self.weights["quiz"]
        
        # Calculate proctoring score (average of normalized proctoring metrics)
        proctoring_start_idx = quiz_end_idx
        proctoring_end_idx = proctoring_start_idx + len(candidate_data['proctoring_metrics'])
        proctoring_scores = normalized_scores[proctoring_start_idx:proctoring_end_idx]
        proctoring_score = np.mean(proctoring_scores) * 10 * self.weights["proctoring"]
        
        # Calculate interview score (average of normalized interview metrics)
        interview_scores = normalized_scores[proctoring_end_idx:]
        interview_score = np.mean(interview_scores) * 10 * self.weights["interview"]
        
        # Calculate total score as sum of all weighted scores
        total_score = (
            resume_score +
            skill_match_score +
            quiz_score +
            proctoring_score +
            interview_score
        )
        
        total_score = round(total_score, 2)
        
        # Make the decision based on the score
        decision = self.make_decision(total_score)
        
        # Create a detailed evaluation result with component scores
        component_scores = {
            "resume_relevance": round(resume_score, 2)/10,
            "skill_match": round(skill_match_score, 2)/10,
            "quiz": round(quiz_score, 2)/10,
            "proctoring": round(proctoring_score, 2)/10,
            "interview": round(interview_score, 2)/10
        }
        total_score = total_score / 10  # Scale total score to 0-10 range
        evaluation_result = {
            "evaluation_result": f"""**Detailed Evaluation:**

Component Scores:
- Resume Relevance: {component_scores['resume_relevance']}
- Skill Match: {component_scores['skill_match']}
- Quiz Performance: {component_scores['quiz']}
- Proctoring: {component_scores['proctoring']}
- Interview: {component_scores['interview']}

The candidate's resume relevance score is {candidate_data['resume_relevance_score']}, indicating a moderate level of alignment between their experience and the job requirements. The skill match scores are generally high, with an average of {np.mean(candidate_data['skill_match'])}. The candidate's performance in the quiz is strong, demonstrating technical knowledge and quick problem-solving ability.

The proctoring metrics suggest that the candidate is honest and compliant. The interview metrics provide a more nuanced view, indicating strengths in gaze stability and expression consistency, but weaknesses in fluency, sentiment, and technical depth.

**Final Score: {total_score}**

**Recommendation:** {decision}""",
            "score": total_score,
            "decision": decision,
            "component_scores": component_scores
        }

        return evaluation_result
