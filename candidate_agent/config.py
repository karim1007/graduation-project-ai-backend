import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the API key from the environment
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# Optionally, handle missing environment variables
if TOGETHER_API_KEY is None:
    raise ValueError("TOGETHER_API_KEY is not set in the environment variables!")
