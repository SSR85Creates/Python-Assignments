
import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS


# =====================================================
# PROJECT CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DOCUMENTS_DIR = BASE_DIR / "documents"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Check your .env file.")


# =====================================================
# 1. BUILD VECTOR STORE
# =====================================================

def build_vectorstore():

    documents = []

    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            "No PDF files found in documents folder."
        )

    # Load PDF documents
    for pdf_file in pdf_files:

        loader = PyPDFLoader(str(pdf_file))
        pages = loader.load()

        for page in pages:
            page.metadata["source"] = pdf_file.name

        documents.extend(pages)

    print(f"Loaded {len(documents)} PDF pages.")

    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)

    print(f"Created {len(chunks)} text chunks.")

    # Generate OpenAI embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=OPENAI_API_KEY
    )

    # Create FAISS vector store
    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    # Save vector store locally
    VECTORSTORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    vectorstore.save_local(str(VECTORSTORE_DIR))

    print("FAISS vector store created successfully.")

    return vectorstore


# =====================================================
# 2. LOAD EXISTING VECTOR STORE
# =====================================================

def load_vectorstore():

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=OPENAI_API_KEY
    )

    if not VECTORSTORE_DIR.exists():
        raise FileNotFoundError(
            "Vector store not found. Index documents first."
        )

    return FAISS.load_local(
        str(VECTORSTORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True
    )


# =====================================================
# 3. ASK QUESTIONS USING RAG
# =====================================================

def ask_question(question, vectorstore):

    # Retrieve relevant document chunks
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 4}
    )

    relevant_docs = retriever.invoke(question)

    if not relevant_docs:
        return (
            "No relevant information found in the documents.",
            []
        )

    # Prepare context from retrieved documents
    context = "\n\n".join(
        [
            f"Source: {doc.metadata.get('source', 'Unknown')}, "
            f"Page: {doc.metadata.get('page', 0) + 1}\n"
            f"{doc.page_content}"
            for doc in relevant_docs
        ]
    )

    # Connect to OpenAI GPT-4o-mini
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=OPENAI_API_KEY
    )

    # Prepare the RAG prompt
    prompt = f"""
You are an assistant that answers questions about
Tamil Nadu agricultural government schemes.

Answer using ONLY the information in the supplied context.

If the answer is not available in the context, clearly say:
"The provided documents do not contain this information."

Do not invent scheme names, benefits, eligibility criteria,
amounts or application procedures.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

    # Generate answer
    response = llm.invoke(prompt)

    # Extract source references
    sources = []

    for doc in relevant_docs:

        source = {
            "filename": doc.metadata.get("source", "Unknown"),
            "page": doc.metadata.get("page", 0) + 1
        }

        if source not in sources:
            sources.append(source)

    return response.content, sources
