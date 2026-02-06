# GameTODO Bot (spawn)

## Запуск

1. Скопируй пример окружения и заполни токен:

```bash
cp .env.example .env
```

2. Запусти проект:

```bash
docker-compose up --build
```

Бот начнёт принимать обновления через polling.

## Переменные окружения
- `BOT_TOKEN` — токен Telegram‑бота
- `DATABASE_URL` — строка подключения к PostgreSQL
- `POSTGRES_USER` — пользователь БД (должен совпадать с `DATABASE_URL`)
- `POSTGRES_PASSWORD` — пароль БД (должен совпадать с `DATABASE_URL`)
- `POSTGRES_DB` — имя БД (должно совпадать с `DATABASE_URL`)
- `TIMEZONE` — локальная таймзона пользователя (по умолчанию Europe/Moscow)
- `LOG_LEVEL` — уровень логирования
