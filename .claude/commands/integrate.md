# /integrate

**Goal**: Connect modules or components into a working system without altering their internal logic.

**When**: Multiple independently developed modules need to work together.

**Agents**: integrator (implement), tech_lead (approve)

## Process

| Step | Owner | Do | Output |
|------|-------|----|--------|
| Study interfaces | Integrator | Read public APIs and contracts of each module | Interface map |
| Integration points | Integrator | Identify where modules connect, define data flow | Integration plan |
| Implement | Integrator | Wire modules together, touch only connection points | Working integration |
| Test | Integrator | Test module interactions, verify data flows correctly | Passing integration tests |
| Verify | Integrator | Ensure each module still works independently | No regressions |

## Gates
- **Blocker**: Internal logic of existing modules changed
- **Blocker**: Existing contracts broken
- **Blocker**: Integration not tested end-to-end
- **Blocker**: Modules no longer work independently

## Authority
**Tech Lead** approves the integration approach.

**Next**: `/test`
