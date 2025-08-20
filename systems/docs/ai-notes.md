---
name: AI Assistant Project Notes
last_updated: 2025-08-20
---

## Project Purpose
- Implement Becoming One™ method via AI-powered Telegram bot
- Build comprehensive consciousness mapping system
- Create secure, scalable knowledge management infrastructure

## Key Decisions & Versions

### Architecture
- Two Railway projects for separation of concerns:
  - brave-gratitude: User-facing Telegram bot (LOCKED)
  - heroic-enchantment: Compass Management API

### Active Components
1. User Bot (brave-gratitude)
   - Status: ✅ WORKING
   - URL: web-production-048a5.up.railway.app
   - Service ID: 9f10ba4a-b48f-4e95-9a89-c30d583e3f87

2. Compass System
   - Status: 🔄 IN DEVELOPMENT
   - Location: deployment/heroic-enchantment/
   - Components:
     - compass_api.py
     - compass_management.html

## Technical Debt & Open Questions
1. Supabase Security
   - Security Definer Views need fixing
   - RLS needs enabling on 35 tables
   - Function Search Path issues pending

## Integration Points
1. Telegram
   - Main Bot: 8244158767:AAGJveKJcOwFO_PxaeROpiQ7FKGSv-0aFrQ
   - Compass Bot: [Pending setup]

2. Databases
   - Supabase: Primary data store
   - Pinecone: Vector embeddings

## Development Standards
- Operating Principles (OPERATING_PRINCIPLES.md)
- Coding Standards (CODING_STANDARDS.md)
- Testing Protocol (TESTING_PROTOCOL.md)
- Project Awareness (PROJECT_AWARENESS.md)
- Development Practices (DEVELOPMENT_PRACTICES.md)

## Recent Changes
2025-08-20:
- Implemented clean architecture
- Added comprehensive development standards suite
- Created Cursor setup guidelines
- Established strict development practices and guardrails
