"""RAG router — upload documents and chat with them."""

import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from src.config import UPLOAD_DIR
from src.utils.rag import get_rag_engine, RAG_AVAILABLE

router = APIRouter()


class RAGChatRequest(BaseModel):
    question: str
    model: str = "llama3"


class RAGChatResponse(BaseModel):
    answer: str
    sources: list[str]


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for RAG."""
    if not RAG_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="RAG not available. Install: pip install langchain-community chromadb sentence-transformers"
        )

    # Validate file type
    allowed = (".pdf", ".txt", ".md")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {allowed}")

    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Load into vectorstore
    try:
        engine = get_rag_engine()
        chunk_count = engine.load_document(file_path)
        return {
            "status": "ok",
            "filename": file.filename,
            "chunks": chunk_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.post("/chat", response_model=RAGChatResponse)
async def rag_chat(req: RAGChatRequest):
    """Chat with uploaded documents."""
    if not RAG_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="RAG not available. Install: pip install langchain-community chromadb sentence-transformers"
        )

    engine = get_rag_engine()

    # Get sources
    sources = engine.query(req.question)

    # Get answer
    answer = engine.chat(req.question, model=req.model)

    return RAGChatResponse(
        answer=answer,
        sources=sources,
    )


@router.get("/documents")
async def list_documents():
    """List uploaded documents."""
    files = []
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            files.append({
                "filename": f,
                "size": os.path.getsize(os.path.join(UPLOAD_DIR, f)),
            })
    return {"documents": files, "count": len(files)}
