---
name: Development Practices & Guardrails
---

## Core Practices

### 1. Quote-Then-Answer Protocol
- ALWAYS extract direct quotes from @Docs or code first
- Base answers on actual evidence, not assumptions
- If no relevant quotes found, explicitly state this
- Reduces confabulation and maintains accuracy

### 2. Diff-Only Changes
- Provide changes as unified diffs only
- No prose rewrites of entire files
- Format: ```diff
  - old line
  + new line
  ```
- Smaller, focused edits for easier review
- Community best practice for clarity

### 3. Testing Discipline
- "Green tests or it didn't happen"
- Every change must:
  - Have associated tests
  - Pass existing test suite
  - Include verification steps
- Explicit evaluation and guardrails required
- No deployment without test coverage

### 4. Context Hygiene
- Keep @Docs focused and relevant
- Use .cursorignore aggressively
- Exclude:
  - Generated files
  - Build artifacts
  - Large binary files
  - Logs and temporary files
- Regular cleanup of stale documentation
- Update ai-notes.md with context changes
