# Becoming One™ — System Compass (v1)

> This is the single source of truth that keeps the bot, prompts, and team aligned. Treat it as **read-first** and **write-deliberately**. All changes should be versioned.

---

## 0) Metadata

* **Compass ID:** `compass-2025-08-v1`
* **Owner:** Johan Niklasson
* **Today's date:** 2025-08-18
* **Status:** Draft (to be signed)
* **Applies to:** Telegram Bot (entryway), Supabase memory, LLM Orchestrator, Retrieval Layer, Offer Router

---

## 1) North Star

**Purpose (one sentence):**
> To provide authentic, practical human development tools through an AI-powered system that respects and enhances genuine human connection.

**Mission (3 bullets max):**
* Create an accessible entryway to authentic personal development through modern technology
* Deliver practical methods that work, backed by structured knowledge and real experience
* Foster genuine human connections while avoiding spiritual bypassing or guru positioning

**Non‑negotiables / Red lines:**
* Never position as spiritual authority - always maintain authentic human connection
* No mystical jargon or guru-like positioning - use clear, simple language
* Protect user privacy and consent at all levels
* Maintain strict version control on all prompts and knowledge

**Primary audience(s):**
* Individuals seeking practical personal development methods
* People interested in authentic human connection without spiritual bypassing
* Users looking for structured, clear guidance without mystical overlay

**Tone & stance:**
Clear, simple language that a child could understand. Authentic human voice, never authoritative. Practical and grounded, focusing on what actually works rather than theory.

---

## 2) Core Principles (Do/Don't)

**Do:**
* Freeze scope for the current phase; changes go through change control
* Fetch from canonical memory; never invent policy
* Prefer simplicity and determinism over cleverness
* Use clear, descriptive variable names and explicit typing
* Write docstrings for all classes and functions
* Follow PEP 8 with 88-character line limit (Black formatter)
* Implement proper error handling with meaningful messages
* Use structured logging (loguru)
* Configure via environment variables

**Don't:**
* Don't ship unversioned prompts or schemas
* Don't route to new tools without explicit approval
* Don't expand scope mid-sprint
* Don't use mystical jargon or guru-like positioning
* Don't store sensitive information (API keys, tokens)
* Don't log sensitive user data
* Don't mix spiritual authority with practical guidance

---

## 3) Definitions & Glossary

* **"Canonical memory"** → structured, versioned facts in Supabase
* **"Orchestrator"** → deterministic state machine that reads from memory and returns events
* **"MVP"** → Onboarding, Routing, FAQ, Lead Capture, Offer Links, Human Escalation
* **Key Domain Terms:**
  * **Becoming One™** → The core brand and methodology for authentic human development
  * **Sacred Library** → 4,871 authentic Hylozoics quotes stored in Supabase
  * **Enhanced Bot** → The primary Telegram interface with full feature integration
  * **Facilitator** → Human guide trained in the Becoming One™ methodology

---

## 4) Scope Boundaries (This Phase)

**In scope:**
* Telegram bot with webhook integration
* Supabase for structured data and memory
* Retrieval system (Pinecone or FTS)
* LLM orchestration (GPT/Claude) behind clean interface
* Railway deployment
* Redis queue for async operations
* Structured logging

**Out of scope (deferred):**
* Payments in Telegram
* Notion/Make.com integrations
* Multi-platform router (WhatsApp/IG)
* CRM synchronization
* Complex analytics

**Exit criteria for this phase:**
* [ ] End-to-end reply within 3s p50 (queue + worker path proven)
* [ ] Retrieval top‑k results logged with doc/version
* [ ] FSM transitions observable in admin view
* [ ] Prompt registry v1 signed and immutable

---

## 5) Canonical Artifacts & Versions

* **Prompt Registry:** `orchestrator:v2025-08-15`, `routing:v2025-08-15`, `style:v2025-08-15`
* **FSM Definition:** `fsm:v1.0` (NEW → ONBOARDING → ROUTING → ANSWER → FOLLOWUP)
* **DB Schema:** `db:v1.0` (migrations applied)
* **Retrieval Index:** `kb:v2025-08-18`

---

## 6) Decision Rules & Change Control

* **Prioritization:** Safety → Correctness → Simplicity → Speed → Features
* **Change proposal format:** Context → Proposed change → Impact → Rollback → Owner → Effective date
* **Approval:** Owner signs in this Compass; version bumps required

**Open proposals:**
* None yet

---

## 7) Operating Modes

* **MVP Mode:** temp=0.2, strict routing, retrieval required for factual answers
* **Maintenance Mode:** bugfix-only; no schema/prompt changes without version bump
* **Experiment Mode:** separate namespace, never touches production artifacts

---

## 8) Orchestrator Contract (I/O)

**Input (minimum):**
* run_id, message_id, user_id
* state + state_payload
* last N messages (N ≤ 6)
* prompt_version, policy_version
* retrieval params (if any)

**Output:**
* `events[]` (type, payload)
* `assistant_message` (text + optional links)
* `new_state`

**Forbidden:** direct network side-effects; only events for the worker to handle

---

## 9) Memory Policy

**What we store:**
* Decisions, prompts, schemas
* Route outcomes
* Retrieval hits
* User consent + tags
* Audit trails for important operations

**What we never store:**
* Raw PII beyond Telegram basics
* Sensitive health data
* API keys or tokens
* Anything marked ephemeral

**Retention:**
* Raw logs: 90 days
* Canonical artifacts: forever (versioned)

**Tagging:**
* `phase:mvp`
* `domain:becoming-one`
* `offer:deep-dive`

---

## 10) Success Metrics & SLAs

* **Accuracy:** ≥ 90% acceptable answers on curated test set
* **Latency:** p50 ≤ 3s (cached), p95 ≤ 10s (with LLM)
* **Hallucination rate:** ≤ 2% on test set with retrieval enabled
* **Human escalation:** triggered on < 0.7 confidence or outside scope

---

## 11) Security & Compliance

* Secrets via environment variables only
* Audit trail for all admin actions
* Principle of least privilege for DB/storage
* Row-level security in Supabase
* Rate limiting implementation
* Input validation at all levels

---

## 12) Rollout Plan (MVP → Stable)

1. Scaffold & webhook echo
2. Queue/worker + FSM skeleton
3. Prompt registry + retrieval
4. Admin view + metrics
5. Seed knowledge base (10 docs)
6. Soft launch in private TG group

---

## 13) Parked Ideas / Later

* TON payments integration
* Multi‑platform router (WhatsApp/IG/YouTube)
* Notion/Make.com executors
* Advanced analytics & cohorts
* Complex CRM integrations

---

## 14) Sign‑off

* **Owner approval:** ☐ Johan (date: ___)
* **"Golden snapshot" created:** ☐ Yes (commit SHA: ___)


