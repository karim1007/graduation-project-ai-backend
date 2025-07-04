# Fixed Enhanced Interview Analysis System
# Install required packages:
# pip install langchain-openai langchain-community langchain-core pydantic

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
import os
import json
from datetime import datetime

# Set your API key
from dotenv import load_dotenv
load_dotenv()

# ========== Step 1: Define Simplified Structured Output Models ==========
class EmotionalIndicator(BaseModel):
    emotion: str = Field(description="The specific emotion detected")
    intensity: float = Field(description="Intensity level from 0.0 to 1.0", ge=0.0, le=1.0)
    evidence: str = Field(description="Textual evidence supporting this emotion")

class CommunicationPattern(BaseModel):
    pattern_type: str = Field(description="Type of communication pattern")
    frequency: str = Field(description="How often this pattern occurs (Low/Medium/High)")
    examples: List[str] = Field(description="Specific examples from the transcript")
    impact_score: float = Field(description="Impact on overall communication effectiveness (0.0-1.0)", ge=0.0, le=1.0)

class CompetencyAssessment(BaseModel):
    competency: str = Field(description="Name of the competency")
    score: float = Field(description="Score from 0.0 to 1.0", ge=0.0, le=1.0)
    evidence: List[str] = Field(description="Supporting evidence from transcript")
    development_areas: List[str] = Field(description="Areas for improvement")

class LanguageMetrics(BaseModel):
    vocabulary_complexity: float = Field(description="Complexity of vocabulary used (0.0-1.0)", ge=0.0, le=1.0)
    sentence_structure_variety: float = Field(description="Variety in sentence structures (0.0-1.0)", ge=0.0, le=1.0)
    filler_word_frequency: float = Field(description="Frequency of filler words (0.0-1.0)", ge=0.0, le=1.0)
    articulation_clarity: float = Field(description="Clarity of articulation (0.0-1.0)", ge=0.0, le=1.0)
    pace_consistency: float = Field(description="Consistency of speaking pace (0.0-1.0)", ge=0.0, le=1.0)

class InterviewAnalysisResult(BaseModel):
    # Overall Assessment
    overall_sentiment: str = Field(description="Overall sentiment: positive, neutral, or negative")
    confidence_level: float = Field(description="Overall confidence level (0.0-1.0)", ge=0.0, le=1.0)
    interview_effectiveness: float = Field(description="Overall interview performance (0.0-1.0)", ge=0.0, le=1.0)
    
    # Emotional Analysis
    primary_emotions: List[EmotionalIndicator] = Field(description="Primary emotions detected throughout interview")
    emotional_stability: float = Field(description="Emotional stability score (0.0-1.0)", ge=0.0, le=1.0)
    stress_indicators: List[str] = Field(description="Signs of stress or anxiety")
    
    # Communication Analysis
    communication_style: str = Field(description="Dominant communication style")
    communication_patterns: List[CommunicationPattern] = Field(description="Identified communication patterns")
    language_metrics: LanguageMetrics = Field(description="Detailed language usage metrics")
    
    # Competency Assessment
    core_competencies: List[CompetencyAssessment] = Field(description="Assessment of key competencies")
    soft_skills_score: float = Field(description="Overall soft skills score (0.0-1.0)", ge=0.0, le=1.0)
    leadership_potential: float = Field(description="Leadership potential score (0.0-1.0)", ge=0.0, le=1.0)
    
    # Behavioral Insights
    behavioral_patterns: List[str] = Field(description="Notable behavioral patterns")
    adaptability_score: float = Field(description="Adaptability score (0.0-1.0)", ge=0.0, le=1.0)
    problem_solving_approach: str = Field(description="Observed problem-solving approach")
    
    # Red Flags and Strengths
    red_flags: List[str] = Field(description="Potential concerns or red flags")
    key_strengths: List[str] = Field(description="Key strengths identified")
    
    # Recommendations
    hiring_recommendation: str = Field(description="Strong Hire, Hire, No Hire, or Strong No Hire")
    confidence_in_recommendation: float = Field(description="Confidence in hiring recommendation (0.0-1.0)", ge=0.0, le=1.0)
    development_recommendations: List[str] = Field(description="Specific development recommendations")
    follow_up_questions: List[str] = Field(description="Suggested follow-up questions for future interviews")
    
    # Detailed Insights
    personality_traits: Dict[str, float] = Field(description="Big Five personality traits scores")
    cultural_fit_indicators: List[str] = Field(description="Indicators of cultural fit")
    growth_potential: float = Field(description="Assessed growth potential (0.0-1.0)", ge=0.0, le=1.0)

