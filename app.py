import os
from typing import Any, Dict

import httpx
from fastapi import FastAPI, Header, HTTPException, Request

app = FastAPI(title="TKEN FastAPI AI Gateway Starter")

BASE_URL = os.getenv("TKEN_BASE_URL", "https://www.tken.shop/v1").rstrip("/")
UPSTREAM_KEY = os.getenv("TKEN_API_KEY", "")
LOCAL_API_KEY = os.getenv("LOCAL_API_KEY", "local-dev-key")
LOW_COST_MODEL = os.getenv("LOW_COST_MODEL", "free-model")
PREMIUM_MODEL = os.getenv("PREMIUM_MODEL", "premium-gpt")
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() != "false" or not UPSTREAM_KEY or UPSTREAM_KEY == "your_tken_api_key"


def require_local_key(authorization: str | None):
    if authorization != f"Bearer {LOCAL_API_KEY}":
        raise HTTPException(status_code=401, detail="Missing or invalid local API key")


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "tken-fastapi-ai-gateway-starter",
        "upstream": BASE_URL,
        "demoMode": DEMO_MODE,
        "routes": [LOW_COST_MODEL, PREMIUM_MODEL],
    }


@app.get("/v1/models")
def models(authorization: str | None = Header(default=None)):
    require_local_key(authorization)
    return {
        "object": "list",
        "data": [
            {"id": LOW_COST_MODEL, "object": "model", "owned_by": "tken"},
            {"id": PREMIUM_MODEL, "object": "model", "owned_by": "tken"},
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request, authorization: str | None = Header(default=None)):
    require_local_key(authorization)
    payload: Dict[str, Any] = await request.json()
    model = payload.get("model") or LOW_COST_MODEL

    if DEMO_MODE:
        return {
            "id": "demo-chatcmpl",
            "object": "chat.completion",
            "model": model,
            "choices": [
                {"index": 0, "message": {"role": "assistant", "content": f"Demo response from {model}."}, "finish_reason": "stop"}
            ],
        }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {UPSTREAM_KEY}", "Content-Type": "application/json"},
            json=payload,
        )
    return response.json()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8795")))
