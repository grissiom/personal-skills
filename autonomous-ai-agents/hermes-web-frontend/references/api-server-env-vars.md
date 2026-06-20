# API Server Environment Variables

All variables go in `~/.hermes/.env`. The API Server platform adapter (`gateway/platforms/api_server.py`) reads these at startup.

## Required

| Variable | Description | Default |
|----------|-------------|---------|
| `API_SERVER_ENABLED` | Enable the API Server platform | `false` |
| `API_SERVER_KEY` | Authentication key for OpenAI-compatible API calls | (empty) |

Without both of these, the API Server adapter won't load. Setting `API_SERVER_KEY` alone also enables it (the adapter treats non-empty key as implicit enable).

## Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `API_SERVER_PORT` | TCP port to listen on | `8642` |
| `API_SERVER_HOST` | Bind address | `0.0.0.0` |
| `API_SERVER_CORS_ORIGINS` | Comma-separated CORS origins for browser UIs | (empty) |
| `API_SERVER_MODEL_NAME` | Model name advertised via `/v1/models` | `hermes-agent` |

## CORS Details

- When set, `Access-Control-Allow-Origin` matches the request's `Origin` header exactly (no wildcard)
- Each origin must include scheme and port, e.g. `http://localhost:3000,http://127.0.0.1:3000`
- Without CORS, browser-based UIs served from different ports will fail with CORS errors

## Port Mapping

```
Browser (:3000) ──fetch()──▶ Hermes API Server (:8642)
```

The default API Server port (8642) is chosen to avoid conflicts with common development ports (3000, 8080, 5173, etc.).

## Gateway Lifecycle

The API Server starts and stops with the Hermes gateway:
- `hermes gateway run` — starts API Server alongside other platforms
- `hermes gateway install` — installs as systemd user service
- `hermes gateway stop` — stops API Server

API Server is excluded from gateway reset notifications (together with `webhook`).
