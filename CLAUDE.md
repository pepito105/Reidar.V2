# Reidar — Project Context for Claude Code

## What This Is

Reidar is a multi-tenant AI investment associate for VC firms. It is not a
database or a dashboard. It sources startups autonomously, classifies them
against a firm's specific investment mandate, generates investment memos,
monitors pipeline companies for signals, and surfaces intelligence through
both a Command Center dashboard and ambient surfaces (Slack, calendar, Gmail,
browser extension) — without requiring the analyst to initiate anything.

The product has two active states:

- **V2** — fully deployed on Railway, live, has real users (Failup Ventures,
  Northzone). Do not break V2. Changes to V2 must be surgical and confirmed.

- **V3** — a full architectural rebuild, fresh repo under the `reidarai` GitHub
  org. V3 is what we are actively building. All new architecture, schema, and
  features are V3 work unless explicitly stated otherwise.

---

## The Three-Layer Architecture (V3)

Understanding these layers is mandatory before making any architectural decision.

### Layer 1: Global Knowledge Base
Shared infrastructure. Not the moat. Companies, founders, investors, funding
rounds, signals — sourced from free/low-cost sources:
- YC public API (api.ycombinator.com/v0.1/companies + yc-oss Algolia index)
- HN Algolia API (Show HN, Launch HN, job posts)
- ProductHunt API (free tier)
- RSS feeds: TechCrunch AI, VentureBeat, The Information, StrictlyVC,
  Axios Pro Rata, Hacker News, MIT Tech Review, Wired Business, Forbes AI,
  Fortune Term Sheet, Bloomberg Technology, Reuters Technology, WSJ Tech
- Brave Search API (on-demand enrichment)
- Harmonic API free tier (on-demand enrichment only, never bulk)
- NO Firecrawl — replaced by custom scraper stack (httpx + Playwright +
  trafilatura + BeautifulSoup)
- NO paid database subscriptions at this stage

### Layer 2: Per-Firm Intelligence (THE MOAT)
Everything proprietary to a specific fund. Scoped by firm_id.

The critical distinction: this layer does not just capture what a firm
decided. It captures how they reasoned. The most valuable knowledge in
VC is never written down — it lives in how partners think. Not just
answers, but reasoning, decisions, tradeoffs, and context. Reidar
captures that reasoning by extracting structured signals from the
artifacts that work naturally produces: meeting transcripts, pass
emails, partner objections, post-call notes, score overrides, pipeline
timing, outreach framing. Nobody fills out a form. The reasoning is
extracted passively from normal workflow.

What this layer accumulates:
- Firm mandate (thesis, stage, geography, check size, exclusions)
- Reasoning signals — structured extractions from every interaction:
  partner objections, conviction triggers, pass reasoning, threshold
  signals, open questions, behavioral signals, score deltas
- Interaction history — raw artifacts (emails, transcripts, notes)
  that feed the extraction pipeline
- Pipeline state and transition history — including time spent in each
  stage, which is itself a reasoning signal
- Score deltas — every human override of Reidar's output is a
  calibration signal logged and embedded
- Per-firm embeddings (Pool 2) — embeddings of extracted reasoning
  signals, NOT raw text

This layer is what compounds. After 12 months, a firm has a structured
record of their reasoning that exists nowhere else — not recoverable
if a partner leaves, not replicable by any competitor regardless of
data volume or model quality.

### Layer 3: Ambient Surfaces
Where value is delivered without the analyst opening a tab:
- Slack bot (event-triggered alerts, queryable associate)
- Calendar agent (pre-meeting briefs, auto-generated 30min before events)
- Gmail integration (inbound classification, sent mail logging,
  transcript ingestion from Granola/Otter/Fathom/Fireflies)
- Browser extension (live context overlay on company pages)

---

## The Two-Pool RAG Architecture

This is the most important architectural concept in V3. Never conflate the
two pools. Never mix their embeddings.

### Pool 1: Global Embeddings
- All company records from the Global Knowledge Base
- Shared across all firms — no firm_id scoping
- Provides market context: comparable companies, funding patterns,
  founder profiles, sector signals
- Uses: text-embedding-3-small via OpenAI API → pgvector (global namespace)

