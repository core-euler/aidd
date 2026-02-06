# AI Development Framework

Agent-based development for Telegram bots, Mini Apps, AI/LLM integrations, and Docker-based systems.

## Quick Start

```bash
cp .env.example .env
docker-compose up -d
```

## Workflow

```
/discovery → /plan → /implement → /test → /review → /ship
     ↓          ↓         ↓          ↓        ↓        ↓
    PO      Tech Lead   Dev/AI     QA    Reviewer  DevOps
  + Arch    approves   Engineer         approves  validates
```

| Command | Purpose | Output |
|---------|---------|--------|
| `/discovery` | Understand requirements | Problem statement, scope |
| `/plan` | Design architecture | Tasks, **Tech Lead approval** |
| `/implement` | Build features | Working code |
| `/integrate_ai` | Add AI features | Versioned prompts |
| `/test` | Validate functionality | **QA approval** |
| `/review` | Check code quality | **Reviewer approval** |
| `/fix` | Fix a bug minimally | Fixed code, issues.md entry |
| `/integrate` | Connect modules together | Working integration |
| `/refactor` | Improve without changing behavior | Cleaner code |
| `/ship` | Deploy to production | Release |

## Roles

| Role | Focus | Can Block? |
|------|-------|------------|
| Product Owner | Requirements, scope | - |
| Architect | System design | - |
| **Tech Lead** | Standards, approval | **Yes** |
| Backend Dev | Implementation | - |
| AI Engineer | LLM/RAG | - |
| DevOps | Docker, deploy | - |
| Fixer | Bug fixes, minimal changes | - |
| Integrator | Module integration | - |
| API Specialist | External APIs, contracts | - |
| **QA** | Testing | **Yes** |
| **Reviewer** | Code quality | **Yes** |

## Key Rules

See `RULES.md` for full list. Critical ones:

1. No code without `/plan` approval
2. No shipping without `/test` + `/review`
3. Docker-compose is source of truth
4. AI prompts must be versioned
5. No hardcoded secrets

## Files

| File | Purpose |
|------|---------|
| `RULES.md` | Shared rules (single source of truth) |
| `PROCESS.md` | Development process and phase workflow |
| `agents/` | Role definitions |
| `commands/` | Command details |
| `standards/` | Tech patterns (aiogram, docker, rag, testing, telegram) |

## Documentation Principles

- No code in project documentation — describe behavior with words
- One current version of each document (no duplicates)
- Phase-based workflow: document → test → implement → debug → result
- See `RULES.md` for full documentation and context management rules
