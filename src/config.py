"""Configuration loader — reads from .env file."""

import os
from dotenv import load_dotenv

load_dotenv()

# Ollama
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3")

# FastAPI
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# RAG
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