### Pool 2: Per-Firm Reasoning Embeddings
- Embeddings of EXTRACTED REASONING SIGNALS — not raw text
- Raw artifacts (transcripts, emails) are processed by Claude Haiku
  first to produce compact, structured reasoning signals. Those signals
  are what get embedded — not the raw 6,000-word transcript.
- Scoped strictly by firm_id — never crosses firm boundaries. Enforced
  by CHECK constraint in the database.
- Provides interpretive lens: how THIS firm reasons about companies,
  sectors, founders, and markets — retrieved at generation time
- Uses: text-embedding-3-small → pgvector (firm_id-scoped namespace)

The extraction pipeline (services/extractors/) runs Claude Haiku on
every raw interaction to produce firm_reasoning_signals records. Those
records are then embedded into firm_embeddings (Pool 2). This two-step
process — extract then embed — is what makes retrieval useful. A pool
of raw transcript embeddings returns noise. A pool of structured
reasoning signal embeddings returns precise, relevant context.

### At Query Time
Retrieve from BOTH pools, weight Pool 2 heavily, pass combined context to
Claude before generation. A memo generated with both pools is fundamentally
different from one generated with either alone.

---

## The Agentic Layer (V3)

V3 moves from cron-based scheduling to event-triggered agent dispatch.
Specific events fire specific agents without user instruction:

- Founder replies to email → refresh research brief, surface to analyst
- Portfolio/pipeline company in press → classify signal, append to timeline,
  Slack notification
- Calendar invite with founder name → generate pre-meeting brief 30min before
- New YC batch published → ingest all, score against mandate, surface top matches
- Company crosses traction threshold → re-score, escalate
- Analyst opens company in dashboard → check freshness, trigger update if stale

The scheduler.py cron pattern from V2 is replaced in V3 by an event log table
that agents consume. This is a schema-level decision — see V3 Schema section.

---

## Stack

### Backend (V2 and V3)
- Python 3.11 + FastAPI — async throughout, no blocking I/O
- SQLAlchemy async ORM — raw SQL never used
- Alembic for schema migrations
- APScheduler for background jobs (V2 only — V3 uses event-driven architecture)
- Deployed on Railway — auto-deploy on git push

### Database
- PostgreSQL via Supabase — pgvector extension for embeddings
- Multi-tenancy: every query scoped by firm_id (V3) or user_id (V2)
- Alembic for all schema changes — never modify schema directly

### AI
- Claude Sonnet (claude-sonnet-4-5) — deep research, memo generation, chat
- Claude Haiku (claude-haiku-4-5-20251001) — batch classification, email triage
  NOTE: Haiku 3 is deprecated as of April 2026. Always use Haiku 4.5.
- OpenAI text-embedding-3-small — embeddings only, both pools

### Scraping (V3 — custom stack, no Firecrawl)
- httpx — async HTTP requests
- Playwright — JS-rendered pages
- trafilatura — article text extraction
- BeautifulSoup — HTML parsing
- Base scraper class handles: rate limiting, retry, dedup, error handling

### Search & Data Sources
- Brave Search API — primary web search and company discovery
- HN Algolia API — free, no auth required
- YC public API — free, no auth required
- ProductHunt API — free tier
- Harmonic API — free tier only, on-demand enrichment, never bulk ingest

### Frontend
- V2: React + Vite, inline styles only (no Tailwind, no CSS files)
- V3: Next.js + shadcn/ui
- Auth: Clerk (useAuth, Bearer token on every API call)
- Data fetching: @tanstack/react-query
- Charts: Recharts

### Auth
- Clerk — production mode, JWT tokens
- user_id extracted from Bearer token (V2 pattern — see Multi-Tenancy below)
- V3 uses firm_id as primary tenant key

