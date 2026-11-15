# AgriScheme Intelligence Platform

## 1. Project Overview

AgriScheme Intelligence is an AI-powered document intelligence platform that helps users retrieve information from Tamil Nadu government agricultural scheme PDFs.

Users can ask questions in natural language and receive context-based answers with PDF source references and page numbers.

## 2. Key Features

- Multiple PDF document processing
- Automatic text extraction and chunking
- OpenAI text embeddings
- FAISS vector database for similarity search
- GPT-4o-mini-powered question answering
- Source references with document names and page numbers
- FastAPI backend
- Streamlit user interface

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| AI Model | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| LLM Framework | LangChain |
| Vector Database | FAISS |
| Backend | FastAPI |
| Frontend | Streamlit |
| PDF Processing | PyPDF |

## 4. Project Structure

```text
09_Agricultural_Schemes_RAG/
│
├── backend/
│   └── rag_pipeline.py
│
├── frontend/
│   └── app.py
│
├── documents/
│   └── PDF documents
│
├── vectorstore/
│   └── FAISS index files
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## 5. Setup Instructions

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_api_key_here
```

Do not upload the `.env` file or API key to GitHub.

## 6. Running the Application

Start the FastAPI backend:

```bash
python -m uvicorn backend.main:app --reload
```

Start the Streamlit frontend in a separate terminal:

```bash
python -m streamlit run frontend/app.py
```

Open the local Streamlit URL displayed in the terminal.

## 7. Application Workflow

1. Load agricultural scheme PDF documents.
2. Extract text from PDF pages.
3. Split text into manageable chunks.
4. Generate embeddings using OpenAI.
5. Store embeddings in FAISS.
6. Retrieve relevant document chunks for user questions.
7. Generate answers using GPT-4o-mini.
8. Display answers with source document names and page references.

## 8. Testing

The application was tested with questions on Tamil Nadu agricultural schemes, including micro-irrigation subsidies.

The application successfully generated an answer and displayed relevant PDF source references.

## 9. Purpose

This project demonstrates how Retrieval-Augmented Generation (RAG) can be applied to government document intelligence, making information easier to discover and access through natural-language questions.