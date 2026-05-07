# Troubleshooting

## `401 Invalid or missing gateway API key`

`GATEWAY_API_KEY` is set in `.env`, but the request does not include the matching bearer token.

Fix:

```powershell
curl http://localhost:8000/v1/models -H "Authorization: Bearer your-key"
```

## Mock Responses Instead Of Provider Responses

`UPSTREAM_BASE_URL` is empty. Add a provider-compatible base URL to `.env` and restart the server.

## Upstream 404

Set `UPSTREAM_BASE_URL` to the provider root or OpenAI-compatible versioned root. The gateway supports values with or without `/v1`.

For example, if your provider exposes `https://api.example.com/v1/chat/completions`, use:

```env
UPSTREAM_BASE_URL=https://api.example.com
```

or:

```env
UPSTREAM_BASE_URL=https://api.example.com/v1
```

## Docker Container Starts But Requests Fail

Check:

- `.env` exists next to `docker-compose.yml`
- `UPSTREAM_API_KEY` is valid when proxy mode is enabled
- port `8000` is not already in use
- the provider accepts OpenAI-compatible JSON payloads

## Streaming Issues

This starter passes through streaming bytes from the upstream provider. If a client stalls, verify that the upstream response has a streaming content type and that no reverse proxy buffers server-sent events.
