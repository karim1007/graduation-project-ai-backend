import openai
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import random
import json
import time
import os

# 🔐 Set your OpenAI API key
openai.api_key = "***REMOVED***"  # Replace with your OpenAI key

# Static lists
question_types = ["essay", "mcq", "coding", "true_false"]
difficulties = ["easy", "medium", "hard"]
domains = [
    "machine learning", "data structures", "algorithms", "python",  "databases", "Computer vision",
    "software engineering","Deep Learning", "AI Ethics", "Cloud Computing"
]

# JSON file to store all generated questions
questions_file = "questions.json"

# Load existing questions if file exists
if os.path.exists(questions_file):
    with open(questions_file, "r") as f:
        try:
            previous_qas = json.load(f)
        except json.JSONDecodeError:
            previous_qas = []
else:
    previous_qas = []

# LangChain Prompt Template
prompt_template = PromptTemplate(
    input_variables=["question_type", "difficulty", "domain", "previous_content", "count"],
    template="""
You are an expert educator creating unique educational questions and answers.

INSTRUCTIONS:
- Generate 1 high-quality question-answer pair
- Question type: {question_type}
- Difficulty: {difficulty}
- Domain: {domain}
- This is question #{count}

AVOID REPETITION:
You have previously generated these topics/questions:
{previous_content}

Make sure your new question is completely different from the above content.

RESPONSE FORMAT (JSON):
{{
    "question": "Your unique question here",
    "answer": "Comprehensive answer here",
    "type": "{question_type}",
    "difficulty": "{difficulty}",
    "domain": "{domain}"
}}

Generate a creative, educational question that hasn't been covered before:
"""
)

# LLM config
llm = ChatOpenAI(model_name="gpt-4.1-mini", temperature=0.7)

# Function to generate a unique QA pair
def generate_question(count):
    question_type = random.choice(question_types)
    difficulty = random.choice(difficulties)
    domain = random.choice(domains)

    previous_content_str = "\n".join(
        [f"- {qa['question']}" for qa in previous_qas[-10:]]
    )  # Show last 10 for memory context

    prompt = prompt_template.format(
        question_type=question_type,
        difficulty=difficulty,
        domain=domain,
        previous_content=previous_content_str,
        count=count
    )

    response = llm.predict(prompt)

    try:
        qa_data = json.loads(response)
        if qa_data["question"] in [qa["question"] for qa in previous_qas]:
            print("⚠️ Duplicate detected, regenerating...")
            return generate_question(count)
        return qa_data
    except json.JSONDecodeError:
        print("❌ Invalid JSON. Retrying...")
        time.sleep(1)
        return generate_question(count)

# Save the QA pair to the file
def save_question_to_file(qa_data):
    previous_qas.append(qa_data)
    with open(questions_file, "w") as f:
        json.dump(previous_qas, f, indent=2)

# Main loop
if __name__ == "__main__":
    total_to_generate = 50  # change this to however many Qs you want

    start = len(previous_qas) + 1
    end = start + total_to_generate

    for i in range(start, end):
        qa = generate_question(i)
        save_question_to_file(qa)
        print(f"✅ Saved Q{i}: {qa['question']}\n")
        time.sleep(2)  # Respect rate limits
