import fitz  # PyMuPDF
from pinecone import Pinecone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === Pinecone Setup ===
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(host="https://q-and-a-ca6oioo.svc.aped-4627-b74a.pinecone.io")
namespace = "resumes"

# === Extract text from PDF ===
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# === Upload to Pinecone ===
def index_resume_to_pinecone(doc_id: str, filename: str, text: str) -> str:
    record = {
        "_id": doc_id,
        "text": text,
        "filename": filename,
        "file_content": text
    }
    index.upsert_records(records=[record], namespace=namespace)
    return doc_id