### Other
- Email: SendGrid
- Design: Syne + DM Sans + JetBrains Mono, dark editorial aesthetic
  Amber (#D97706) for action/signal, Purple (#6D28D9) for AI elements
- Figma: Remote MCP installed and authenticated

---

## Project Structure

### V2 (live — reidar-v2 repo)
```
backend/
  app/
    api/routes/        # FastAPI route files
    core/              # database, config, auth
    models/            # SQLAlchemy models
    services/          # business logic
  alembic/             # migrations
frontend/
  src/
    components/        # React components
    App.jsx
    main.jsx
```

### V3 (building — reidarai org, fresh repo)
```
backend/
  app/
    api/routes/
    core/              # db, config, auth, event_bus
    models/            # SQLAlchemy models (3-layer schema)
    services/
      scrapers/        # base scraper + source-specific scrapers
      extractors/      # Claude Haiku extraction pipeline
      embeddings/      # embedding pipeline, both pools
      agents/          # event-triggered agent runners
      rag/             # graph-aware RAG, dual-pool retrieval
    jobs/              # event consumers (replaces scheduler.py)
frontend/  # Next.js + shadcn/ui
```

---

## V3 Schema

**The full schema specification lives in `reidar_v3_schema.md`.**

Read that file before touching any model, migration, or query. It contains:
- Full table definitions with every column, type, and index
- The reasoning signal extraction concept explained with worked examples
- The two-pool RAG architecture with annotated query patterns
- The complete event type taxonomy
- Ten design rules that must never be violated

### Non-negotiable schema rules (summary — full rules in schema doc)

1. **Global tables (Layer 1) NEVER have firm_id.**
   Applies to: companies, founders, investors, funding_rounds,
   global_signals, company_embeddings.

2. **Per-firm tables (Layer 2) ALWAYS have firm_id.**
   Applies to: firms, firm_members, firm_companies, interactions,
   firm_reasoning_signals, firm_embeddings, score_deltas,
   outreach_events, investment_memos, firm_notifications,
   pipeline_stage_transitions.

3. **Pool 1 embeddings: firm_id IS NULL (CHECK constraint enforced).**
   **Pool 2 embeddings: firm_id IS NOT NULL (CHECK constraint enforced).**
   Never cross-contaminate the pools.

4. **The events table is append-only.**
   Only processed_at and processing_attempts may be updated.
   Never delete a row.

5. **firm_reasoning_signals is written by the extraction pipeline only.**
   Never by humans filling out forms. It is the output of Claude Haiku
   processing raw interactions — not a CRM notes field.

6. **Pipeline stage transitions are logged in pipeline_stage_transitions.**
   The current stage lives on firm_companies.pipeline_stage.
   The history and timing live in pipeline_stage_transitions.
   Both matter. The time spent in a stage is a reasoning signal.

7. **Alembic for all schema changes. Never modify Supabase directly.**

8. **All timestamps UTC. UUIDs as primary keys. JSONB for structured
   variable-schema data. TEXT for free-form human writing.**

### V3 pipeline stages (more granular than V2)
watching → outreach → first_call → diligence → ic_review →
term_sheet → closed → passed / invested / portfolio

### Key tables at a glance
Layer 1: companies, founders, investors, funding_rounds,
         global_signals, company_embeddings (Pool 1)

Layer 2: firms (+ decision_structure), firm_members (+ personal_thesis, focus_sectors, conviction_patterns), firm_companies,
         pipeline_stage_transitions, interactions,
         firm_reasoning_signals, score_deltas, outreach_events,
         calendar_events, slack_messages, documents,
         firm_embeddings (Pool 2), investment_memos,
         firm_notifications

Layer 3: events, agent_runs, scrape_jobs

---

## Critical Rules — Never Violate These

1. **NEVER run alembic migrations** — Remi runs manually: `alembic upgrade head`
2. **NEVER run scraping, sourcing, or classification jobs**
3. **NEVER modify .env files**
4. **NEVER install packages without asking first**
5. **NEVER run the dev server or any long-running process**
6. **NEVER touch scheduler.py without explicit instruction**
7. **NEVER modify V2 without explicit instruction** — V2 is live with real users
8. **Always read the relevant files before making changes** — never assume
   file structure or function signatures
9. **Always make surgical changes** — one file at a time
10. **Always show the plan before writing code** — wait for confirmation
11. **Always commit immediately after applying confirmed changes**
    `git add -A && git commit -m "[description]"` — never leave uncommitted work
12. **Never use overnight cron agents that modify files on disk**
13. **Lint-check after every change**

---

## Multi-Tenancy — Most Critical Runtime Pattern

### V3 pattern (firm_id)
Every query against a per-firm table must be scoped by firm_id:

```python
# WRONG
select(FirmCompany).where(FirmCompany.status == "watching")

# RIGHT
select(FirmCompany)
    .where(FirmCompany.firm_id == firm_id)
    .where(FirmCompany.status == "watching")
```

### V2 pattern (user_id — keep for all V2 work)
```python
# WRONG
select(FirmProfile).where(FirmProfile.is_active == True)

# RIGHT
select(FirmProfile)
    .where(FirmProfile.user_id == user_id)
    .where(FirmProfile.is_active == True)
    .limit(1)
result.scalars().first()  # never scalar_one_or_none() on FirmProfile
```

### V2 user_id extraction helper (already defined in most route files)
```python
def _user_id_from_request(request: Request) -> Optional[str]:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            import jwt
            decoded = jwt.decode(
                token,
                options={"verify_signature": False},
                algorithms=["RS256", "HS256"]
            )
            return decoded.get("sub")
        except Exception:
            return None
    return None
```

---

## V2 Key Services (reference — do not refactor without instruction)

- `classifier.py` — classify_startup, classify_batch, research_startup,
  detect_signals
- `sourcing_service.py` — autonomous company discovery via Brave Search
- `research_service.py` — brave_search(), firecrawl_scrape(),
  research_with_brave_and_firecrawl()
- `refresh_service.py` — nightly signal refresh for pipeline companies
- `notification_service.py` — email delivery (weekly digest, top match
  alert, diligence batch)
- `notification_writer.py` — writes to notifications table
- `job_health.py` — start_job_run, complete_job_run, fail_job_run
- `scheduler.py` — APScheduler jobs (nightly scrape 4:30AM, signal refresh
  3AM, research batch 3:30AM, sourcing 4AM, weekly summary Monday 8AM ET)

---

## V2 Database Models (reference)

- `Startup` — core company record, user_id scoped
- `FirmProfile` — VC firm config, thesis, notification prefs
- `CompanySignal` — signal events for pipeline companies
- `Notification` — unified notification table
- `AssociateMemory` — AI associate memory with pgvector embeddings
- `SchedulerRun` — job health tracking

---

## V2 Signal System (reference)

detect_signals in classifier.py uses Brave Search + Firecrawl to find signals.
Searches with freshness="pw" (past week), deduplicates against existing signals,
asks Claude to extract only grounded events with source_url. Signals only run
for pipeline companies (watching/outreach/diligence).

---

## V2 Notification System (reference)

- `company_signals` — stores actual signal events with source_url
- `notifications` — unified feed for in-app bell drawer
- NotificationDrawer.jsx reads from /api/notifications/feed
  (NOT /signals/feed — this is a known distinction)

---

## V2 Email System (reference)

Three email types via SendGrid:
1. Weekly digest (Monday 8AM ET) — Claude-generated narrative
2. Top match alert — fires per 5/5 company
3. Diligence batch — nightly, Claude interprets each signal

All emails use APP_URL env var (not localhost).
Sent to profile.notification_emails.

---

## Frontend Patterns (V2)

- No Tailwind — inline styles only
- API base URL from environment variable
- Auth via useAuth() from @clerk/clerk-react
- All API calls include Bearer token in Authorization header
- Notification polling: 60 seconds

---

## Environment Variables (backend)

Never modify .env directly. Key variables:
- `DATABASE_URL` — Supabase pooler connection string
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY` — embeddings only (text-embedding-3-small)
- `BRAVE_API_KEY`
- `FIRECRAWL_API_KEY` — V2 only, not used in V3
- `SENDGRID_API_KEY`
- `FROM_EMAIL`, `NOTIFICATION_EMAIL`
- `APP_URL` — Railway frontend URL (never localhost)
- `CLERK_SECRET_KEY`

---

## Deployment

- V2 Backend: https://radar-production-8cea.up.railway.app
- V2 Frontend: https://zestful-creativity-production.up.railway.app
- Database: Supabase (shared between local and Railway)
- Deploy: `cd ~/radar && git add -A && git commit -m "[message]" && git push`
- Railway auto-deploys on git push — never add migrations to Procfile
- Local Python: /opt/homebrew/bin/python3.11
- Local venv: ~/reidar-v2/venv

---

## How to Work

- **Prompts come from Claude.ai chat, get pasted into Claude Code** — Remi
  generates prompts in Claude.ai, reviews them, then pastes into Claude Code
- **Read before writing** — always read the relevant files before making changes
- **Plan before coding** — show the plan, wait for confirmation, then implement
- **One file at a time** — surgical changes only
- **Commit immediately** — after every confirmed change, commit before moving on
- **V2 is sacred** — live product, real users. No speculative changes.
- **V3 is greenfield** — fresh repo, schema-first, build in order
