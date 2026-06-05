"""RAG implementation — chat with your documents using ChromaDB + Ollama."""

import os
import httpx
from typing import Optional
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

from src.config import OLLAMA_URL, DEFAULT_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, UPLOAD_DIR


class RAGEngine:
    """RAG engine using ChromaDB + Ollama embeddings."""

    def __init__(self, persist_dir: str = "chroma_db"):
        self.persist_dir = persist_dir
        self.embeddings = OllamaEmbeddings(
            model=DEFAULT_MODEL,
            base_url=OLLAMA_URL,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        self.vectorstore: Optional[Chroma] = None

    def load_document(self, file_path: str) -> int:
        """Load a document and add to vectorstore. Returns chunk count."""
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext in (".txt", ".md"):
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)

        if self.vectorstore is None:
            self.vectorstore = Chroma.from_documents(
                chunks,
                self.embeddings,
                persist_directory=self.persist_dir,
            )
        else:
            self.vectorstore.add_documents(chunks)

        return len(chunks)

    def query(self, question: str, k: int = 4) -> list[str]:
        """Query the vectorstore for relevant chunks."""
        if self.vectorstore is None:
            return []

        results = self.vectorstore.similarity_search(question, k=k)
        return [doc.page_content for doc in results]

    def chat(self, question: str, model: str = DEFAULT_MODEL) -> str:
        """Chat with RAG context."""
        # Get relevant chunks
        chunks = self.query(question)
        context = "\n\n".join(chunks) if chunks else "No relevant documents found."

        # Build prompt
        system_prompt = f"""You are a helpful assistant that answers questions based on the provided context.

Context from documents:
{context}

Answer the question based on the context above. If the context doesn't contain enough information, say so."""

        # Call Ollama
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            "stream": False,
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(f"{OLLAMA_URL}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
            return data.get("message", {}).get("content", "")
        except Exception as e:
            return f"Error: {str(e)}"


# Singleton
_rag_engine = None


def get_rag_engine() -> RAGEngine:
    """Get or create RAG engine instance."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
