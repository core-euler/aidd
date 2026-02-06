# /review

**Goal**: Ensure code quality and standards compliance before shipping.

**When**: After `/test` passes.

**Agents**: reviewer

## Process

| Step | Owner | Do | Output |
|------|-------|----|--------|
| Architecture | Rev | Verify follows plan, check separation of concerns | Compliance assessment |
| Code Quality | Rev | Readability, complexity, error handling, logging | Quality assessment |
| Security | Rev | No secrets, input validation, SQL injection, XSS | Security assessment |
| AI Review | Rev | Prompts versioned, retry logic, fallbacks, logging | AI assessment |
| Verdict | Rev | Approve / Approve with suggestions / Request changes | Review verdict |

## Checklist (abbreviated)
- [ ] Follows approved architecture
- [ ] Handlers→services→repos separation
- [ ] No hardcoded secrets
- [ ] Structured JSON logging
- [ ] Error handling complete
- [ ] AI prompts versioned (if applicable)
- [ ] Tests pass (>80% coverage)

## Gates
- **Blocker**: Violates standards
- **Blocker**: Security vulnerabilities
- **Blocker**: Hardcoded secrets
- **Blocker**: AI prompts not versioned

When blockers found → return to `/implement`.

## Authority
**Reviewer** can block shipping. Tech Lead consulted for architectural decisions.

**Next**: `/ship`
