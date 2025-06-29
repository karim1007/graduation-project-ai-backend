
import json
import uuid
from pinecone import Pinecone

# Init Pinecone client
pc = Pinecone(api_key="***REMOVED***")

# Connect to your integrated index
index = pc.Index(host="https://q-and-a-ca6oioo.svc.aped-4627-b74a.pinecone.io")

# Namespace to use (optional but recommended)
namespace = "questions"

# Load questions from JSON
with open("questions.json", "r") as f:
    qa_list = json.load(f)

# Upsert each question one by one
for qa in qa_list:
    record = {
        "_id": str(uuid.uuid4()),
        "text": qa["question"],  # This will be embedded by Pinecone
        "answer": qa["answer"],
        "type": qa["type"],
        "difficulty": qa["difficulty"],
        "domain": qa["domain"]
    }

    # Upsert the record
    index.upsert_records(
        namespace=namespace,
        records=[record]
    )

    print(f"✅ Uploaded: {record['text']}")
