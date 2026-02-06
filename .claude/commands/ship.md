# /ship

**Goal**: Approve and deploy release after all gates pass.

**When**: After `/test` and `/review` pass.

**Agents**: tech_lead (approve), devops (validate/deploy)

## Process

| Step | Owner | Do | Output |
|------|-------|----|--------|
| Verify Gates | TL | Confirm test/review passed, no blockers | Gate checklist |
| Docker Validation | DevOps | Cold start, health checks, migrations, no secrets | Docker report |
| Release Notes | Both | Document changes, breaking changes, new env vars | Release notes |
| Checklist | Both | Infrastructure, code quality, security, docs | Deployment checklist |
| Approval | TL | **Approve or reject** release | Ship decision |
| Deploy | DevOps | Execute deployment, monitor startup | Confirmation |

## Ship Decision Matrix

| Condition | Action |
|-----------|--------|
| All gates passed | **SHIP** |
| Minor issues only | **SHIP** with monitoring |
| Major issues | **STAGING** only |
| Blockers found | **DO NOT SHIP** |

## Gates
- **Blocker**: Test or review not passed
- **Blocker**: Docker cold start fails
- **Blocker**: Hardcoded secrets
- **Blocker**: Missing env vars in `.env.example`

## Authority
**Tech Lead** final approval. For production, PO may also need to approve business readiness.

**Done**: Feature shipped
