# /test

**Goal**: Validate implementation from user perspective.

**When**: After `/implement`, before `/review`.

**Agents**: qa

## Process

| Step | Owner | Do | Output |
|------|-------|----|--------|
| Plan | QA | Review acceptance criteria, identify test scenarios | Test plan |
| Functional | QA | Test happy path, verify acceptance criteria | Pass/fail results |
| Edge Cases | QA | Test boundaries, failures, concurrent ops | Issues found |
| Integration | QA | Test end-to-end flows, docker cold start | Integration results |
| Verdict | QA | Document issues with severity, recommend ship/no-ship | Test report |

## Severity Levels
- **Blocker**: Prevents core functionality, must fix
- **Major**: Significant impact, has workaround
- **Minor**: Cosmetic or low-impact

## Gates
- **Blocker**: Core functionality broken
- **Blocker**: Acceptance criteria not met
- **Blocker**: Docker cold start fails
- **Blocker**: Security vulnerability

When blockers found → return to `/implement`.

## Authority
**QA** can block shipping. PO may override for minor issues.

**Next**: `/review`
