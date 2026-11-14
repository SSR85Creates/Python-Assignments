from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load API key from .env
load_dotenv()

# Initialize the language model
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)

# Define the prompt
prompt = """
Suggest exactly 5 healthy breakfast ideas.
Format:
- Numbered list
- One line per idea
- No introduction or preamble
"""

# Get response from the model
reply = llm.invoke(prompt)

# Print the complete response object (for learning)
print(reply.content)