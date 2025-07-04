import os
from pinecone import Pinecone

# Initialize Pinecone
pc = Pinecone(api_key="***REMOVED***")

# Connect to your integrated index
index = pc.Index(host="https://q-and-a-ca6oioo.svc.aped-4627-b74a.pinecone.io")

# Delete all vectors where metadata.type == "mcq"
index.delete(filter={"type": {"$eq": "mcq"}},namespace="questions")