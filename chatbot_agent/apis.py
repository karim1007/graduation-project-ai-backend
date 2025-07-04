import requests
import urllib.parse
import re

def get_supabase_job_url(job_title: str) -> str:
    base_url = "https://zdaxvwxqyzmclscjlsoc.supabase.co/rest/v1/jobs"
    encoded_title = urllib.parse.quote(job_title)
    return f"{base_url}?title=eq.{encoded_title}&select=*"
# === Supabase Configuration ===
SUPABASE_URL = "https://zdaxvwxqyzmclscjlsoc.supabase.co/rest/v1"
API_KEY = "***REMOVED***"

HEADERS = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# === Functions ===
def get_job_supabase(job_title: str) -> dict:
    """
    Retrieve a job posting from Supabase by title.
    :param job_title: Title of the job to search for
    :return: dict with 'status_code' and 'response' (parsed JSON)
    """
    url = get_supabase_job_url(job_title)
    resp = requests.get(url, headers=HEADERS)
    return {
        "status_code": resp.status_code,
        "response": resp.json()
    }
def create_job_supabase(job_data: dict) -> dict:
    """
    Create a new job posting in Supabase.
    :param job_data: dict matching the jobs table schema
    :return: dict with 'status_code' and 'response' (parsed JSON)
    """
    url = f"{SUPABASE_URL}/jobs"
    print(f"Creating job with data: {job_data}")
    resp = requests.post(url, headers=HEADERS, json=job_data)
    return {
        "status_code": resp.status_code,
    }


def create_assessment_supabase(assessment_data: dict) -> dict:
    """
    Create a new assessment in Supabase.
    :param assessment_data: dict matching the assessments table schema
    :return: dict with 'status_code' and 'response' (parsed JSON)
    """
    url = f"{SUPABASE_URL}/assessments"
    resp = requests.post(url, headers=HEADERS, json=assessment_data)
    return {
        "status_code": resp.status_code,
        "response": resp.json()
    }

DEFAULT_PT = {
    "multiple_choice": (10, 5),
    "true_false":      (5,  2),
    "coding":          (15, 10),
    "essay":           (20, 10),
}

# map your API’s “types” -> Supabase question type
TYPE_MAP = {
    "mcq":        "multiple_choice",
    # leave others unchanged
    "true_false": "true_false",
    "coding":     "coding",
    "essay":      "essay",
}

LOCAL_AGENT_URL = "http://localhost:8000/exam-generation-agent/generate-questions"

def generate_questions(job_description: str, num_questions: int) -> dict:
    """Hit your local agent and return the raw JSON."""
    resp = requests.post(
        LOCAL_AGENT_URL,
        json={"job_description": job_description, "num_questions": num_questions},
        headers={"Content-Type": "application/json"},
        timeout=(3, 30)
    )
    resp.raise_for_status()
    return resp.json()


def build_questions_payload(gen: dict) -> list:
    """
    Takes the raw {'questions', 'answers', 'types', 'difficulties', 'domains'}
    and returns a list of fully-formed question objects ready for Supabase.
    """
    out = []
    for i, (q_text, ans, t, diff, dom) in enumerate(zip(
        gen["questions"],
        gen["answers"],
        gen["types"],
        gen["difficulties"],
        gen["domains"]
    )):
        qtype = TYPE_MAP.get(t, t)
        qobj = {
            "id":        f"q{i+1}",
            "type":      qtype,
            "content":   q_text,
            "difficulty": diff,
            "domain":    dom,
            # store the full answer text too
            "answer":    ans,
        }

        # MCQ: parse options & correctAnswer
        if t == "mcq":
            lines = q_text.split("\n")
            qobj["content"] = lines[0]
            # lines like 'A) foo'
            opts = [ln.split(") ",1)[1] for ln in lines[1:] if re.match(r"^[A-Z]\)", ln)]
            qobj["options"] = opts
            # ans like 'B) ...'
            letter = re.match(r"^([A-Z])\)", ans).group(1)
            qobj["correctAnswer"] = ord(letter) - ord("A")

        # True/False and others have no extra parsing
        elif t == "true_false":
            # optional: explicitly set options
            qobj["options"] = ["True", "False"]
            val = ans.strip().split(".")[0].lower()
            qobj["correctAnswer"] = 0 if val == "true" else 1

        # assign default points & timeLimit
        pts, tl = DEFAULT_PT.get(qtype, (10, 5))
        qobj["points"] = pts
        qobj["timeLimit"] = tl

        out.append(qobj)
    return out

def choose_best_resume(job_description: str) -> dict:
    url = "http://localhost:8000/cv-agent/choose_best_resume/"
    headers = {"Content-Type": "application/json"}
    payload = {"job_description": job_description}

    response = requests.post(url, headers=headers, json=payload)

    if response.ok:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}

# === Example Usage ===
if __name__ == "__main__":
    # 1) Create a Jobs
    # doct={'title': 'AI Engineer', 'location': 'Egypt', 'type': 'full-time', 'responsibilities': 'Develop and deploy AI models and algorithms, collaborate with cross-functional teams to integrate AI solutions, and continuously improve system performance through research and experimentation.', 'salary_min': 20000, 'salary_max': 21000, 'salary_currency': 'USD', 'description': 'We are seeking a skilled AI Engineer to design, develop, and implement artificial intelligence solutions that enhance our products and services. The ideal candidate will have expertise in machine learning, deep learning, and data analysis to build intelligent systems that solve complex problems.', 'status': 'draft', 'department': 'Engineering and Computer Science', 'created_by': None, 'skills': [], 'requirements': [], 'benefits': '401k', 'experience_level': 'senior-level'}
    # print(create_job_supabase(doct))

    # 2) Get a Job
    #print(get_job_supabase("AI engineer"))

    # 3) Create an Assessment
    # 1) generate from local agent
    # gen = generate_questions("Python Developer with Django experience", 3)

    # # 2) map to Supabase question objects
    # questions_payload = build_questions_payload(gen)

    # # 3) assemble the full assessment (feel free to tweak these fields)
    # assessment_payload = {
    #     "title":               "Auto-Generated Python Assessment",
    #     "description":         "Covers MCQ, true/false, and coding.",
    #     "duration":            60,
    #     "passing_score":       70,
    #     "skills":              ["Python"],
    #     "randomize_questions": True,
    #     "allow_retake":        False,
    #     "proctoring":          True,
    #     "instructions":        "Answer all questions to the best of your ability.",
    #     "questions":           questions_payload,
    #     "type":                "technical",
    #     "status":              "scheduled"
    # }

    # # 4) send it to Supabase
    # result = create_assessment_supabase(assessment_payload)
    # print("Supabase response:", result)

    
    
    
    
    
    
    # 4) Choose the best resume
    # job_desc = "We are looking for a skilled AI Engineer to develop and deploy machine learning models."
    # best_resume = choose_best_resume(job_desc)
    # print("Best Resume:", best_resume)
    print()