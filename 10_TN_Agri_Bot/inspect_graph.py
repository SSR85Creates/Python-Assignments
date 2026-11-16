
import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

load_dotenv()

graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    database="06388906"
)

print("\n--- SAMPLE DOCUMENT CONTENT ---")

documents = graph.query("""
MATCH (d:Document)
WHERE d.text IS NOT NULL
RETURN d.text AS content
LIMIT 5
""")

for i, doc in enumerate(documents, start=1):
    print(f"\nDOCUMENT {i}:")
    print(doc["content"][:1000])

print("\n--- GRAPH RELATIONSHIPS ---")

relationships = graph.query("""
MATCH (a)-[r]->(b)
RETURN labels(a) AS source,
       type(r) AS relationship,
       labels(b) AS target
LIMIT 20
""")

for item in relationships:
    print(item)

print("\n--- DOCUMENT COUNT ---")

print(graph.query("""
MATCH (d:Document)
RETURN count(d) AS total_documents
"""))
