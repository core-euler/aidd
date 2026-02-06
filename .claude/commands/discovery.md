# /discovery

**Goal**: Understand problem space before implementation.

**When**: New feature, unclear requirements, major pivot.

**Agents**: product_owner (business), architect (technical)

## Process

| Step | Owner | Do | Output |
|------|-------|----|--------|
| Problem Analysis | PO | Interview stakeholders, identify goals, define success metrics | Problem statement |
| Scope Definition | PO | Define in/out scope, priorities (MoSCoW), acceptance criteria | Scope document |
| Technical Context | Arch | Review architecture, identify dependencies, check docker compatibility | Constraints doc |
| Risk Assessment | Both | Document assumptions, identify blockers, propose mitigations | Risk register |

## Output
- Problem statement with business context
- Scope (in/out) with acceptance criteria
- Technical constraints and dependencies
- Assumptions and risk register

## Gates
- **Blocker**: Critical info missing or problem unclear
- **Pause**: External dependencies need clarification

## Authority
- **PO**: Scope and priorities
- **Architect**: Technical feasibility

**Next**: `/plan`
