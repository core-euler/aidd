# Aiogram Standard

aiogram 3.x — Telegram bot framework.

## Architecture

- Layers: **Handlers → Services → Repositories**
- Handlers: routing, input validation, call service, send response only
- Services: all business logic, external API interactions
- Repositories: data access (SQLAlchemy async)
- Each layer in its own directory: `handlers/`, `services/`, `repositories/`

## Project Structure

```
bot/
├── handlers/          # Routers per feature (start.py, common.py, feature.py)
├── services/          # Business logic
├── repositories/      # Data access
├── middlewares/        # Logging, DI, auth
├── states/            # FSM StatesGroup definitions
├── keyboards/         # Keyboard factory functions (inline.py, reply.py)
├── filters/           # Custom filters
├── config.py          # pydantic_settings.BaseSettings + .env
└── main.py            # Entry point
```

## Required

- Configuration via `pydantic_settings.BaseSettings`, source: `.env`
- Each feature gets its own `Router`, registered in `main.py` via `dp.include_router()`
- Services injected into handlers through middleware (not global imports)
- FSM (`StatesGroup`) for any dialog > 1 step
- FSM storage = `RedisStorage` in production
- `callback.answer()` always called first in callback handlers
- All logs via `structlog` in JSON format with fields: `user_id`, `update_type`, `update_id`
- Global error handler via `@router.errors()` — logs and notifies user
- Keyboards are standalone functions in `keyboards/`, return ready Markup objects
- `allowed_updates` specified explicitly when starting polling/webhook

## Forbidden

- Business logic in handlers
- `MemoryStorage` in production
- Hardcoded tokens and secrets
- Blocking I/O in async handlers
- Ignoring callback queries (causes infinite spinner for user)
- Storing sensitive data in FSM state (use database)

## Middleware

- **LoggingMiddleware**: logs all incoming updates (update_id, user_id, update_type, result)
- **ServiceMiddleware**: creates DB session, instantiates repositories and services, injects into `data`
- Registration order: logging first, then DI

## Entry Point (main.py)

Initialization sequence:
1. Configure structlog (JSON processors)
2. Create `Bot` and `Dispatcher` with `RedisStorage`
3. Register middleware on `dp.update`
4. Register routers (errors first)
5. `dp.start_polling()` with `allowed_updates`
