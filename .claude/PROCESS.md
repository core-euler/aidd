# Development Process

**Workflow**: See `README.md`

## Project Documentation Structure

```
docs/
  spec.md          — project specification (single source of truth)
  changelog.md     — history of changes
  phases/          — phase documentation (phase-1.md, phase-2.md, ...)
  issues.md        — known issues, bugs, anti-patterns
  results/         — completed phase results (result-1.md, ...)
```

## Phase Workflow

Each phase follows this cycle:

1. **Document** — create `docs/phases/phase-N.md` with goals, scope, acceptance criteria
2. **Test** — write tests first (TDD), covering acceptance criteria
3. **Implement** — build until tests pass
4. **Debug** — if error found: document in `docs/issues.md` → fix → update spec if needed
5. **Result** — create `docs/results/result-N.md` as a marker of completed phase

## Quality Gates

| Gate | Owner | Blocks If |
|------|-------|-----------|
| Plan | Tech Lead | Architecture unclear or violates standards |
| Test | QA | Acceptance criteria not met |
| Review | Reviewer | Code quality or security issues |
| Ship | Tech Lead + DevOps | Docker fails, secrets hardcoded |

## Definition of Done

- [ ] Works in docker-compose (cold start)
- [ ] No hardcoded secrets
- [ ] Tests pass (>80% coverage)
- [ ] QA + Reviewer + Tech Lead approved
- [ ] AI prompts versioned (if applicable)
- [ ] Structured JSON logging

## Invariants

1. No code without `/plan` approval
2. No shipping without `/test` + `/review`
3. Docker cold start must work
4. AI prompts versioned (no magic strings)
5. Handlers → Services → Repositories
