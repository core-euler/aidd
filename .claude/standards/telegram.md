# Telegram Standard

Telegram Bot API, Mini Apps, platform specifics.

## Rate Limits

- Groups: 20 messages/minute
- Private messages: 30 messages/second (spread across users)
- Single user: max 1 message/second
- Multiple media: use `sendMediaGroup`
- Implementation: `asyncio.Semaphore(20)` + handle `RetryAfter` with `e.timeout` sleep

## Message Limits

- Text: max 4096 characters
- Caption: max 1024 characters
- Inline results: max 50
- Split long messages at `\n` before the limit, send in parts

## Error Handling

- `TelegramForbiddenError` (bot blocked): mark user as inactive in DB
- `TelegramBadRequest`: log and re-raise
- `TelegramAPIError` (generic): retry after 1 second
- All errors logged via structlog

## Formatting

- Primary parse mode: **HTML** (via aiogram utilities `hbold`, `hcode`, `hlink`)
- HTML preferred over MarkdownV2 (fewer escaping issues)

## Mini Apps (WebApp)

- Open button: `InlineKeyboardButton` with `web_app=WebAppInfo(url=...)`
- `initData` validation is mandatory: HMAC-SHA256 with key = HMAC("WebAppData", bot_token)
- Never trust WebApp data without hash validation

## Webhooks vs Polling

- **Development**: polling (`dp.start_polling()`)
- **Production**: webhooks
- Webhook requirements: HTTPS, valid SSL, port 443/80/88/8443, response < 1 second
- On startup: `set_webhook()` with `drop_pending_updates=True`
- On shutdown: `delete_webhook()`

## Deep Links

- Format: `https://t.me/{bot_username}?start={payload}`
- Handling: `CommandStart(deep_link=True)` + `command.args`

## Privacy

- Store minimum data: `user_id`, `username` (optional), `created_at`
- Do not store: phone numbers, full chat history, location (without consent)
- Implement `/deletedata` command for user data deletion

## Required

- Validate all data from Telegram (especially WebApp initData)
- Rate limiting via semaphore
- Graceful error handling (blocks, API errors)
- Webhooks in production
- Split long messages
- `callback.answer()` on every callback query
- structlog for all interactions
- User data deletion capability

## Forbidden

- Ignoring rate limits
- Trusting WebApp data without validation
- Storing unnecessary user data
- Polling in production
- Messages > 4096 characters without splitting
- Ignoring callback queries
- Hardcoded bot token
- Blocking operations in async handlers