# ========== Step 2: Set up the model with correct name ==========
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.1)

# ========== Step 3: Advanced Text Splitting ==========
def split_text_advanced(long_text: str) -> List[Document]:
    """Split text into manageable chunks"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=300,
        separators=["\n\nINTERVIEWER:", "\n\nCANDIDATE:", "\n\n", "\n", " ", ""]
    )
    docs = splitter.create_documents([long_text])
    return docs

# ========== Step 4: Create Enhanced Analysis Chain ==========
def create_analysis_chain():
    """Create the analysis chain with proper error handling"""
    
    # Set up the parser
    parser = PydanticOutputParser(pydantic_object=InterviewAnalysisResult)
    
    # Create the prompt template
    prompt = PromptTemplate(
        template="""
You are an expert behavioral psychologist and HR professional. Analyze the following interview transcript and provide a comprehensive, structured assessment.

CRITICAL: You MUST provide values for ALL required fields in the exact JSON format specified. Do not omit any fields.

Interview Transcript:
{text}

ANALYSIS REQUIREMENTS:

1. EMOTIONAL ANALYSIS:
   - Identify 3-5 primary emotions with specific evidence from the transcript
   - Assess emotional stability throughout the interview
   - Note any stress indicators or anxiety signs

2. COMMUNICATION ASSESSMENT:
   - Determine dominant communication style (e.g., "Confident and articulate", "Hesitant but thoughtful", "Direct and concise")
   - Identify 2-3 communication patterns with examples
   - Rate language metrics on technical complexity, clarity, and pace

3. COMPETENCY EVALUATION:
   - Assess 4-6 key competencies (e.g., Problem Solving, Leadership, Technical Skills, Communication)
   - Provide specific evidence for each competency score
   - Suggest development areas

4. BEHAVIORAL INSIGHTS:
   - Note 3-5 behavioral patterns observed
   - Assess adaptability and problem-solving approach
   - Evaluate leadership potential

5. RECOMMENDATIONS:
   - Provide clear hiring recommendation with confidence level
   - Suggest 3-5 development recommendations
  

6. PERSONALITY & FIT:
   - Rate Big Five traits: openness, conscientiousness, extraversion, agreeableness, neuroticism (0.0-1.0)
   - Identify cultural fit indicators
   - Assess growth potential

IMPORTANT: 
- All scores must be between 0.0 and 1.0
- Provide specific evidence from the transcript for all assessments
- If information is not available, make reasonable inferences based on available data
- Ensure all required fields are filled with appropriate values

{format_instructions}

