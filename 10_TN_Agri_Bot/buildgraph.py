
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    database="06388906"
)

print("Connected to Neo4j!")

# Remove old graph data
graph.query("MATCH (n) DETACH DELETE n")
print("Old graph cleared.")

# Read detailed scheme data
with open("data/schemes.txt", "r", encoding="utf-8") as file:
    content = file.read()

# Split content into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)

chunks = splitter.split_text(content)

documents = [
    Document(
        page_content=chunk,
        metadata={"source": "Tamil Nadu Government Scheme Website"}
    )
    for chunk in chunks
]

print("Total document chunks:", len(documents))

# Initialize LLM and graph transformer
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

transformer = LLMGraphTransformer(llm=llm)

# Process and store in batches
batch_size = 5

for i in range(0, len(documents), batch_size):
    batch = documents[i:i + batch_size]

    print(f"\nProcessing batch {i // batch_size + 1}...")

    graph_documents = transformer.convert_to_graph_documents(batch)

    graph.add_graph_documents(
        graph_documents,
        baseEntityLabel=True,
        include_source=True
    )

    print(f"Batch {i // batch_size + 1} stored!")

print("\nKnowledge Graph rebuilding completed!")

result = graph.query("MATCH (n) RETURN count(n) AS total_nodes")
print("Total graph nodes:", result)

print("Step 7 completed!")
