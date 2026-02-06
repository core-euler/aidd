# /integrate_ai

**Goal**: Add AI functionality with proper versioning, error handling, and observability.

**When**: Adding LLM, RAG, or embedding features.

**Agents**: ai_engineer (implement), tech_lead (approve)

## Process

| Step | Owner | Do | Output |
|------|-------|----|--------|
| Design | AI Eng | Choose model, design prompts, plan retry/fallback, estimate costs | AI architecture |
| Prompts | AI Eng | Create versioned templates, test edge cases, optimize tokens | Versioned prompts |
| Implementation | AI Eng | Retry logic, fallbacks, structured logging, env vars for keys | Working integration |
| Observability | AI Eng | Log: version, model, tokens, cost, latency; test failure modes | Monitored service |
| Review | TL | Validate versioning, error handling, costs | Approval |

## Required Pattern
Prompts must be wrapped in a versioned structure. On error — retry with exponential backoff (3 attempts), on failure — return a fallback response. Every request must be logged with fields: version, model, tokens, cost, latency.

## Gates
- **Blocker**: Prompts not versioned
- **Blocker**: No retry/fallback logic
- **Blocker**: AI requests not logged
- **Blocker**: Costs not documented
- **Blocker**: API keys hardcoded

## Authority
**Tech Lead** approves model choices and cost implications.

**Next**: `/test`
