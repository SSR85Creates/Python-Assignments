
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph

load_dotenv()

# Connect to Neo4j
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    database="06388906"
)

print("Connected to Neo4j successfully!")

# Initialize OpenAI
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

print("\nTamil Nadu Government Schemes - Graph RAG Chatbot")
print("Ask questions about schemes, benefits and eligibility.")
print("Type 'exit' to stop.")

while True:

    question = input("\nAsk your question: ")

    if question.lower().strip() in ["exit", "quit"]:
        print("Chatbot stopped.")
        break

    try:
        # Retrieve relevant document content from Neo4j
        search_prompt = f"""
        Extract 3 to 6 important search keywords or short phrases
        from this question about Tamil Nadu government schemes.

        Return only comma-separated keywords.

        Question: {question}
        """

        keyword_response = llm.invoke(search_prompt)
        keywords = [
            word.strip().lower()
            for word in keyword_response.content.split(",")
            if word.strip()
        ]

        # Search stored documents
        query = """
        MATCH (d:Document)
        WHERE d.text IS NOT NULL
        AND any(term IN $terms
            WHERE toLower(d.text) CONTAINS term)
        RETURN d.text AS content
        LIMIT 8
        """

        results = graph.query(query, {"terms": keywords})

        if not results:
            print("\nNo matching information found in the government website data.")
            continue

        context = "\n\n".join(
            item["content"] for item in results
        )

        # Generate answer using retrieved source content
        answer_prompt = f"""
        You are a Tamil Nadu Government Schemes assistant.

        Answer the user's question using ONLY the supplied website content.

        Do not invent benefits, eligibility criteria, amounts or procedures.

        If the information is unavailable, clearly say:
        "The available website information does not specify this."

        WEBSITE CONTENT:
        {context}

        USER QUESTION:
        {question}

        Provide a clear and concise answer.
        """

        response = llm.invoke(answer_prompt)

        print("\nAnswer:")
        print(response.content)

        print("\nSource: Tamil Nadu Government Scheme Website")
        print("Retrieved document chunks:", len(results))

    except Exception as e:
        print("\nError:", str(e))
