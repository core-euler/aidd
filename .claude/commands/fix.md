# /fix

**Goal**: Fix a bug with minimal changes, without breaking existing functionality.

**When**: A bug is found during development, testing, or production.

**Agents**: fixer (implement), reviewer (verify)

## Process

| Step | Owner | Do | Output |
|------|-------|----|--------|
| Reproduce | Fixer | Reproduce the bug reliably, document steps | Reproduction steps |
| Root cause | Fixer | Identify the root cause, trace through code | Root cause analysis |
| Propose fix | Fixer | Propose minimal fix, explain why it works | Fix proposal |
| Implement | Fixer | Apply the fix, keep changes minimal | Fixed code |
| Verify | Fixer | Run tests, confirm fix, ensure nothing else broke | Passing tests |
| Document | Fixer | Add entry to docs/issues.md with cause and solution | Updated issues.md |

## Gates
- **Blocker**: Fix changes unrelated code
- **Blocker**: Existing tests broken after fix
- **Blocker**: Root cause not documented in issues.md
- **Blocker**: Fix introduces new functionality

## Authority
**Reviewer** verifies the fix is minimal and correct.

**Next**: Update spec if the fix changes documented behavior.