Remember: Provide complete, structured analysis with all required fields filled.
""",
        input_variables=["text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Create the chain using the new syntax
    chain = prompt | llm | parser
    
    return chain

# ========== Step 5: Main Analysis Function ==========
def analyze_interview_advanced(interview_text: str, save_to_file: bool = True) -> InterviewAnalysisResult:
    """
    Perform comprehensive interview analysis with structured output
    
    Args:
        interview_text: The complete interview transcript
        save_to_file: Whether to save results to JSON file
    
    Returns:
        InterviewAnalysisResult: Structured analysis results
    """
    try:
        print("Creating analysis chain...")
        chain = create_analysis_chain()
        
        print("Processing interview text...")
        # For long texts, we'll combine chunks or process the full text directly
        if len(interview_text) > 10000:
            # Split into chunks and analyze the most relevant parts
            docs = split_text_advanced(interview_text)
            # Take first few chunks that contain the most interaction
            combined_text = "\n\n".join([doc.page_content for doc in docs[:3]])
        else:
            combined_text = interview_text
        
        print("Running analysis...")
        # Run the analysis
        result = chain.invoke({"text": combined_text})
        
        print("Analysis completed successfully!")
        
        # Save to file if requested
        if save_to_file:
            output_file = f'interview_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result.dict(), f, indent=2, ensure_ascii=False)
            print(f"Results saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        # Return a basic fallback analysis
        return create_fallback_analysis(interview_text)

# ========== Step 6: Fallback Analysis Function ==========
def create_fallback_analysis(interview_text: str) -> InterviewAnalysisResult:
    """Create a basic fallback analysis if the main analysis fails"""
    
    return InterviewAnalysisResult(
        overall_sentiment="neutral",
        confidence_level=0.5,
        interview_effectiveness=0.6,
        primary_emotions=[
            EmotionalIndicator(
                emotion="neutral",
                intensity=0.5,
                evidence="Analysis could not be completed due to parsing error"
            )
        ],
        emotional_stability=0.5,
        stress_indicators=["Unable to analyze due to technical error"],
        communication_style="Unable to determine",
        communication_patterns=[
            CommunicationPattern(
                pattern_type="Unknown",
                frequency="Unknown",
                examples=["Analysis incomplete"],
                impact_score=0.5
            )
        ],
        language_metrics=LanguageMetrics(
            vocabulary_complexity=0.5,
            sentence_structure_variety=0.5,
            filler_word_frequency=0.5,
            articulation_clarity=0.5,
            pace_consistency=0.5
        ),
        core_competencies=[
            CompetencyAssessment(
                competency="Overall Assessment",
                score=0.5,
                evidence=["Unable to complete full analysis"],
                development_areas=["Recommend manual review"]
            )
        ],
        soft_skills_score=0.5,
        leadership_potential=0.5,
        behavioral_patterns=["Analysis incomplete"],
        adaptability_score=0.5,
        problem_solving_approach="Unable to determine",
        red_flags=["Technical analysis error - recommend manual review"],
        key_strengths=["Unable to determine"],
        hiring_recommendation="No Hire",
        confidence_in_recommendation=0.1,
        development_recommendations=["Recommend manual interview review"],
        personality_traits={
            "openness": 0.5,
            "conscientiousness": 0.5,
            "extraversion": 0.5,
            "agreeableness": 0.5,
            "neuroticism": 0.5
        },
        cultural_fit_indicators=["Unable to determine"],
        growth_potential=0.5
    )

# ========== Step 7: Results Formatting ==========
def format_analysis_report(result: InterviewAnalysisResult) -> str:
    """Format the analysis result into a clear, tidy report"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# INTERVIEW ANALYSIS REPORT",
        f"Generated on: {timestamp}",
        "",
        "## EXECUTIVE SUMMARY",
        f"- **Effectiveness**: {result.interview_effectiveness:.1%}",
        f"- **Confidence Level**: {result.confidence_level:.1%}",
        f"- **Hiring Recommendation**: {result.hiring_recommendation} ({result.confidence_in_recommendation:.1%})",
        "",
        "## EMOTIONAL INSIGHTS",
        f"- **Overall Sentiment**: {result.overall_sentiment}",
        f"- **Emotional Stability**: {result.emotional_stability:.1%}",
    ]

    lines.append("- **Primary Emotions:**")
    for e in result.primary_emotions[:3]:
        lines.append(f"  • {e.emotion} ({e.intensity:.1%}) – {e.evidence}")
    if result.stress_indicators:
        lines.append(f"- **Stress Indicators**: {', '.join(result.stress_indicators[:3])}")

    lines.extend([
        "",
        "## COMMUNICATION SKILLS",
        f"- **Style**: {result.communication_style}",
        f"- **Vocabulary Complexity**: {result.language_metrics.vocabulary_complexity:.1%}",
        f"- **Articulation Clarity**: {result.language_metrics.articulation_clarity:.1%}",
        f"- **Filler Word Frequency**: {result.language_metrics.filler_word_frequency:.1%}",
        f"- **Pace Consistency**: {result.language_metrics.pace_consistency:.1%}",
        "",
        "## COMPETENCIES",
    ])
    for c in result.core_competencies:
        lines.append(f"- **{c.competency}**: {c.score:.1%}")
    lines.extend([
        f"- **Soft Skills**: {result.soft_skills_score:.1%}",
        f"- **Leadership Potential**: {result.leadership_potential:.1%}",
        f"- **Adaptability**: {result.adaptability_score:.1%}",
        f"- **Growth Potential**: {result.growth_potential:.1%}",
        "",
        "## STRENGTHS",
    ])
    for s in result.key_strengths[:5]:
        lines.append(f"• {s}")
    lines.append("")
    lines.append("## DEVELOPMENT RECOMMENDATIONS")
    for d in result.development_recommendations[:5]:
        lines.append(f"• {d}")
    if result.red_flags:
        lines.append("")
        lines.append("## RED FLAGS")
        for r in result.red_flags:
            lines.append(f"• {r}")
    lines.extend([
        "",
        "## PERSONALITY TRAITS (Big Five)",
        f"- **Openness**: {result.personality_traits.get('openness', 0):.1%}",
        f"- **Conscientiousness**: {result.personality_traits.get('conscientiousness', 0):.1%}",
        f"- **Extraversion**: {result.personality_traits.get('extraversion', 0):.1%}",
        f"- **Agreeableness**: {result.personality_traits.get('agreeableness', 0):.1%}",
        f"- **Neuroticism**: {result.personality_traits.get('neuroticism', 0):.1%}",
        "",
        "## BEHAVIORAL PATTERNS",
    ])
    for b in result.behavioral_patterns[:5]:
        lines.append(f"• {b}")
    lines.extend([
        "",
        "## FOLLOW-UP QUESTIONS",
    ])
    for i, q in enumerate(result.follow_up_questions[:5], 1):
        lines.append(f"{i}. {q}")
    
    return "\n".join(lines)


