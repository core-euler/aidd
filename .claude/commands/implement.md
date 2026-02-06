# /implement

**Goal**: Build functionality following approved plan. No architectural decisions.

**When**: After `/plan` approved by Tech Lead.

**Agents**: backend_dev, ai_engineer (for AI tasks)

## Process

| Step | Owner | Do | Output |
|------|-------|----|--------|
| Setup | Dev | Review plan, identify scope, prepare env vars | Clear scope |
| Implementation | Dev | Follow architecture exactly, handlers→services→repos, structured logging | Working code |
| Local Testing | Dev | Test in docker-compose, verify acceptance criteria, test edge cases | Validated code |
| Documentation | Dev | Update `.env.example`, document API changes | Documented code |

## Rules
Inherits [RULES.md](../RULES.md) plus:
- Follow approved plan exactly (no scope changes)
- If plan is wrong, return to `/plan` first

## Gates
- **Blocker**: Deviates from plan
- **Blocker**: Doesn't run in docker-compose
- **Blocker**: Hardcoded secrets
- **Blocker**: AI prompts not versioned

## Authority
None - must follow approved plan. Changes require returning to `/plan`.

**Next**: `/test`
