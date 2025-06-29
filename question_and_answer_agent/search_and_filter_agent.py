import json
from typing import List, Literal, Optional, Dict, Any
from pinecone import Pinecone
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.messages import HumanMessage

# === 🔐 API Keys ===
OPENAI_API_KEY = "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"
PINECONE_API_KEY = "pcsk_2nExZA_FGuSQwgZEAmSiW9pHnpn4CzofTTLgoyt4VJqy2cBdvTPegKDKF1LaTL1Cv4EGx7"
PINECONE_HOST = "https://q-and-a-ca6oioo.svc.aped-4627-b74a.pinecone.io"

# === 🌐 Pinecone Setup ===
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(host=PINECONE_HOST)
namespace = "questions"

# === 🔧 Pinecone Search Tool ===
@tool
def search_questions(query_text: str, top_k: int = 3, filters: Optional[dict] = None) -> List[dict]:
    """Search interview questions given a query and optional metadata filters."""
    results = index.search(
        namespace=namespace,
        query={
            "inputs": {"text": query_text},
            "top_k": top_k,
            "filter": filters or {}
        },
        fields=["text", "answer", "type", "difficulty", "domain"]
    )

    qas = []
    seen = set()
    for hit in results["result"]["hits"]:
        row = hit["fields"]
        if row["text"] not in seen:
            seen.add(row["text"])
            qas.append(row)
    return qas


# === 🧠 Prompt for Extracting Metadata + Queries ===
prompt = ChatPromptTemplate.from_template("""
You're an expert educational AI tasked with analyzing a job description and preparing interview question queries.

You must:
1. Infer relevant `question_types`, `difficulty` levels, and `domains` for filtering (use only allowed values).
2. Generate {num_queries} short and focused search queries that will help retrieve questions from a technical interview database.

Allowed Values:
- question_types: ["essay", "mcq", "coding", "true_false"]
- difficulties: ["easy", "medium", "hard"]
- domains: ["machine learning", "data structures", "algorithms", "python", "databases", "Computer vision", "software engineering", "Deep Learning", "AI Ethics", "Cloud Computing"]

Return output as JSON:
{{
  "question_types": [...],
  "difficulties": [...],
  "domains": [...],
  "queries": ["...", "...", "..."]
}}

Job Description:
\"\"\"
{job_description}
\"\"\"
""")

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.6, api_key=OPENAI_API_KEY)
parser = JsonOutputParser()
chain: Runnable = prompt | llm | parser


# === 🤖 Agent Function ===
def agent_generate_questions(job_description: str, total_questions: int = 10) -> List[Dict[str, Any]]:
    # Step 1: Let the agent decide filters + queries
    metadata_and_queries = chain.invoke({
        "job_description": job_description,
        "num_queries": 6
    })

    question_types = metadata_and_queries.get("question_types", [])
    difficulties = metadata_and_queries.get("difficulties", [])
    domains = metadata_and_queries.get("domains", [])
    queries = metadata_and_queries.get("queries", [])

    print("\n🧠 Inferred Filters:")
    print("Types:", question_types)
    print("Difficulties:", difficulties)
    print("Domains:", domains)
    print("Queries:", queries)

    filters = {}
    if question_types: filters["type"] = {"$in": question_types}
    if difficulties: filters["difficulty"] = {"$in": difficulties}
    if domains: filters["domain"] = {"$in": domains}

    # Step 2: Call search_questions tool using varied prompts
    results = []
    seen = set()
    for query in queries:
        qas = search_questions.invoke({
            "query_text": query,
            "top_k": 3,
            "filters": filters
        })
        for qa in qas:
            if qa["text"] not in seen:
                seen.add(qa["text"])
                results.append(qa)
            if len(results) >= total_questions:
                break
        if len(results) >= total_questions:
            break

    return results


def generate_questions(Job_Description: str, total_questions: int):
    jd = """
    Job Summary:

The Data Scientist within the Data, Analytics & AI Center of Excellence (CoE) is responsible for leveraging advanced analytical techniques, machine learning models, and statistical tools to derive actionable insights from complex datasets. This role supports the company's strategic objectives by driving data-driven decision-making and enabling predictive capabilities across various business functions including Manufacturing.
 Responsibilities:

Develop and implement machine learning models to address specific business challenges.
Collaborate with cross-functional teams to identify opportunities for data-driven solutions.
Analyze large and complex datasets to uncover trends, patterns, and actionable insights.
Design and execute experiments to validate hypotheses and optimize processes.
Build predictive and prescriptive models to forecast outcomes and recommend actions.
Create and maintain data pipelines for extracting, transforming, and loading data efficiently.
Automate repetitive tasks and processes using AI and machine learning.
Prepare visualizations and dashboards to effectively communicate analytical results.
Ensure all models and analyses comply with organizational data governance standards.
Contribute to the continuous improvement of analytics frameworks and methodologies.
Stay updated with the latest trends and tools in data science and machine learning.
Mentor junior team members and provide technical guidance when needed.
Collaborate with data engineers to ensure the integrity and quality of data pipelines.
Develop documentation for models, processes, and methodologies to support knowledge sharing.
Support stakeholders in understanding and applying analytical insights to their operations.


Requirements:
Bachelor's or Master's degree in Data Science, Computer Science, Statistics, Mathematics, or a related field.
5-7 years of experience in data science, analytics, or machine learning roles.
Proven experience in building, validating, and deploying machine learning models.
Experience working in a cross-functional team environment.
Excellent written and verbal English language proficiency.


Skills:

Proficiency in programming languages such as Python, R, or Scala.
Expertise in machine learning frameworks like TensorFlow, PyTorch, or scikit-learn.
Advanced skills in data manipulation using SQL and big data technologies.
Strong knowledge of data visualization tools (e.g., Tableau, Power BI, or Matplotlib).
Experience with cloud platforms: Azure for data science is a plus.
Solid understanding of statistics, probability, and experimental design.
Familiarity with natural language processing (NLP) and computer vision techniques.
Strong problem-solving and critical-thinking skills.
    """

    questions = agent_generate_questions(Job_Description, total_questions)

    for i, q in enumerate(questions, 1):
        print(f"\nQ{i}: {q['text']}")
        print(f"A: {q['answer']}")
        print(f"Type: {q['type']} | Difficulty: {q['difficulty']} | Domain: {q['domain']}")
        print("-" * 50)

    # Extract questions and answers into JSON format
    # Extract questions and answers into JSON format
    qa_json = {
        "questions": [q['text'] for q in questions],
        "answers": [q['answer'] for q in questions],
        "types": [q['type'] for q in questions],
        "difficulties": [q['difficulty'] for q in questions],
        "domains": [q['domain'] for q in questions]
    }
    
    # Save to file
    return qa_json

