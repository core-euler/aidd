# /refactor

**Goal**: Improve code quality without changing behavior.

**When**: Technical debt identified, between features (never during active development).

**Agents**: tech_lead (scope/approve), backend_dev (implement)

## Process

| Step | Owner | Do | Output |
|------|-------|----|--------|
| Scope | TL | Define goals, boundaries, what NOT to change | Refactor plan |
| Verify Tests | Dev | Ensure tests exist and pass (>80% coverage) | Test baseline |
| Refactor | Dev | Incremental changes, run tests after each | Refactored code |
| Verify Behavior | Both | Full test suite, compare before/after | No regressions |
| Review | TL | Confirm goals achieved, no scope creep | Approval |

## Patterns
- **Extract Method**: Split large functions
- **Remove Duplication**: Extract shared logic
- **Simplify Conditionals**: Early returns, flatten nesting
- **Rename**: Improve clarity

## Rules
- Make one change at a time
- Run tests after each change
- **DO NOT**: Change external behavior, add features, fix bugs (do separately)

## Gates
- **Blocker**: Tests fail (behavior changed)
- **Blocker**: Scope expanded
- **Blocker**: External APIs changed

## Authority
**Tech Lead** approves scope and validates no behavior change.
