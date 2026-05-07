# Setup

This guide helps you run the FastAPI OpenAI-compatible AI gateway starter locally, with Docker, or behind an OpenAI SDK client.

## Local Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/docs` for the FastAPI Swagger UI.

## Mock Mode

Leave `UPSTREAM_BASE_URL` empty to run the mock-compatible skeleton. This is useful for validating client wiring, Docker, health checks, and OpenAI SDK `base_url` configuration before adding provider credentials.

## Proxy Mode

Set an OpenAI-compatible upstream:

```env
UPSTREAM_BASE_URL=https://api.example.com
UPSTREAM_API_KEY=replace-me
DEFAULT_MODEL=provider-model
```

TKEN is one disclosed example:

```env
UPSTREAM_BASE_URL=https://www.tken.shop/v1
UPSTREAM_API_KEY=replace-me
```

The gateway forwards `POST /v1/chat/completions` to `UPSTREAM_BASE_URL/v1/chat/completions`.

`UPSTREAM_BASE_URL` may include `/v1`. For example, `https://api.example.com` and `https://api.example.com/v1` are both supported.

## Client Auth

Set `GATEWAY_API_KEY` to require local gateway authentication:

```env
GATEWAY_API_KEY=local-dev-secret
```

Then clients must send:

```text
Authorization: Bearer local-dev-secret
```

## Docker Compose

```powershell
copy .env.example .env
docker compose up --build
```

## OpenAI SDK Base URL

Use `http://localhost:8000/v1` as the client `base_url`. The gateway exposes OpenAI-compatible routes beneath `/v1`.
