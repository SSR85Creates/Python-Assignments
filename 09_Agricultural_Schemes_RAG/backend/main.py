
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.rag_pipeline import build_vectorstore, ask_question

app = FastAPI(title="Agricultural Schemes RAG API")

vectorstore = None
index_stats = {}


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "Agricultural Schemes RAG API is running",
        "status": "online"
    }


@app.get("/stats")
def get_stats():
    return index_stats


@app.post("/index")
def index_documents():
    global vectorstore, index_stats

    try:
        vectorstore = build_vectorstore()

        index_stats = {
            "status": "indexed",
            "documents": len(vectorstore.docstore._dict),
            "message": "Documents indexed successfully"
        }

        return index_stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
def ask(request: QuestionRequest):
    if vectorstore is None:
        raise HTTPException(
            status_code=400,
            detail="Please index documents first"
        )

    try:
        answer, sources = ask_question(
            request.question,
            vectorstore
        )

        return {
            "question": request.question,
            "answer": answer,
            "sources": sources
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
