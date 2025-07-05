import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from pinecone import Pinecone
from typing import Optional, List
import json
import openai
# === Setup ===
openai.api_key = "***REMOVED***"  # Preferably use os.getenv()

openai_api_key = "***REMOVED***"
pinecone_api_key = "***REMOVED***"

# Initialize Pinecone client and index
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index(host="https://q-and-a-ca6oioo.svc.aped-4627-b74a.pinecone.io")
namespace = "resumes"

# Initialize OpenAI model via LangChain
llm = ChatOpenAI(model_name="gpt-4.1-mini", temperature=0.2, api_key=openai_api_key)

# === Step 1: Retrieve top-K resumes ===
def search_resumes(job_description: str, top_k: int = 3, filters: Optional[dict] = None) -> List[dict]:
    """Search resumes in Pinecone using a job description as the query."""
    results = index.search(
        namespace=namespace,
        query={
            "inputs": {"text": job_description},
            "top_k": top_k,
            "filter": filters or {}
        },
        fields=["filename", "file_content", "ID"]
    )

    resumes = []
    seen = set()
    for hit in results["result"]["hits"]:
        print(hit)
        score = hit["_score"]
        row = hit["fields"]
        id= hit["_id"]
        if row["file_content"] not in seen:
            seen.add(row["file_content"])
            resumes.append({
                "ID": id,
                "filename": row.get("filename", "Unnamed"),
                "content": row.get("file_content", ""),
                "score": score
            })

    return resumes

# === Step 2: Compare and Summarize ===
def generate_summary(job_description: str, resumes: list):
    resume_texts = "\n\n".join([
        f"Candidate ID: {res['ID']}\n\nResume Content:\n{res['content']}"
        for res in resumes
    ])

    prompt = f"""
You are a smart hiring assistant AI designed to evaluate candidates based on job fit.

INSTRUCTIONS:
- Carefully read the provided job description.
- Review the resumes of each candidate.
- Determine the candidate who is the best overall match.
- Justify your choice clearly based on alignment with required skills, relevant experience, and educational background.

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUMES:
{resume_texts}

OUTPUT FORMAT (JSON):
{{
  "best_candidate_id": "(insert ID of candidate)",
  "best_candidate_name": "(insert name of candidate)" infer it from the resume,
  "reason": "Brief but clear explanation why this candidate is the best match for the job, including specific skills, experience, or education that align with the job description.",
  "email": "(insert email of candidate if available)"
}}
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


def choose_best_candiate(job_description: str, top_k: int = 3) -> dict:
    """Main function to search resumes and generate a summary."""
    top_resumes = search_resumes(job_description, top_k=top_k)
    if not top_resumes:
        return {"error": "No resumes found matching the job description."}

    summary = generate_summary(job_description, top_resumes)
    parsed_output = json.loads(summary)
    target_id = parsed_output.get("best_candidate_id")
    result = next((item for item in top_resumes if item["ID"] == target_id), None)
    confidence_score = result["score"] if result else 0.0
    return {
        "best_candidate_id": target_id,
        "best_candidate_name": parsed_output.get("best_candidate_name", result["filename"]),
        "reason": parsed_output.get("reason", ""),
        "confidence_score": confidence_score,
        "email": parsed_output.get("email", "Unknown")
    }


def generate_job_detailss(job_title: str, department: str, employment_type: str, experience_level: str) -> dict:
    prompt = (
        f"Create a job description and list of responsibilities and requirements for the following role:\n\n"
        f"Job Title: {job_title}\n"
        f"Department: {department}\n"
        f"Employment Type: {employment_type}\n"
        f"Experience Level: {experience_level}\n\n"
        f"Return the result strictly in the following JSON format:\n\n"
        f"""{{
  "job_description": "...",
  "responsibilities": ["...", "...", "..."],
  "requirements": "..."
}}"""
f"Be as detailed as possible, including specific skills, qualifications, and any other relevant information."
    )

    response = openai.chat.completions.create(
        model="gpt-4.1-mini",  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        
    )

    # Parse and return the JSON from the response
    import json
    content = response.choices[0].message.content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("LLM did not return valid JSON. Raw output:\n" + content)
    