# ========== Step 8: Simple Analysis Function (Alternative) ==========
def analyze_interview_simple(interview_text: str) -> dict:
    """
    Simplified analysis function that returns a dictionary instead of structured object
    Use this if Pydantic parsing continues to fail
    """
    
    simple_prompt = PromptTemplate(
        template="""
Analyze this interview transcript and provide a structured assessment:

{text}

Provide your analysis in the following format:
- Overall Sentiment: [positive/neutral/negative]
- Confidence Level: [0.0-1.0]
- Key Strengths: [list 3-5 strengths]
- Areas for Improvement: [list 3-5 areas]
- Hiring Recommendation: [Strong Hire/Hire/No Hire/Strong No Hire]
- Confidence in Recommendation: [0.0-1.0]

Be specific and provide evidence from the transcript.
""",
        input_variables=["text"]
    )
    
    chain = simple_prompt | llm
    result = chain.invoke({"text": interview_text})
    
    return {"analysis": result.content}

# ========== Example Usage ==========
if __name__ == "__main__":
    # Test with a shorter, more manageable sample
    sample_interview = """
    James: "Let's dive into some technical areas. Can you explain the difference between SQL and NoSQL databases, and when you might use each?"
Sarah: "Oh, absolutely! So SQL databases are... well, they use SQL, which is the structured query language. They're really good for when you need to store data in a structured way. NoSQL is more flexible – it's like, when you don't need the structure as much?
I've mainly worked with MySQL in my projects, and it's been great for storing user information and things like that. NoSQL is newer, I think, and it's good for... um... bigger applications? I know MongoDB is a popular one, though I haven't used it personally yet. But I'm definitely eager to learn! I'm always excited to pick up new technologies."
[Vague, imprecise explanations showing limited understanding of fundamental concepts]
James: "Okay, let's try a coding question. Could you write a function that finds the second largest number in an array?"
Sarah: (brightening up) "Sure! I love problem-solving challenges. Let me think through this step by step..."
(writes on whiteboard)
javascriptfunction findSecondLargest(arr) {
    arr.sort();
    return arr[arr.length - 2];
}
"So I'd sort the array first, and then just grab the second-to-last element. That should give us the second largest number!"
James: "What if the array has duplicate values, like [5, 5, 3, 1]?"
Sarah: (pausing, looking uncertain) "Oh... hmm. That's a good point. Maybe I could... remove duplicates first? Or... actually, I'm not sure how to handle that case efficiently. In my current projects, we usually have unique values, so I haven't run into this scenario. But this is exactly the kind of challenge I'd love to research and figure out! Could I follow up with you on the solution after the interview?"
[Shows problem-solving attempt but lacks technical depth; however, maintains positive attitude and learning mindset]
Mark: "Let's talk about your experience with APIs. How do you handle error responses and retries?"
Sarah: "Great question! APIs are so important for modern applications. In my experience, when we call APIs, sometimes they don't work – like when the server is down or there's a network issue. So we need to handle those errors gracefully.
I usually wrap API calls in try-catch blocks to catch any errors. For retries, I... well, I know it's important to retry failed requests, but I haven't implemented a sophisticated retry mechanism myself. I think there are libraries that can help with that? In my current role, our senior architect set up most of the API infrastructure, so I've been working more on the frontend integration side.
But I'm really interested in learning more about backend architecture! I know concepts like exponential backoff are important for retries, though I'd need to research the implementation details."
    """
    
    try:
        print("Starting interview analysis...")
        print("="*50)
        
        # Try the advanced analysis first
        result = analyze_interview_advanced(sample_interview)
        
        print("\nAnalysis completed successfully!")
        print("="*50)
        
        # Print formatted report
        report = format_analysis_report(result)
        print(report)
        
    except Exception as e:
        print(f"Advanced analysis failed: {str(e)}")
        print("Trying simple analysis...")
        
        # Fallback to simple analysis
        simple_result = analyze_interview_simple(sample_interview)
        print("\nSimple Analysis Result:")
        print("="*30)
        print(simple_result["analysis"])