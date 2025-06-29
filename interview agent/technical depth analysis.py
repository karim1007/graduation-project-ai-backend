import json
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import Runnable

# === 🔐 Initialize LLM ===
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.4, api_key="***REMOVED***")
evaluate_prompt = ChatPromptTemplate.from_template("""
You are a technical evaluator comparing a candidate's answer to a golden answer.

Evaluate the following:
- Question: {question}
- Golden Answer: {golden_answer}
- Candidate Answer: {candidate_answer}

Return a JSON object:
{{
  "verdict": "Correct / Incorrect / Partially Correct",
  "reasoning": "...",
  "thought_process_considered": "Yes/No with justification"
}}
""")
evaluate_chain: Runnable = evaluate_prompt | llm | JsonOutputParser()

def evaluate_answer_batch(
    questions: List[str],
    golden_answers: List[str],
    candidate_answers: List[str]
) -> List[Dict]:
    evaluations = []
    for q, gold, cand in zip(questions, golden_answers, candidate_answers):
        result = evaluate_chain.invoke({
            "question": q,
            "golden_answer": gold,
            "candidate_answer": cand
        })
        evaluations.append(result)
    return evaluations

# === 🧠 Function 2: Exam-Level Technical Summary ===
exam_summary_prompt = ChatPromptTemplate.from_template("""
You are a senior technical reviewer evaluating a candidate's performance on a technical assessment.

Use the following data:
- Questions and answers attempted by the candidate
- Evaluations of each answer

Your task:
1. Identify trends in performance (e.g., strong/weak domains, question types, difficulty)
2. Summarize strengths and weaknesses
3. Suggest technical areas for improvement

Data:
{exam_data}

Provide a detailed yet clear technical evaluation of the overall exam.
""")
exam_summary_chain: Runnable = exam_summary_prompt | llm

def generate_exam_summary(qa_and_eval: List[Dict]) -> str:
    return exam_summary_chain.invoke({
        "exam_data": json.dumps(qa_and_eval, indent=2)
    }).content

# === ✅ Main Function ===
def run_exam_pipeline(input_json_path: str, output_json_path: str, candidate_answers: List[str]):
    with open(input_json_path, "r") as f:
        data = json.load(f)

    questions = data["questions"]
    golden_answers = data["answers"]
    #assuming we will get the questions and answers from the input JSON
    #questions = quesiton_list
    #golden_answers = golden_answer_list
    assert len(candidate_answers) == len(questions)

    print("🔍 Evaluating each answer...")
    evaluations = evaluate_answer_batch(questions, golden_answers, candidate_answers)

    combined = []
    for i in range(len(questions)):
        combined.append({
            "question": questions[i],
            "golden_answer": golden_answers[i],
            "candidate_answer": candidate_answers[i],
            "evaluation": evaluations[i]
        })

    print("🧠 Generating exam-level technical feedback...")
    exam_summary = generate_exam_summary(combined)
    final_grade = calculate_grade(combined)

    result = {
        "questions_evaluated": combined,
        "exam_summary": exam_summary,
        "final_grade": final_grade
    }

    with open(output_json_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"✅ Evaluation saved to {output_json_path}")
    print("\n📋 Exam Summary:\n")
    print(exam_summary)
def calculate_grade(evaluations: List[Dict]) -> float:
    score = 0.0
    for ev in evaluations:
        verdict = ev["evaluation"]["verdict"].strip().lower()
        if verdict == "correct":
            score += 1.0
        elif verdict == "partially correct":
            score += 0.5
        # incorrect = 0, so no need to add
    grade_percent = (score / len(evaluations)) * 100
    return round(grade_percent, 2)
if __name__ == "__main__":
    candidate_answers = [
        "CIELAB is perceptually uniform, which helps clustering be more accurate. K-means makes better groups in this space.",
        "asyncio lets you write concurrent code with coroutines and the event loop. aiohttp helps with async http requests.",
        "True",
        "Indexes speed up queries. B-tree is balanced, bitmap is good for low-cardinality fields.",
        "Normalization removes duplication. 1NF makes atomic, 2NF full dependency, 3NF removes indirect.",
        "CNNs are better for images because they use filters and pooling.",
        "True",
        "To prevent overfitting by randomly disabling neurons.",
        "Not sure how to implement this",
    ]

    run_exam_pipeline(
        input_json_path="qa_pairs.json",
        output_json_path="exam_results.json",
        candidate_answers=candidate_answers
    )