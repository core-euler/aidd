# Shared Rules

All agents and commands inherit these rules. Don't repeat them elsewhere.

## Process
- Flow: `/discovery` → `/plan` → `/implement` → `/test` → `/review` → `/ship`
- No code without approved `/plan`
- No architecture changes during `/implement`
- Don't touch working code when adding new functionality
- First phase = client-facing side (what users can interact with)

## Documentation
- No code in project documentation (spec, phases, issues) — describe with words only
- Exception: anti-patterns in issues.md may include minimal code examples
- One current version of each document (no spec-v1, spec-v2 duplicates)
- Changelog is maintained separately in docs/changelog.md

## Context Management
- Load only related modules into context
- Always load spec.md for any task
- Don't load documentation of unrelated modules

## Code
- Type hints required
- Handlers → Services → Repositories (no business logic in handlers)
- Environment variables only (no hardcoded secrets)
- Structured JSON logging
- Tests: >80% coverage

## AI Features
- Prompts versioned (no magic strings)
- Retry with exponential backoff
- Fallback behavior defined
- Log: model, tokens, cost, latency

## Docker
- All code must work in `docker-compose`
- Validate cold start before shipping
- Health checks required

## Quality Gates

| Gate | Authority | Blocks If |
|------|-----------|-----------|
| Plan | Tech Lead | Architecture unclear or violates standards |
| Test | QA | Acceptance criteria not met |
| Review | Reviewer | Code quality or security issues |
| Ship | Tech Lead + DevOps | Docker fails or secrets hardcoded |

## Standards
See `standards/` for: aiogram, docker, telegram, rag, testing
