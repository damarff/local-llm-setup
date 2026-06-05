"""Example: RAG — chat with your documents."""

import httpx

API_URL = "http://localhost:8000"


def upload_document(file_path: str) -> dict:
    """Upload a document for RAG."""
    with open(file_path, "rb") as f:
        resp = httpx.post(
            f"{API_URL}/rag/upload",
            files={"file": (file_path, f)},
            timeout=60.0,
        )
    resp.raise_for_status()
    return resp.json()


def rag_chat(question: str, model: str = "llama3") -> dict:
    """Chat with uploaded documents."""
    resp = httpx.post(
        f"{API_URL}/rag/chat",
        json={"question": question, "model": model},
        timeout=120.0,
    )
    resp.raise_for_status()
    return resp.json()


def list_documents() -> list:
    """List uploaded documents."""
    resp = httpx.get(f"{API_URL}/rag/documents")
    resp.raise_for_status()
    return resp.json()["documents"]


if __name__ == "__main__":
    # Upload a document
    print("Uploading document...")
    result = upload_document("example.pdf")
    print(f"Uploaded: {result['filename']} ({result['chunks']} chunks)")

    # List documents
    print("\nUploaded documents:")
    for doc in list_documents():
        print(f"  - {doc['filename']}")

    # Chat with document
    print("\nAsking question...")
    answer = rag_chat("What is the main topic of this document?")
    print(f"Answer: {answer['answer']}")
    print(f"Sources: {len(answer['sources'])} relevant chunks")
