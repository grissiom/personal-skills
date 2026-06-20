# WeChat / Weixin (iLink Bot API) — Implementation Details

Source: `gateway/platforms/weixin.py` (~2170 lines)

## Base URLs

| Service | URL |
|---------|-----|
| iLink API | `https://ilinkai.weixin.qq.com` |
| CDN (media) | `https://novac2c.cdn.weixin.qq.com/c2c` |

Defaults set as constants `ILINK_BASE_URL` and `WEIXIN_CDN_BASE_URL`.

## API Endpoints

| Endpoint | Constant | Use |
|----------|----------|-----|
| `ilink/bot/getupdates` | `EP_GET_UPDATES` | Long-poll inbound messages |
| `ilink/bot/sendmessage` | `EP_SEND_MESSAGE` | Send text/media messages |
| `ilink/bot/sendtyping` | `EP_SEND_TYPING` | Typing indicator |
| `ilink/bot/getconfig` | `EP_GET_CONFIG` | Get typing tickets, config |
| `ilink/bot/getuploadurl` | `EP_GET_UPLOAD_URL` | Get CDN upload URL for media |
| `ilink/bot/get_bot_qrcode` | `EP_GET_BOT_QR` | QR code for bot login |
| `ilink/bot/get_qrcode_status` | `EP_GET_QR_STATUS` | Poll QR scan status |

## Key Constants

| Constant | Value | Meaning |
|----------|-------|---------|
| `ILINK_APP_ID` | `"bot"` | iLink app identifier |
| `CHANNEL_VERSION` | `"2.2.0"` | Protocol version |
| `ILINK_APP_CLIENT_VERSION` | `(2 << 16) \| (2 << 8) \| 0` | Client version packed int |
| `LONG_POLL_TIMEOUT_MS` | `35_000` | getupdates long-poll timeout |
| `API_TIMEOUT_MS` | `15_000` | sendmessage/getuploadurl timeout |
| `CONFIG_TIMEOUT_MS` | `10_000` | getconfig timeout |
| `QR_TIMEOUT_MS` | `35_000` | QR polling timeout |
| `MAX_CONSECUTIVE_FAILURES` | `3` | Threshold before backoff |
| `RETRY_DELAY_SECONDS` | `2` | Normal retry delay |
| `BACKOFF_DELAY_SECONDS` | `30` | Backoff after consecutive failures |
| `MESSAGE_DEDUP_TTL_SECONDS` | `300` | 5-minute dedup window |

## Error Codes

| Code | Meaning | Handling |
|------|---------|----------|
| `-14` | Session expired | Triggers full reconnect |
| `-2` | Rate limit | Backoff + retry |
| `ret=-2, errcode=-2, errmsg="unknown error"` | Stale session (not rate limit) | Same as `-14` — triggers reconnect |

Detected by `_is_stale_session_ret()` using both `ret`/`errcode` values plus lowercase matching on `errmsg`.

## Media Types

| Constant | Value | Type |
|----------|-------|------|
| `MEDIA_IMAGE` | `1` | Images |
| `MEDIA_VIDEO` | `2` | Videos |
| `MEDIA_FILE` | `3` | Documents / generic files |
| `MEDIA_VOICE` | `4` | Voice messages (`.silk`) |

## Item Types (message items)

| Constant | Value | Content |
|----------|-------|--------|
| `ITEM_TEXT` | `1` | Text message body |
| `ITEM_IMAGE` | `2` | Image media item |
| `ITEM_VOICE` | `3` | Voice media item |
| `ITEM_FILE` | `4` | File media item |
| `ITEM_VIDEO` | `5` | Video media item |

## Message Types

| Constant | Value | Meaning |
|----------|-------|---------|
| `MSG_TYPE_USER` | `1` | Incoming from user |
| `MSG_TYPE_BOT` | `2` | Outgoing from bot |
| `MSG_STATE_FINISH` | `2` | Message completed |

## CDN Media Protocol

Media files use **AES-128-ECB** encryption (PKCS7 padding) for upload/download:

1. **Upload flow** — `_get_upload_url()` → get CDN upload URL → encrypt file with AES-128-ECB → POST ciphertext → server returns `x-encrypted-param` header → use as `encrypt_query_param` in message payload
2. **Download flow** — receive `encrypt_query_param` and `aes_key` → GET `cdn/download?encrypted_query_param=...` → AES-128-ECB decrypt

Key handling details (critical to get right):
- `aes_key` is 16 random bytes
- `aes_key_for_api` = `base64(hex(aes_key))`, **NOT** `base64(raw_aes_key)` — sending the wrong encoding causes images to show as grey boxes on the receiver side
- `filesize` = `_aes_padded_size(rawsize)` = `((rawsize + 1 + 15) // 16) * 16`
- `rawfilemd5` is MD5 of the original plaintext

## Headers

Every iLink POST request includes these headers (via `_headers()`):
- `Content-Type: application/json`
- `AuthorizationType: ilink_bot_token`
- `Authorization: Bearer {token}` (if token available)
- `Content-Length: {body_length}`
- `X-WECHAT-UIN: {random_4byte_uint_b64_encoded}` — random per-request
- `iLink-App-Id: bot`
- `iLink-App-ClientVersion: {ILINK_APP_CLIENT_VERSION}`

Every request body includes a `base_info` dict: `{"channel_version": "2.2.0"}`.

## CDN SSL

Tencent's iLink server may fail verification against some system CA stores (notably Homebrew's OpenSSL on macOS Apple Silicon). The adapter falls back to `certifi`'s Mozilla CA bundle when available. If `certifi` is not installed, uses `trust_env=True` (honors `SSL_CERT_FILE`).

## CDN URL Allowlist

To prevent SSRF, media download is restricted to these hosts:
- `novac2c.cdn.weixin.qq.com`
- `ilinkai.weixin.qq.com`
- `wx.qlogo.cn`
- `thirdwx.qlogo.cn`
- `res.wx.qq.com`
- `mmbiz.qpic.cn`
- `mmbiz.qlogo.cn`

Defined in `_WEIXIN_CDN_ALLOWLIST`.

## Stored Credentials

Accounts persisted at `~/.hermes/weixin/accounts/{account_id}.json` with perms `0o600`.
Context tokens per peer stored at `~/.hermes/weixin/accounts/{account_id}.context-tokens.json`.
Context token cache has a 600s TTL for typing tickets (`TypingTicketCache`).

## Markdown Adaptation for WeChat

The adapter converts Markdown to WeChat-friendly formatting:
- `# Heading` → `【Heading】`
- `## ... #### Heading` → `**Heading**`
- Tables → key-value list lines (`- Key: Value`)
- Long lines soft-wrapped at 120 chars (for WeChat copy-friendliness)
- Code blocks preserved as-is
- Blank lines collapsed to at most one

## Direct Send Helper

`send_weixin_direct()` is the cron/one-shot entry point. It bypasses the long-poll adapter lifecycle and uses the raw API. It reuses a live adapter's session if one exists (same token) for efficiency.

Environment variables for direct mode:
- `WEIXIN_TOKEN`
- `WEIXIN_ACCOUNT_ID`
- `WEIXIN_BASE_URL`
- `WEIXIN_CDN_BASE_URL`

## Chat Type Detection (`_guess_chat_type()`)

- If `room_id` or `chat_room_id` is present → `group` chat
- If `to_user_id` differs from `account_id` and `msg_type == 1` → `group` chat
- Otherwise → `dm` (direct message)
