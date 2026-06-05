"""Chat router — chat with local LLM."""

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.config import OLLAMA_URL, DEFAULT_MODEL

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    model: str = DEFAULT_MODEL
    system_prompt: str = "You are a helpful assistant."
    temperature: float = 0.7


class ChatResponse(BaseModel):
    response: str
    model: str
    done: bool


@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Chat with local LLM."""
    payload = {
        "model": req.model,
        "messages": [
            {"role": "system", "content": req.system_prompt},
            {"role": "user", "content": req.message},
        ],
        "stream": False,
        "options": {"temperature": req.temperature},
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()

        return ChatResponse(
            response=data.get("message", {}).get("content", ""),
            model=req.model,
            done=data.get("done", True),
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cannot connect to Ollama: {str(e)}")


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    """Chat with streaming response."""
    payload = {
        "model": req.model,
        "messages": [
            {"role": "system", "content": req.system_prompt},
            {"role": "user", "content": req.message},
        ],
        "stream": True,
        "options": {"temperature": req.temperature},
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.send(
                client.build_request("POST", f"{OLLAMA_URL}/api/chat", json=payload),
                stream=True,
            )
            resp.raise_for_status()

            async def generate():
                async for line in resp.aiter_lines():
                    if line:
                        yield line + "\n"

        from starlette.responses import StreamingResponse
        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cannot connect to Ollama: {str(e)}")
