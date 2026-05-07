import os
import time
from typing import Any

import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field


APP_NAME = "FastAPI OpenAI-Compatible AI Gateway Starter"
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gateway-example-model")
UPSTREAM_BASE_URL = os.getenv("UPSTREAM_BASE_URL", "").rstrip("/")
UPSTREAM_API_KEY = os.getenv("UPSTREAM_API_KEY", "")
GATEWAY_API_KEY = os.getenv("GATEWAY_API_KEY", "")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))

app = FastAPI(
    title=APP_NAME,
    description="A portable FastAPI starter for OpenAI-compatible chat completion gateways.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


class ChatMessage(BaseModel):
    role: str
    content: str | list[dict[str, Any]]


class ChatCompletionRequest(BaseModel):
    model: str = Field(default=DEFAULT_MODEL)
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None


def _require_gateway_key(authorization: str | None) -> None:
    if not GATEWAY_API_KEY:
        return
    expected = f"Bearer {GATEWAY_API_KEY}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing gateway API key")


def _upstream_url(v1_path: str) -> str:
    if not UPSTREAM_BASE_URL:
        raise HTTPException(status_code=500, detail="UPSTREAM_BASE_URL is not configured")
    path = v1_path if UPSTREAM_BASE_URL.endswith("/v1") else f"/v1{v1_path}"
    return f"{UPSTREAM_BASE_URL}{path}"


def _mock_chat_completion(payload: ChatCompletionRequest) -> dict[str, Any]:
    now = int(time.time())
    last_user = next((m.content for m in reversed(payload.messages) if m.role == "user"), "")
    if isinstance(last_user, list):
        last_user = "a multimodal message"

    content = (
        "Mock gateway response. Configure UPSTREAM_BASE_URL and UPSTREAM_API_KEY "
        f"to proxy this request. Last user message: {last_user}"
    )

    return {
        "id": f"chatcmpl_mock_{now}",
        "object": "chat.completion",
        "created": now,
        "model": payload.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": sum(len(str(m.content).split()) for m in payload.messages),
            "completion_tokens": len(content.split()),
            "total_tokens": sum(len(str(m.content).split()) for m in payload.messages) + len(content.split()),
        },
    }


async def _proxy_upstream(path: str, body: dict[str, Any], stream: bool) -> JSONResponse | StreamingResponse:
    headers = {"Content-Type": "application/json"}
    if UPSTREAM_API_KEY:
        headers["Authorization"] = f"Bearer {UPSTREAM_API_KEY}"

    url = _upstream_url(path)
    timeout = httpx.Timeout(REQUEST_TIMEOUT_SECONDS)

    if stream:
        client = httpx.AsyncClient(timeout=timeout)
        request = client.build_request("POST", url, json=body, headers=headers)
        response = await client.send(request, stream=True)
        if response.status_code >= 400:
            text = await response.aread()
            await client.aclose()
            raise HTTPException(status_code=response.status_code, detail=text.decode("utf-8", errors="replace"))

        async def event_stream():
            try:
                async for chunk in response.aiter_bytes():
                    yield chunk
            finally:
                await response.aclose()
                await client.aclose()

        return StreamingResponse(
            event_stream(),
            status_code=response.status_code,
            media_type=response.headers.get("content-type", "text/event-stream"),
        )

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, json=body, headers=headers)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return JSONResponse(status_code=response.status_code, content=response.json())


@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "fastapi-openai-compatible-ai-gateway-starter",
        "upstream_configured": bool(UPSTREAM_BASE_URL),
    }


@app.get("/v1/models")
async def models(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    _require_gateway_key(authorization)
    return {
        "object": "list",
        "data": [
            {
                "id": DEFAULT_MODEL,
                "object": "model",
                "created": 0,
                "owned_by": "gateway",
            }
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(
    payload: ChatCompletionRequest,
    request: Request,
    authorization: str | None = Header(default=None),
) -> JSONResponse | StreamingResponse:
    _require_gateway_key(authorization)
    body = await request.json()
    if UPSTREAM_BASE_URL:
        return await _proxy_upstream("/v1/chat/completions", body, payload.stream)
    return JSONResponse(content=_mock_chat_completion(payload))
