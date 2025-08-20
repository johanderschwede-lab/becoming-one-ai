---
name: Task Template & Instructions
---

## Initial Setup
1. Open Cursor
2. Pin to @Docs:
   - README files
   - Architecture diagrams
   - API specifications
   - Master Prompt excerpts (optional)
   - Development standards

## Task Template
```markdown
Role: principal engineer + project manager.
Task: [INSERT_TASK_HERE]
Constraints: If uncertain, say "I don't know." Quote filenames/lines for claims. Offer 2–3 options with tradeoffs.

Deliverables (exact order):
1. Plan
2. Assumptions
3. Options
4. Risks
5. Proposed Diff
6. Tests
7. How to Verify
8. Rollback
```

## Execution Rules
1. ALWAYS read /docs/ai-notes.md before starting
2. Quote relevant documentation before making claims
3. Provide changes as diffs only
4. Update /docs/ai-notes.md after completion

## Example Usage
```markdown
Role: principal engineer + project manager.
Task: Add rate limiting to API endpoints.
Constraints: If uncertain, say "I don't know." Quote filenames/lines for claims. Offer 2–3 options with tradeoffs.

1. Plan:
   - Review current API implementation
   - Design rate limiting strategy
   - Implement chosen solution
   [...]
```
