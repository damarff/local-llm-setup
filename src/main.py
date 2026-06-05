"""Local LLM API — FastAPI backend for Ollama."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import HOST, PORT, UPLOAD_DIR
from src.routers import chat, models, rag

# Create upload directory
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Local LLM API",
    description="API for local LLM inference via Ollama",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(models.router, prefix="/models", tags=["Models"])
app.include_router(rag.router, prefix="/rag", tags=["RAG"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    import httpx
    from src.config import OLLAMA_URL

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags", timeout=5.0)
            ollama_status = "connected" if resp.status_code == 200 else "error"
    except Exception:
        ollama_status = "disconnected"

    return {
        "status": "healthy",
        "ollama": ollama_status,
    }
