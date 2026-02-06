# /plan

**Goal**: Create implementation-ready architecture and task breakdown.

**When**: After `/discovery`, before any implementation.

**Agents**: architect (design), tech_lead (approve/reject)

## Process

| Step | Owner | Do | Output |
|------|-------|----|--------|
| Architecture Design | Arch | Component boundaries, data models, API contracts, folder structure | Architecture doc |
| Task Breakdown | Arch | Sequence tasks with dependencies, assign complexity, define acceptance criteria | Task list |
| Risk Assessment | Both | Identify risks, assess complexity, propose mitigations | Risk register |
| Technical Validation | TL | Review against standards, validate separation of concerns, **approve/reject** | Approval verdict |

## Output
- Architecture document with diagrams
- Sequenced task list with acceptance criteria
- Environment variables list
- Risk register with mitigations
- Tech Lead approval

## Gates
- **Blocker**: Tech Lead rejects plan
- **Blocker**: Violates framework standards
- **Blocker**: Tasks unclear or missing acceptance criteria

## Authority
**Tech Lead** approves or rejects. Rejection requires specific feedback.

**Next**: `/implement`
