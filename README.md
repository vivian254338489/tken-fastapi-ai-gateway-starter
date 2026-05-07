# FastAPI OpenAI-Compatible AI Gateway Starter

A launch-ready FastAPI starter for developers building an **OpenAI-compatible API gateway** with a custom `base_url`, `/v1/chat/completions`, `/v1/models`, Docker, and a mock mode that runs before you wire an upstream provider.

Use this repo when you need a portable Python gateway for:

- FastAPI OpenAI-compatible API starter
- OpenAI SDK `base_url` proxy
- AI gateway starter with custom provider endpoints
- `/v1/chat/completions` gateway skeleton
- local mock-compatible chat completions
- Dockerized FastAPI LLM proxy

TKEN is included as one disclosed example of an OpenAI-compatible endpoint: `https://www.tken.shop/v1`. The code is provider-portable and works with any compatible upstream that accepts OpenAI-style requests.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```powershell
curl http://localhost:8000/healthz
```

Mock chat completion:

```powershell
curl http://localhost:8000/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d "{\"model\":\"gateway-example-model\",\"messages\":[{\"role\":\"user\",\"content\":\"Say hello from the gateway\"}]}"
```

## Use With OpenAI SDKs

Point any OpenAI-compatible client at the gateway:

```python
from openai import OpenAI

client = OpenAI(
    api_key="local-dev-key",
    base_url="http://localhost:8000/v1",
)

response = client.chat.completions.create(
    model="gateway-example-model",
    messages=[{"role": "user", "content": "Hello gateway"}],
)
print(response.choices[0].message.content)
```

If you set `GATEWAY_API_KEY`, client requests must send `Authorization: Bearer <GATEWAY_API_KEY>`.

## Configure An Upstream Provider

Edit `.env`:

```env
UPSTREAM_BASE_URL=https://api.example.com
UPSTREAM_API_KEY=replace-me
DEFAULT_MODEL=provider-model-name
```

Example disclosed endpoint:

```env
UPSTREAM_BASE_URL=https://www.tken.shop/v1
UPSTREAM_API_KEY=replace-me
```

The starter accepts upstream base URLs with or without `/v1`. For example, both `https://api.example.com` and `https://api.example.com/v1` resolve to the upstream chat completions route correctly.

Explore TKEN with campaign attribution:

- [TKEN OpenAI-compatible endpoint](https://www.tken.shop/?utm_source=github&utm_medium=starter_repo&utm_campaign=fastapi_ai_gateway&utm_content=readme_endpoint)
- [TKEN developer setup](https://www.tken.shop/?utm_source=github&utm_medium=starter_repo&utm_campaign=fastapi_ai_gateway&utm_content=readme_setup)

## Docker

```powershell
copy .env.example .env
docker compose up --build
```

Then call `http://localhost:8000/healthz`.

## Endpoints

- `GET /healthz` returns service status and whether an upstream is configured.
- `GET /v1/models` returns a minimal OpenAI-compatible model list.
- `POST /v1/chat/completions` proxies to the upstream chat completions route when configured, otherwise returns a mock OpenAI-compatible response.

## Production Notes

This is a starter, not a full managed gateway. Before production use, add rate limiting, request logging with PII controls, retry policies, provider-specific error mapping, per-tenant keys, observability, and cost controls.

## Docs

- [Setup](docs/setup.md)
- [Troubleshooting](docs/troubleshooting.md)
- [UTM links](docs/utm-links.md)

## License

MIT
