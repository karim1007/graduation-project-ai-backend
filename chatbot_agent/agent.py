import os
import random
from typing import List
from prompts import prompt
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from apis import build_questions_payload, generate_questions, get_job_supabase, create_job_supabase, create_assessment_supabase , choose_best_resume, get_supabase_assessment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# --- 1. Define Your Tools ---
# A tool is a function that the agent can decide to call.
# The @tool decorator is a simple way to create one.
# The function's docstring is VERY important. The agent uses it to decide
# when and how to use the tool.
from typing import Optional, Dict, Any
@tool
def create_job(
    job_name: str,
    location: str,
    job_type: str,
    responsibility: Optional[str],
    salary: int,
    job_description: Optional[str] = None,
    currency: Optional[str] = "USD",
    department: Optional[str] = "Engineering and Computer Science",
    skills: Optional[List[str]] = None,
    requirements: Optional[List[str]] = None,
) -> str:
    """
    Creates a new job listing in the database.

    Required parameters:
    - job_name: Name of the job
    - location: Job location
    - job_type: "full-time" or "part-time"
    - responsibility: Core responsibilities of the role
    - salary: Salary or salary range
    - currency: Currency of the salary (default is "USD")
    Optional:
    - job_description: A detailed description (if not provided, the agent MUST generate one)
    - Department: Department for the job (default is "Engineering and Computer Science") you can infer it
    - skills: List of required skills (optional) you can infer it
    - requirements: List of job requirements (optional) you can infer it
    """
    experience_level = random.choice(["entry-level", "mid-level", "senior-level"])

    dictionary= {
        "title": job_name,
        "location": location,
        "type": job_type,
        "responsibilities": responsibility,
        "salary_min": salary,
        "salary_max": salary + 1000,  # Assuming a range of 1000 for simplicity
        "salary_currency": currency,
        "description": job_description if job_description else "Generated description based on provided details.",
        "status": "draft",
        "department": department,
        "created_by": None,
        "skills": skills if skills else [],
        "requirements": requirements if requirements else [],
        "benefits": "401k",  # Optional, can be added later
        "experience_level": experience_level,
    }
    result = create_job_supabase(dictionary)
    if result["status_code"] == 201:
        # Assuming the API returns a job ID or similar identifier
        job_id = get_job_supabase(job_name)["response"][0]["id"]
        link = f"http://localhost:3000/recruiter/jobs/{job_id}"
        return f"Job '{job_name}' created successfully with id '{job_id}'. You can view it at {link}"
    else:
        return f"Failed to create job '{job_name}'. Status code: {result['status_code']}"

    #raise NotImplementedError("Implement job creation logic here")


@tool
def create_exam(
    job_name: str = None,
    num_questions: int = 5,
    
) -> str:
    """
    Creates an exam with questions based on a job.

    Parameters:
    - job_name: If provided, uses an existing job
    - num_questions: Number of questions to generate for the exam (default is 5)
    Returns:
    - exam_id and a list of generated questions
    """
    job_details= get_job_supabase(job_name)["response"][0]
    title = f"{job_name} Exam (AI generateds)"
    description = job_details["description"] if job_details else "Generated exam based on job details."
    duration= 60  # Duration in minutes
    passing_score = 70
    types = "technical"
    status = "scheduled"
    questionss= generate_questions(job_details["description"], num_questions)
    questions = build_questions_payload(questionss)
    uuids = "353764fa-5193-42fb-b8f0-1bf31013bdf9"
   
    
    candidate_id =  uuids
    print(candidate_id)
    payload={
        "title": title,
        "description": description,
        "duration": duration,
        "passing_score": passing_score,
        "instructions": "Answer all questions to the best of your ability.",
        "questions": questions,
        "type": types,
        "status": status,
        "candidate_id": candidate_id
    }
    result = create_assessment_supabase(payload)
    assessment = get_supabase_assessment()

    link = f"http://localhost:3000/recruiter/assessments/{assessment[0]['id']}"
    if result["status_code"] == 201:
        # Assuming the API returns an exam ID or similar identifier
        return f"Exam '{title}' created successfully with {num_questions} questions. You can view it at {link}"
    else:
        return f"Failed to create exam for job '{job_name}'"

    return f"exam created for job '{job_name}' with {num_questions} questions."
    raise NotImplementedError("Implement exam creation logic here")



@tool
def select_best_candidate(job_name: str) -> str:
    """
    Selects the best candidate for the given job.

    Parameters:
    - job_name: Name of the job to evaluate
    Returns:
    - A dict with 'candidate_id' or 'candidate_name' and 'reason' for selection and also email
    """
    result = get_job_supabase(job_name)
    if result["status_code"] != 200 or not result["response"]:
        return f"No job found with name '{job_name}'. Please check the job name and try again."
    job_description = result["response"][0]["description"]
    best_candidate = choose_best_resume(job_description)
    return f"The best candidate for the job '{job_name}' is {best_candidate['best_candidate_name']} with ID {best_candidate['best_candidate_id']} and email {best_candidate['email']}. Reason: {best_candidate['reason']}."
    raise NotImplementedError("Implement candidate selection logic here")


# Create a list of the tools the agent can use.
tools = [select_best_candidate, create_job, create_exam]


# --- 2. Set up the LLM and Agent ---
# We'll use OpenAI's gpt-4o model for this example.
# Make sure you have your OPENAI_API_KEY set in your environment variables.
# os.environ["OPENAI_API_KEY"] = "sk-..." # uncomment and set your key if not in env

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.4, api_key=os.getenv("OPENAI_API_KEY"))

# The `create_react_agent` function is a prebuilt graph that chains together
# an LLM call (to decide the next action) and a tool executor.
agent_executor = create_react_agent(llm, tools,prompt=prompt)

print("✅ Agent created successfully!")

# --- 3. (Optional) Run the Agent Directly ---W
# This part is for testing the agent directly from the script.
if __name__ == "__main__":
    print("\n--- Running Agent Example ---")

    # The input to the agent is a dictionary with a "messages" key.
    # The value is a list of messages. The last message is the user's request.
    inputs = {"messages": [HumanMessage(content="What is the weather in San Francisco?")]}

    # The `stream` method lets us see the agent's thought process step-by-step.
    # Each item in the stream is a "chunk" of the graph's state.
    print(f"\n> User Question: {inputs['messages'][-1].content}\n")
    print("Agent's thought process:")
    for chunk in agent_executor.stream(inputs, stream_mode="values"):
        # The 'messages' key contains the list of messages in the state
        last_message = chunk["messages"][-1]
        
        # If the last message is an AIMessage, it's a thought or the final answer
        if last_message.tool_calls:
            # This is the "Action" step
            print(f"\n---\n🤔 Thought: The user is asking for the weather. I should use my `search_weather` tool.\nTool Call: {last_message.tool_calls[0]['name']}({last_message.tool_calls[0]['args']})")
        elif last_message.type == "tool":
            # This is the "Observation" step
            print(f"---\n🛠️ Observation: The tool returned the following result:\n`{last_message.content}`")
        else:
             # This is the final answer
             print("---\n✅ Final Answer:")
             print(last_message.content)