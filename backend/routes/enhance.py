from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional

from services.prompt_enhancer import prompt_enhancer

router = APIRouter()


class EnhanceRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    negative_prompt: Optional[str] = None
    provider: Literal["local", "ollama", "lmstudio"] = "local"
    model: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 512
    temperature: float = 0.7
    seed: int = 42
    enhancer_repo: Optional[str] = None


class EnhanceResponse(BaseModel):
    enhanced: str
    negative_prompt: Optional[str] = None
    filename: Optional[str] = None


def _fallback_filename(text: str) -> Optional[str]:
    words = []
    for raw in text.lower().split():
        cleaned = "".join(ch for ch in raw if ch.isalnum())
        if cleaned:
            words.append(cleaned)
        if len(words) >= 8:
            break
    if not words:
        return None
    return " ".join(words)


@router.post("/enhance", response_model=EnhanceResponse)
async def enhance_prompt(req: EnhanceRequest):
    try:
        enhanced, negative = await prompt_enhancer.enhance_with_negative(
            prompt=req.prompt,
            negative_prompt=req.negative_prompt,
            provider=req.provider,
            model=req.model,
            base_url=req.base_url,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            seed=req.seed,
            enhancer_repo=req.enhancer_repo,
        )
        filename = await prompt_enhancer.enhance_filename(
            prompt=enhanced,
            provider=req.provider,
            model=req.model,
            base_url=req.base_url,
            max_tokens=min(req.max_tokens, 64),
            temperature=0.3,
            seed=req.seed,
        )
        if not filename:
            filename = _fallback_filename(enhanced)
        return EnhanceResponse(enhanced=enhanced, negative_prompt=negative, filename=filename)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/enhance/models")
async def list_enhance_models(
    provider: Literal["local", "ollama", "lmstudio"], base_url: Optional[str] = None
):
    """List available models for prompt enhancement.

    Returns model list with metadata:
    - models: List of model IDs (for backward compatibility)
    - model_details: List of full model objects with id, display_name, state, type
    """
    try:
        model_details = await prompt_enhancer.list_models(provider=provider, base_url=base_url)
        # Return both formats: simple list for backward compat, details for new UI
        return {
            "models": [m["id"] for m in model_details],
            "model_details": model_details
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
