import os
from dotenv import load_dotenv
from baml_client.sync_client import b
from baml_client.types import *

# Load environment variables from .env file
load_dotenv()

# Verify API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Test a simple BAML function
def main():
    # This function name should match one defined in your baml_src files
    # Using the ExtractResume function defined in resume.baml
    sample_resume = """
    John Doe
    john.doe@example.com
    
    Experience:
    - Software Engineer at Tech Company
    - Intern at Startup
    
    Skills:
    - Python
    - JavaScript
    """
    result = b.ExtractResume(sample_resume)
    print(result)

if __name__ == "__main__":
    main()