# Testing Standard

TDD approach. pytest + pytest-asyncio. All tests run in docker-compose.

## Structure

```
tests/
├── unit/               # Fast, isolated (mocks instead of real dependencies)
│   ├── test_services.py
│   ├── test_repositories.py
│   └── test_utils.py
├── integration/        # With real DB and Redis
│   ├── test_api_endpoints.py
│   ├── test_bot_handlers.py
│   └── test_celery_tasks.py
├── e2e/                # End-to-end (slow)
│   └── test_user_flows.py
├── fixtures/           # Test data factories
│   ├── telegram_fixtures.py
│   └── database_fixtures.py
└── conftest.py         # Shared fixtures and configuration
```

## Test Pyramid

- **Unit** (most): mock dependencies, test services and utilities in isolation
- **Integration** (moderate): real DB/Redis in test docker-compose, test repositories and API
- **E2E** (minimal): full user scenarios

## Test Pattern

- Structure: **Arrange → Act → Assert**
- Naming: `test_<what>_<condition>_<expectation>` (e.g. `test_register_user_already_exists_returns_existing`)
- Test both success and error paths
- Edge cases and boundary values

## Mocking

- Telegram Bot API: `Mock(spec=types.Message)` with `AsyncMock` for methods
- Services for handlers: `AsyncMock` injected as parameter
- OpenAI / external APIs: `AsyncMock` with prepared return_value
- Real APIs are never called in tests

## FSM Tests

- Use `MemoryStorage` + `FSMContext` for testing state transitions
- Verify: correct state transition, data persistence, state clearing on completion

## Fixtures

- Shared fixtures in `conftest.py`: event loop, redis client, test DB session
- Telegram-specific in `fixtures/telegram_fixtures.py`: message_mock and callback_query_mock factories
- DB fixtures: create/drop tables via `Base.metadata`, transactions with rollback

## pytest Configuration

- `asyncio_mode = auto`
- Markers: `unit`, `integration`, `e2e`
- Coverage: `--cov` with `--cov-fail-under=80`
- Verbose: `-v --strict-markers`

## Coverage Thresholds

| Layer | Minimum |
|-------|---------|
| Overall | 80% |
| Services | 90% |
| Handlers | 85% |
| Repositories | 90% |

Coverage exclusions: `tests/*`, `venv/*`, `*/migrations/*`, `__repr__`, `__main__`

## Running

- In docker: `docker-compose -f docker-compose.test.yml up --abort-on-container-exit`
- Test docker-compose: separate `postgres_test` and `redis_test` with health checks
- Test services use their own DSN/URL, isolated from dev/prod

## Required

- Tests before implementation (TDD)
- Mocks for all external APIs
- Tests in docker-compose
- Coverage > 80%
- Fixtures for reusable data
- Both paths: success and error

## Forbidden

- Calling real APIs in tests
- Production DB for tests
- Hardcoded test data (use fixtures)
- Shared state between tests
- Ignoring failing tests
