
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

prompts = [
    "What is Artificial Intelligence? Explain with a simple example.",
    "What is Manufacturing Quality 4.0? Explain its importance in the automotive industry.",
    "You are a manufacturing technology consultant. Explain how Artificial Intelligence, predictive analytics, and automated quality inspection can improve manufacturing operations. Discuss practical applications, business benefits, implementation challenges, and an example from the automotive industry."
]

for p in prompts:
    print(llm.invoke(p).content)
