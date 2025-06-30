TOGETHER_API_KEY="***REMOVED***"

import os
from typing import List, Dict, Any, Annotated, Tuple
from langchain_together import ChatTogether
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool, BaseTool
from pydantic import BaseModel, Field
from tenacity import retry
from detection import process_candidate_exam

# Set up API key for Together AI
os.environ["TOGETHER_API_KEY"] = TOGETHER_API_KEY

# Define some example tools for the agent
@tool
def analyze_candidate(candidate_name: str) -> str:
    """
    Analyzes the exam footage of a candidate to detect any suspicious activity or cheating."""
    result= process_candidate_exam(candidate_name)
    return result

# Define a custom tool with pydantic model for input validation




# Create a list of tools
tools = [analyze_candidate]
# Initialize the language model
model = ChatTogether(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    temperature=0.4,
    max_tokens=1000
)

# Create the React agent
agent = create_react_agent(model, tools)

# Define a function to run the agent
messages = [
    (
        "system",
        "You are a strict and observant proctoring agent analyzing live or recorded exam footage. Your task is to review the candidate's behavior and identify any signs of cheating or suspicious activity.",
    ),
    ("human", "analyze karim's exam footage"),
]

# Example usage
agent_response = agent.invoke({"messages": messages})
print(agent_response["messages"][-1].content)

