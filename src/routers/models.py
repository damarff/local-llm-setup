"""Models router — list, pull, and manage Ollama models."""

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.config import OLLAMA_URL

router = APIRouter()


class PullRequest(BaseModel):
    model: str


class ModelInfo(BaseModel):
    name: str
    size: int
    modified_at: str


@router.get("/")
async def list_models():
    """List all available models."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            resp.raise_for_status()
            data = resp.json()

        models = data.get("models", [])
        return {
            "models": [
                ModelInfo(
                    name=m.get("name", ""),
                    size=m.get("size", 0),
                    modified_at=m.get("modified_at", ""),
                )
                for m in models
            ],
            "count": len(models),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cannot connect to Ollama: {str(e)}")


@router.post("/pull")
async def pull_model(req: PullRequest):
    """Download a model from Ollama registry."""
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/pull",
                json={"name": req.model},
            )
            resp.raise_for_status()
            return {"status": "ok", "model": req.model}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Pull failed: {str(e)}")


@router.delete("/{model_name}")
async def delete_model(model_name: str):
    """Delete a model."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{OLLAMA_URL}/api/delete",
                json={"name": model_name},
            )
            resp.raise_for_status()
        return {"status": "deleted", "model": model_name}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Delete failed: {str(e)}")


@router.get("/{model_name}")
async def get_model_info(model_name: str):
    """Get detailed info about a model."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/show",
                json={"name": model_name},
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cannot get model info: {str(e)}")
