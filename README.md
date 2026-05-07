# TKEN FastAPI AI Gateway Starter

FastAPI-style OpenAI-compatible proxy starter with low-cost and premium model routes.

Default upstream API base:

```text
https://www.tken.shop/v1
```

Get an API key:

```text
https://www.tken.shop/?utm_source=github&utm_medium=readme&utm_campaign=tken_fastapi_ai_gateway_starter
```

## Quick Start

```bash
pip install fastapi uvicorn httpx
python app.py
```

The starter also includes demo mode so the files can be inspected and validated without credentials.

## Routes

| Route | Purpose |
| --- | --- |
| `/health` | local gateway health |
| `/v1/models` | OpenAI-compatible model list |
| `/v1/chat/completions` | OpenAI-compatible chat proxy |

## Environment

```env
TKEN_API_KEY=your_tken_api_key
TKEN_BASE_URL=https://www.tken.shop/v1
LOCAL_API_KEY=local-dev-key
LOW_COST_MODEL=free-model
PREMIUM_MODEL=premium-gpt
DEMO_MODE=true
```

## Disclosure

This project is TKEN-related tooling. It is not affiliated with FastAPI, OpenAI, Anthropic, ChatGPT, Claude, Codex, or OpenClaw.
