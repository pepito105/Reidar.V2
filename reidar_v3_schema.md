# Reidar V3 — Complete Database Schema Specification

**Version:** V3  
**Database:** PostgreSQL via Supabase (pgvector extension required)  
**ORM:** SQLAlchemy async  
**Migrations:** Alembic  
**Last updated:** April 2026  

---

## What This Document Is

This is the complete database schema for Reidar V3. It is written to be
readable by anyone — technical or not — who needs to understand what Reidar
stores, why it stores it, and how the pieces connect.

Every table in this schema exists for a specific reason tied to the product
vision. Understanding the vision is prerequisite to understanding the schema.

---

## The Product, In One Paragraph

Reidar is an AI investment associate for venture capital firms. It works
autonomously — sourcing startups from the open web, scoring them against a
firm's investment mandate, generating investment memos, and monitoring deals
for live signals — without requiring an analyst to ask it to. But the core
value is not the sourcing or the memos. The core value is that Reidar
captures how a specific VC firm *reasons* about investments, not just what
they decided. Every pass, every conviction note, every partner objection,
every post-call Slack message, every score override — these are reasoning
artifacts. Reidar extracts structured signals from them, embeds them, and
retrieves them at the moment of generation to produce intelligence that
reflects how this specific fund thinks. That reasoning layer compounds over
time in a way no generic tool can replicate.

---

## The Three-Layer Architecture

The schema is organized into three distinct layers. Understanding the
boundary between them is mandatory before reading any table definition.

### Layer 1: Global Knowledge Base
Shared infrastructure. Not the moat. Every company, founder, investor, and
funding round that Reidar has ever ingested from public sources. This data
is shared across all firms — no firm owns it. It provides the market
context that makes Reidar's memos grounded in reality rather than
hallucinated. Sources include the YC public API, HN Algolia, ProductHunt,
RSS feeds, Brave Search, and the Harmonic API free tier.

**Key rule:** Global tables NEVER have a firm_id column.

### Layer 2: Per-Firm Intelligence (The Moat)
Everything that belongs to a specific fund. Pipeline state, interaction
history, reasoning signals, embeddings of private context. This is what
compounds. This is what cannot be replicated. A fund that has used Reidar
for 12 months has a structured record of how they reason that exists nowhere
else in the world — not recoverable if a partner leaves, not replicable by
any competitor with better data.

**Key rule:** Per-firm tables ALWAYS have a firm_id column. Every query
against these tables must include WHERE firm_id = :firm_id. No exceptions.

### Layer 3: Event Infrastructure (The Agentic Layer)
The event log and agent execution tables that power Reidar's autonomous
behavior. Rather than running scheduled cron jobs, V3 operates on an
event stream. Every meaningful thing that happens — a founder replies to
an email, a company raises a round, a calendar invite arrives — is written
to the events table as an immutable record. Agents consume from this table
and act without being asked.

**Key rule:** The events table is append-only. Records are never updated
or deleted. processed_at is set when an agent consumes an event, but the
event record itself is never modified.

---

## The Two-Pool RAG Architecture

RAG stands for Retrieval-Augmented Generation. Before Reidar generates
any output — a memo, a score, a chat response, a pre-meeting brief —
it first retrieves relevant context from two pools of embeddings and
injects that context into the Claude prompt. The model generates WITH
that context rather than from general training alone.

### Pool 1: Global Embeddings
Embeddings of company records, founder profiles, funding round data, and
market signals from the Global Knowledge Base. Shared across all firms.
Used to provide market context: what comparable companies exist, what
funding patterns look like in a sector, what founder backgrounds are
common. These embeddings have firm_id = NULL.

### Pool 2: Per-Firm Reasoning Embeddings
Embeddings of reasoning signals extracted from a specific firm's history.
These are NOT embeddings of raw text (emails, transcripts). They are
embeddings of structured reasoning signals extracted FROM that raw text
by Claude Haiku. A meeting transcript becomes a set of structured signals:
questions asked, concerns raised, conviction triggers, partner objections.
Those signals are embedded and stored with firm_id = [firm's id].

At query time, Reidar runs retrieval against BOTH pools simultaneously,
merges the results, weights Pool 2 heavily, and passes the combined context
to Claude Sonnet before generation. The output reflects both market reality
(Pool 1) and firm-specific reasoning (Pool 2).

---

## Reasoning Signal Extraction: How Artifacts Become Embeddings

This is the most important concept in the schema to understand before
reading the table definitions.

Raw artifacts — meeting transcripts, pass emails, CRM notes, behavioral
events — are not embedded directly. They are first processed by Claude
Haiku to extract structured reasoning signals. These signals are compact,
dense, and semantically meaningful. They are what gets embedded.

**Example:**

Raw artifact (meeting transcript, ~6000 words):
> "...so I pushed back on the market size question and the founder said
> they were initially focused on mid-market legal teams but the enterprise
> pull has been stronger than expected. Maria asked about defensibility
> specifically in the context of Thomson Reuters building this natively.
> The founder's answer about the proprietary case outcome dataset was
> interesting but Maria didn't seem fully satisfied. We agreed to come
> back with a technical advisor..."

Extracted reasoning signals (stored in firm_reasoning_signals):
```json
{
  "signal_type": "partner_objection",
  "dimension": "defensibility",
  "objecting_partner": "Maria",
  "objection": "Thomson Reuters building natively",
  "founder_response": "Proprietary case outcome dataset as moat",
  "resolution": "unresolved — technical advisor review pending",
  "conviction_level": "skeptical"
}
{
  "signal_type": "market_signal",
  "dimension": "customer_segment",
  "observation": "Enterprise pull stronger than founder expected",
  "implication": "ICP may be larger than pitch suggests",
  "conviction_level": "positive_surprise"
}
{
  "signal_type": "open_question",
  "question": "Can proprietary dataset defensibility hold against Thomson Reuters?",
  "assigned_to": "technical_advisor",
  "urgency": "blocking"
}
```

Each of these signals becomes a separate embedding in Pool 2, scoped to
the firm. When Reidar later evaluates another legal tech company for the
same firm, the retrieval query finds these signals — and Claude generates
a memo that says "This fund has an open question about defensibility
against incumbents in legal tech, specifically Thomson Reuters" — without
any human having to remember or re-enter that context.

---

## Schema: Layer 1 — Global Knowledge Base

---

### `companies`

The central entity in the Global Knowledge Base. One record per company,
shared across all firms. Contains everything Reidar knows about a company
from public sources.

```sql
CREATE TABLE companies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity
    name            TEXT NOT NULL,
    slug            TEXT UNIQUE NOT NULL,  -- url-safe identifier, e.g. "acme-corp"
    website         TEXT,
    domain          TEXT,                  -- extracted from website, used for dedup
    
    -- Description
    one_liner       TEXT,                  -- single sentence description
    description     TEXT,                  -- longer description
    business_model  TEXT,                  -- B2B SaaS / marketplace / infrastructure / etc.
    target_customer TEXT,                  -- specific job title or company type
    
    -- Classification
    sector          TEXT,                  -- primary sector, e.g. "legal tech"
    subsector       TEXT,                  -- e.g. "contract management"
    tags            TEXT[],                -- array of thesis tags
    ai_nativeness   SMALLINT,              -- 1-5: 1=no AI, 5=AI is the core product
    
    -- Stage & Funding
    stage           TEXT,                  -- pre-seed / seed / series-a / series-b / growth
    total_raised_usd BIGINT,               -- total capital raised in USD
    last_round_type  TEXT,                 -- seed / series-a / etc.
    last_round_usd   BIGINT,               -- size of most recent round
    last_round_date  DATE,
    valuation_usd    BIGINT,               -- most recent known valuation
    
    -- Team
    employee_count   INTEGER,
    founding_year    INTEGER,
    headquarters     TEXT,                 -- city, country
    
    -- Source tracking
    source           TEXT NOT NULL,        -- yc / producthunt / hn / rss / brave / harmonic
    source_url       TEXT,                 -- original URL where this company was found
    source_batch     TEXT,                 -- e.g. "W25" for YC companies
    harmonic_id      TEXT,                 -- Harmonic's ID if enriched via Harmonic API
    yc_id            TEXT,                 -- YC's internal ID if applicable
    
    -- Quality
    enrichment_status TEXT DEFAULT 'raw',  -- raw / enriched / verified
    last_enriched_at  TIMESTAMPTZ,
    
    -- Timestamps
    founded_at       DATE,
    scraped_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_companies_domain ON companies(domain);
CREATE INDEX idx_companies_sector ON companies(sector);
CREATE INDEX idx_companies_stage ON companies(stage);
CREATE INDEX idx_companies_source ON companies(source);
CREATE INDEX idx_companies_created_at ON companies(created_at DESC);
CREATE UNIQUE INDEX idx_companies_slug ON companies(slug);
```

**Why this exists:** Every piece of intelligence Reidar generates about a
company starts here. This is the canonical record of what Reidar knows from
public sources. It is NOT a per-firm view — it contains no scoring,
pipeline state, or firm opinions.

---

### `founders`

Founder profiles. One record per person. Linked to companies via
company_founders join table.

```sql
CREATE TABLE founders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity
    name            TEXT NOT NULL,
    email           TEXT,
    linkedin_url    TEXT,
    twitter_url     TEXT,
    
    -- Background
    prior_companies TEXT[],   -- array of prior company names
    prior_roles     TEXT[],   -- array of prior job titles
    education       TEXT[],   -- array of schools/degrees
    domain_years    INTEGER,  -- years of domain experience
    
    -- Founder signals
    prior_exits      BOOLEAN DEFAULT FALSE,  -- has had a prior exit
    repeat_founder   BOOLEAN DEFAULT FALSE,  -- has founded before
    technical        BOOLEAN,                -- is technical co-founder
    domain_expert    BOOLEAN,                -- has direct domain expertise
    
    -- Source
    source           TEXT,
    source_url       TEXT,
    
    -- Timestamps
    scraped_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE company_founders (
    company_id  UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    founder_id  UUID NOT NULL REFERENCES founders(id) ON DELETE CASCADE,
    role        TEXT,       -- CEO / CTO / CPO / etc.
    is_primary  BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (company_id, founder_id)
);
```

**Why this exists:** Founder quality is one of the most important early-
stage investment signals. The background, domain experience, and prior
outcomes of founders are critical inputs to both the mandate scoring and
the reasoning retrieval. Keeping founders as a separate entity (not just
fields on companies) allows the same founder to be associated with
multiple companies over time.

---

### `investors`

Investor records — VCs, angels, syndicates. Used to track who else has
backed a company, providing a signal quality layer (Tier 1 backer vs.
unknown angel) and enabling network-based reasoning ("this fund co-invests
with Sequoia regularly").

```sql
CREATE TABLE investors (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          TEXT NOT NULL,
    type          TEXT,           -- vc / angel / corporate / family-office / accelerator
    tier          SMALLINT,       -- 1-3: 1=tier1 (a16z, Sequoia), 2=established, 3=emerging
    focus_stages  TEXT[],
    focus_sectors TEXT[],
    website       TEXT,
    crunchbase_url TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### `funding_rounds`

Individual funding rounds for companies. Linked to both companies and
investors via round_investors join table.

```sql
CREATE TABLE funding_rounds (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    round_type      TEXT NOT NULL,    -- pre-seed / seed / series-a / series-b / bridge
    amount_usd      BIGINT,
    valuation_usd   BIGINT,
    announced_date  DATE,
    closed_date     DATE,
    
    lead_investor   TEXT,             -- name of lead investor
    notable_investors TEXT[],         -- array of notable co-investor names
    
    source_url      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE round_investors (
    round_id    UUID NOT NULL REFERENCES funding_rounds(id) ON DELETE CASCADE,
    investor_id UUID NOT NULL REFERENCES investors(id) ON DELETE CASCADE,
    is_lead     BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (round_id, investor_id)
);

CREATE INDEX idx_funding_rounds_company ON funding_rounds(company_id);
CREATE INDEX idx_funding_rounds_date ON funding_rounds(announced_date DESC);
```

---

### `global_signals`

Public signal events about companies — funding announcements, product
launches, press coverage, hiring velocity spikes, leadership changes.
These are global (not firm-specific). The same signal can be relevant to
multiple firms.

```sql
CREATE TABLE global_signals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    signal_type     TEXT NOT NULL,
    -- Values: funding_announced / product_launched / press_coverage /
    --         hiring_spike / leadership_change / partnership_announced /
    --         revenue_milestone / customer_win / award / regulatory

    title           TEXT NOT NULL,          -- short description
    summary         TEXT,                   -- Claude-generated summary
    source_url      TEXT NOT NULL,          -- URL where signal was found
    source_name     TEXT,                   -- TechCrunch / VentureBeat / etc.
    
    signal_strength SMALLINT,               -- 1-5: how significant is this signal
    sentiment       TEXT,                   -- positive / neutral / negative
    
    published_at    TIMESTAMPTZ,            -- when the signal was published
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_global_signals_company ON global_signals(company_id);
CREATE INDEX idx_global_signals_type ON global_signals(signal_type);
CREATE INDEX idx_global_signals_detected ON global_signals(detected_at DESC);
```

---

### `company_embeddings` (Pool 1)

Vector embeddings of company records for semantic search across the
Global Knowledge Base. These embeddings power the "find companies similar
to X" and "what comparable companies exist in this space" retrieval.

firm_id is always NULL here. These are shared.

```sql
CREATE TABLE company_embeddings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    firm_id         UUID DEFAULT NULL,  -- ALWAYS NULL for Pool 1. Enforced by constraint.
    
    embedding_type  TEXT NOT NULL,
    -- Values: full_profile / one_liner / thesis_tags / founder_background
    -- Different embedding types capture different semantic dimensions.
    -- full_profile embeds the complete company description.
    -- thesis_tags embeds only the classification tags for mandate matching.
    
    content_hash    TEXT NOT NULL,      -- hash of the content that was embedded
                                        -- used to detect when re-embedding is needed
    embedding       VECTOR(1536) NOT NULL,  -- text-embedding-3-small output
    
    model_version   TEXT NOT NULL DEFAULT 'text-embedding-3-small',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT pool1_no_firm_id CHECK (firm_id IS NULL)
);

CREATE INDEX idx_company_embeddings_company ON company_embeddings(company_id);
CREATE INDEX idx_company_embeddings_type ON company_embeddings(embedding_type);
-- pgvector index for cosine similarity search
CREATE INDEX idx_company_embeddings_vector 
    ON company_embeddings USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
```

---

## Schema: Layer 2 — Per-Firm Intelligence

All tables in this layer have firm_id as a required, indexed column.
Every query against these tables must be scoped by firm_id. This is not
optional. It is the most critical runtime pattern in the system.

---

### `firms`

The core firm record. One row per VC firm using Reidar. Contains both
the identity of the firm and their investment mandate — the configuration
that everything else is filtered against.

```sql
CREATE TABLE firms (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity
    name            TEXT NOT NULL,
    slug            TEXT UNIQUE NOT NULL,
    website         TEXT,
    
    -- Auth mapping
    clerk_org_id    TEXT UNIQUE,      -- Clerk organization ID
    owner_user_id   TEXT NOT NULL,    -- Clerk user ID of the GP/admin who set up the account
    
    -- Investment Mandate
    -- This is the core configuration. Everything Reidar does is filtered
    -- through this mandate. It is stored both as structured fields and as
    -- free-text thesis for Claude to reason against.
    
    thesis_text     TEXT,
    -- Free-text investment thesis in the firm's own words.
    -- Example: "We invest in AI-native B2B SaaS companies automating
    -- knowledge work in regulated verticals at pre-seed and seed stage."
    -- This gets injected verbatim into Claude prompts.
    
    focus_stages    TEXT[] NOT NULL DEFAULT '{}',
    -- Array of stages: pre-seed / seed / series-a / series-b
    
    focus_sectors   TEXT[] NOT NULL DEFAULT '{}',
    -- Array of sector strings. Free-text, not constrained.
    -- Example: ["legal tech", "fintech", "healthcare AI", "dev tools"]
    
    focus_geographies TEXT[] NOT NULL DEFAULT '{}',
    -- Array of geographic focuses.
    -- Example: ["North America", "Europe", "Global"]
    
    check_size_min_usd  BIGINT,      -- minimum check size in USD
    check_size_max_usd  BIGINT,      -- maximum check size in USD
    
    excluded_sectors TEXT[] NOT NULL DEFAULT '{}',
    -- Sectors to explicitly never surface. Hard filter.
    -- Example: ["crypto", "gambling", "defense"]
    
    excluded_business_models TEXT[] NOT NULL DEFAULT '{}',
    -- Business models to exclude.
    -- Example: ["services", "agency", "consulting"]
    
    ai_nativeness_min SMALLINT DEFAULT 1,
    -- Minimum AI nativeness score (1-5) to surface a company.
    -- A fund that only wants AI-native companies sets this to 4 or 5.
    
    coverage_threshold SMALLINT DEFAULT 3,
    -- Minimum mandate fit score (1-5) for a company to appear in Coverage.
    -- Companies below this threshold are suppressed from the feed.
    
    -- Firm context for reasoning
    portfolio_companies TEXT[],
    -- Array of portfolio company names.
    -- Used for conflict detection and comparable reasoning.
    -- "Does this company compete with something we already own?"
    
    notable_investments TEXT[],
    -- Past investments the firm is proud of / wants Claude to reference.
    -- Used to calibrate Reidar's understanding of the firm's taste.
    
    typical_pass_reasons TEXT[],
    -- The fund's most common pass reasons in their own words.
    -- Seeded on onboarding, refined over time by Reidar's extraction.
    -- Example: ["market too small", "team missing technical co-founder",
    --           "too early for enterprise sales"]
    
    -- Notification preferences
    notification_emails TEXT[] NOT NULL DEFAULT '{}',
    weekly_digest_enabled BOOLEAN DEFAULT TRUE,
    top_match_alerts_enabled BOOLEAN DEFAULT TRUE,
    signal_alerts_enabled BOOLEAN DEFAULT TRUE,
    
    -- Slack integration
    slack_workspace_id  TEXT,
    slack_bot_token     TEXT,
    slack_channel_id    TEXT,   -- primary channel for Reidar alerts
    
    -- Status
    is_active           BOOLEAN DEFAULT TRUE,
    onboarded_at        TIMESTAMPTZ,
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_firms_clerk_org ON firms(clerk_org_id);
CREATE INDEX idx_firms_owner ON firms(owner_user_id);
```

**Why this exists:** The firm profile is the foundation of everything
Reidar does. Without it, Reidar is a generic research tool. With it,
every output is mandate-specific. The thesis_text, focus_stages, and
excluded_sectors fields get injected into every Claude prompt.

---

### `firm_members`

People at the firm who have access to Reidar. A firm has one owner (the
GP or partner who set up the account) and potentially multiple members
(analysts, associates, other partners). Each member's individual behavior
is tracked separately because different people at the same firm reason
differently — a partner's objections carry more weight than an analyst's.

```sql
CREATE TABLE firm_members (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id     UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    
    clerk_user_id   TEXT NOT NULL UNIQUE,  -- Clerk user ID
    name            TEXT NOT NULL,
    email           TEXT NOT NULL,
    role            TEXT NOT NULL,         -- gp / partner / principal / associate / analyst
    
    -- Gmail integration (per-member, not per-firm)
    gmail_connected     BOOLEAN DEFAULT FALSE,
    gmail_access_token  TEXT,              -- encrypted
    gmail_refresh_token TEXT,              -- encrypted
    gmail_token_expiry  TIMESTAMPTZ,
    gmail_last_synced   TIMESTAMPTZ,
    gmail_email         TEXT,              -- connected Gmail address
    
    -- Calendar integration
    calendar_connected  BOOLEAN DEFAULT FALSE,
    calendar_access_token  TEXT,           -- encrypted
    calendar_refresh_token TEXT,           -- encrypted
    
    is_active   BOOLEAN DEFAULT TRUE,
    joined_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_firm_members_firm ON firm_members(firm_id);
CREATE INDEX idx_firm_members_clerk ON firm_members(clerk_user_id);
```

---

### `firm_companies`

The relationship between a firm and a company. This is where the firm's
view of a company lives — their fit score, pipeline stage, notes,
and the history of how the relationship has evolved.

One row per (firm, company) pair. Created when a firm first sees a company
in Coverage or adds it manually.

```sql
CREATE TABLE firm_companies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Pipeline state
    pipeline_stage  TEXT NOT NULL DEFAULT 'watching',
    -- Values: watching / outreach / first_call / diligence / ic_review /
    --         term_sheet / closed / passed / invested / portfolio
    -- Note: more granular than V2's 5 stages. Reasoning lives in transitions.
    
    pipeline_entered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- When this company entered the pipeline (first added to any stage)
    
    -- Mandate scoring
    fit_score           SMALLINT,       -- 1-5: Reidar's mandate fit score
    fit_score_rationale TEXT,           -- Claude's explanation of the score
    ai_nativeness_score SMALLINT,       -- 1-5: how AI-native is this company
    
    -- Analyst override
    analyst_fit_score   SMALLINT,       -- if analyst disagreed with Reidar's score
    analyst_override_reason TEXT,       -- why they overrode (reasoning signal)
    overridden_by       UUID REFERENCES firm_members(id),
    overridden_at       TIMESTAMPTZ,
    
    -- Pass tracking
    passed_at           TIMESTAMPTZ,
    pass_category       TEXT,
    -- Values: team / market_size / timing / competition / stage / terms /
    --         portfolio_conflict / thesis_fit / traction / technology
    
    pass_reason_official TEXT,
    -- What the fund told the founder (or logged officially)
    
    pass_reason_internal TEXT,
    -- What the fund actually thought (not shared with founder)
    -- The gap between these two is a reasoning signal.
    
    pass_what_would_change TEXT,
    -- "What would need to be true for us to revisit this?"
    -- Extremely valuable for the second encounter pattern.
    
    -- Conviction tracking
    conviction_level    TEXT,
    -- Values: exploring / interested / excited / high_conviction / champion
    -- Tracks where the deal stands emotionally, not just procedurally.
    
    champion_member_id  UUID REFERENCES firm_members(id),
    -- Who at the firm is the internal champion driving this deal forward?
    -- Deals with no champion rarely close.
    
    -- Notes (unstructured, human-written)
    notes               TEXT,
    internal_memo       TEXT,   -- running internal memo, updated over time
    
    -- Outreach tracking
    first_outreach_at   TIMESTAMPTZ,
    last_outreach_at    TIMESTAMPTZ,
    outreach_method     TEXT,   -- cold_email / warm_intro / conference / inbound
    intro_path          TEXT,   -- who made the introduction if warm
    
    -- Second encounter support
    previously_seen     BOOLEAN DEFAULT FALSE,
    previous_pass_id    UUID REFERENCES firm_companies(id),
    -- Self-reference to earlier firm_company record.
    -- If a company comes back around, we link to the prior evaluation.
    -- This is how Reidar surfaces "you saw this company before, here's
    -- how you thought about it then, here's what has changed."
    
    -- Research state
    last_researched_at  TIMESTAMPTZ,
    research_status     TEXT DEFAULT 'pending',
    -- Values: pending / in_progress / complete / stale
    -- stale = research is more than 30 days old
    
    -- Metadata
    added_by            UUID REFERENCES firm_members(id),
    added_source        TEXT,
    -- Values: coverage / manual / email_inbound / import / research_agent
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(firm_id, company_id)
);

CREATE INDEX idx_firm_companies_firm ON firm_companies(firm_id);
CREATE INDEX idx_firm_companies_company ON firm_companies(company_id);
CREATE INDEX idx_firm_companies_stage ON firm_companies(firm_id, pipeline_stage);
CREATE INDEX idx_firm_companies_fit ON firm_companies(firm_id, fit_score DESC);
```

**Why this exists:** This is the core per-firm entity. It holds the firm's
view of a company — not facts about the company (those live in `companies`)
but opinions, decisions, and state. The pass_reason_official vs.
pass_reason_internal gap is a reasoning signal. The analyst_override fields
are reasoning signals. The conviction_level and champion fields capture
the behavioral dimensions of deal progression that a pipeline stage alone
cannot represent.

---

### `pipeline_stage_transitions`

An immutable log of every time a company moves between pipeline stages.
The pipeline_stage field on firm_companies tells you where a company is
NOW. This table tells you the full history of how it got there — and the
timing and reasoning at each transition.

This is a reasoning artifact. A company that sat in first_call for 6 weeks
before passing tells a different story than one that passed the same day.

```sql
CREATE TABLE pipeline_stage_transitions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    firm_company_id UUID NOT NULL REFERENCES firm_companies(id) ON DELETE CASCADE,
    
    from_stage      TEXT,           -- NULL if this is the first stage (entry)
    to_stage        TEXT NOT NULL,
    
    transitioned_by UUID REFERENCES firm_members(id),  -- NULL if system-triggered
    transition_type TEXT NOT NULL,
    -- Values: manual / agent_triggered / email_reply / calendar_event /
    --         signal_triggered / timeout

    reason          TEXT,           -- why did this transition happen?
    notes           TEXT,           -- any notes at the time of transition
    
    -- Timing signal
    days_in_prior_stage INTEGER,
    -- Computed: how many days was the company in from_stage before this transition?
    -- A deal that sat in diligence for 90 days and then passed is different
    -- from one that passed after 5 days. The duration is a reasoning signal.
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_transitions_firm ON pipeline_stage_transitions(firm_id);
CREATE INDEX idx_transitions_firm_company ON pipeline_stage_transitions(firm_company_id);
CREATE INDEX idx_transitions_created ON pipeline_stage_transitions(created_at DESC);
```

---

### `interactions`

Every meaningful interaction between the firm and a company — emails,
calls, meetings, demos, reference checks, founder events. This is the
raw artifact store from which reasoning signals are extracted.

Each interaction record stores the raw artifact AND the extracted
reasoning signals (stored separately in firm_reasoning_signals).

```sql
CREATE TABLE interactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    firm_company_id UUID NOT NULL REFERENCES firm_companies(id) ON DELETE CASCADE,
    member_id       UUID REFERENCES firm_members(id),
    -- Which member had this interaction? NULL if system-generated.
    
    interaction_type TEXT NOT NULL,
    -- Values: email_inbound / email_outbound / call / meeting / demo /
    --         reference_check / conference_meeting / lp_intro /
    --         document_received / transcript_ingested / note_added /
    --         co_investor_call / technical_review / customer_call
    
    -- Raw artifact
    raw_content     TEXT,
    -- The full text of the interaction. Email body, transcript text,
    -- meeting notes, etc. This is the source material for extraction.
    
    subject         TEXT,           -- email subject or meeting title
    participants    JSONB,
    -- Structured array of participant objects, not raw strings.
    -- TEXT[] loses name/role/affiliation — JSONB preserves it.
    -- Example:
    -- [{ "name": "Maria Chen", "email": "maria@benchmark.com",
    --    "role": "Partner", "affiliation": "Benchmark", "type": "investor" },
    --   { "name": "Alex Wu", "email": "alex@acme.com",
    --    "role": "CEO", "affiliation": "Acme Corp", "type": "founder" }]
    direction       TEXT,           -- inbound / outbound / internal
    
    -- Parsed metadata
    occurred_at     TIMESTAMPTZ NOT NULL,   -- when did this actually happen
    duration_minutes INTEGER,               -- for calls and meetings
    
    -- Source tracking
    source          TEXT NOT NULL,
    -- Values: gmail_sync / calendar_sync / manual / transcript_upload /
    --         granola / otter / fathom / fireflies
    
    gmail_message_id    TEXT,       -- if sourced from Gmail
    calendar_event_id   TEXT,       -- if sourced from calendar
    transcript_url      TEXT,       -- if an external notetaker transcript
    
    -- Extraction state
    extraction_status TEXT DEFAULT 'pending',
    -- Values: pending / processing / complete / failed
    -- Claude Haiku processes raw_content to extract reasoning signals.
    -- This field tracks whether that extraction has happened.
    
    extracted_at    TIMESTAMPTZ,
    
    -- Sentiment (extracted by Claude Haiku)
    overall_sentiment TEXT,         -- positive / neutral / negative / mixed
    conviction_delta  TEXT,         -- increased / decreased / unchanged / unclear
    -- Did this interaction increase or decrease internal conviction?
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_interactions_firm ON interactions(firm_id);
CREATE INDEX idx_interactions_firm_company ON interactions(firm_company_id);
CREATE INDEX idx_interactions_type ON interactions(firm_id, interaction_type);
CREATE INDEX idx_interactions_occurred ON interactions(occurred_at DESC);
CREATE INDEX idx_interactions_extraction ON interactions(extraction_status) 
    WHERE extraction_status = 'pending';
```

---

### `firm_reasoning_signals`

The most important table in Layer 2. This is where extracted reasoning
lives. Every interaction is processed by Claude Haiku to produce structured
signals — these signals are what get embedded into Pool 2 and retrieved
at generation time.

This table is NOT written by humans. It is written by the extraction
pipeline after processing raw interactions.

```sql
CREATE TABLE firm_reasoning_signals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    
    -- Source linkage
    interaction_id      UUID REFERENCES interactions(id) ON DELETE SET NULL,
    firm_company_id     UUID REFERENCES firm_companies(id) ON DELETE CASCADE,
    -- A signal may relate to a specific company, or to the firm generally
    -- (e.g., a thesis signal that emerged from a pattern across many deals).
    
    -- Signal classification
    signal_type     TEXT NOT NULL,
    -- Values:
    -- partner_objection     — a specific concern raised by a partner
    -- conviction_trigger    — what caused conviction to increase
    -- pass_reasoning        — structured decomposition of a pass decision
    -- threshold_signal      — a specific metric/milestone that matters to this fund
    -- founder_signal        — an observation about a founder's qualities
    -- market_signal         — an observation about market dynamics
    -- open_question         — an unresolved question blocking a decision
    -- thesis_refinement     — new information that updates the firm's thesis
    -- comparable_reference  — "this is like X, which we've seen before"
    -- champion_signal       — evidence of internal championing behavior
    -- red_flag              — something that triggered concern
    -- behavioral_signal     — inferred from behavior, not stated explicitly
    --                         e.g., "responded in 3 hours" = high conviction
    -- second_encounter       — company previously evaluated, prior reasoning surfaced
    --                         e.g., "passed 8 months ago citing market size;
    --                         now at $800K ARR — original concern partially addressed"
    -- intro_path             — who introduced whom, relationship graph signal
    --                         e.g., "intro via portfolio founder at Acme —
    --                         second deal sourced through this network node"
    -- calendar_pattern       — meeting recurrence, escalation, cancellation signals
    --                         e.g., "third founder meeting in 10 days — escalating
    --                         conviction; GP added to most recent invite"
    -- network_signal         — co-investor patterns, LP introductions, conference
    --                         connections — who the firm interacts with around a deal
    -- velocity_signal        — speed of pipeline movement and response latency
    --                         e.g., "moved from first_call to diligence in 3 days —
    --                         fastest stage transition for any deal this quarter"
    
    -- Entity scope
    entity_type     TEXT,
    -- What does this signal relate to?
    -- Values: company / founder / sector / stage / fund_thesis / partner
    
    entity_id       UUID,
    -- The UUID of the related entity (company, founder, etc.)
    -- NULL if the signal is about the firm's thesis generally.
    
    -- Signal content (structured, extracted by Claude Haiku)
    structured_data JSONB NOT NULL DEFAULT '{}',
    -- The structured extraction. Schema varies by signal_type.
    -- 
    -- For partner_objection:
    -- { "partner": "Maria", "dimension": "defensibility",
    --   "objection": "Thomson Reuters building natively",
    --   "founder_response": "Proprietary dataset moat",
    --   "resolution": "unresolved", "conviction_impact": "negative" }
    --
    -- For pass_reasoning:
    -- { "official_reason": "not the right time",
    --   "inferred_real_reason": "founder didn't build trust",
    --   "thesis_dimension_failed": "team",
    --   "what_would_change": "see execution traction at $1M ARR",
    --   "confidence": "high" }
    --
    -- For threshold_signal:
    -- { "metric": "ARR", "threshold": 500000,
    --   "context": "would revisit at $500K ARR",
    --   "stage": "seed", "sector": "legal tech" }
    --
    -- For behavioral_signal:
    -- { "behavior": "responded_to_email_in_3_hours",
    --   "inferred_conviction": "high",
    --   "baseline": "typically responds in 2 days",
    --   "inference_confidence": "medium" }
    
    -- Text for embedding
    signal_text     TEXT NOT NULL,
    -- A human-readable summary of this signal, written by Claude Haiku.
    -- This is what gets embedded. It is compact, dense, and semantically
    -- meaningful — not the raw transcript or email.
    -- Example: "Partner Maria raised unresolved defensibility concern about
    -- Thomson Reuters building natively in legal AI space for Acme Corp.
    -- Founder's dataset moat argument was not fully convincing. Technical
    -- advisor review assigned as blocking open question."
    
    -- Quality
    confidence      TEXT DEFAULT 'medium',  -- high / medium / low
    -- How confident is the extraction in this signal?
    
    extraction_model TEXT DEFAULT 'claude-haiku-4-5-20251001',
    -- Which model extracted this signal?
    
    -- Temporal context
    signal_date     TIMESTAMPTZ,
    -- When did the underlying event happen? (may differ from created_at
    -- if we're processing a historical transcript)
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_reasoning_signals_firm ON firm_reasoning_signals(firm_id);
CREATE INDEX idx_reasoning_signals_type ON firm_reasoning_signals(firm_id, signal_type);
CREATE INDEX idx_reasoning_signals_entity ON firm_reasoning_signals(entity_id);
CREATE INDEX idx_reasoning_signals_company ON firm_reasoning_signals(firm_company_id);
```

---

### `score_deltas`

Every time a human overrides Reidar's generated output — a fit score, a
recommended next step, a memo section — that delta is logged here. This
is a behavioral reasoning signal: it tells Reidar where its model of the
firm diverges from the firm's actual thinking.

```sql
CREATE TABLE score_deltas (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    firm_company_id UUID NOT NULL REFERENCES firm_companies(id) ON DELETE CASCADE,
    member_id       UUID REFERENCES firm_members(id),
    
    delta_type      TEXT NOT NULL,
    -- Values: fit_score / ai_nativeness / pipeline_stage / next_step_recommendation /
    --         memo_team_section / memo_market_section / memo_competitive_section /
    --         memo_conclusion / memo_bull_case / memo_risks
    
    reidar_value    TEXT NOT NULL,   -- what Reidar suggested
    human_value     TEXT NOT NULL,   -- what the human set it to
    
    delta_direction TEXT,            -- higher / lower / different
    -- For numeric fields (scores): was the human value higher or lower?
    -- For text fields: just 'different'
    
    reason          TEXT,
    -- Did the human explain why they overrode? Rarely provided explicitly,
    -- but captured when it is. This is the highest-quality reasoning signal
    -- when present.
    
    context_at_time JSONB,
    -- Snapshot of relevant context when the override happened.
    -- e.g., what stage was the company in, what was the fit score before
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_score_deltas_firm ON score_deltas(firm_id);
CREATE INDEX idx_score_deltas_type ON score_deltas(firm_id, delta_type);
```

**Why this exists:** Score deltas are where Reidar learns calibration
errors. If the firm consistently scores lower than Reidar on market size
for B2B SaaS companies, Reidar's mandate model is miscalibrated. If they
consistently score higher on specific founder profiles, that's a thesis
refinement signal. This table is the feedback loop.

---

### `outreach_events`

Detailed tracking of every outreach attempt — the method, the message
framing, the intro path, and the response. This captures the reasoning
signals embedded in HOW a firm reaches out, not just THAT they reached out.

```sql
CREATE TABLE outreach_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    firm_company_id UUID NOT NULL REFERENCES firm_companies(id) ON DELETE CASCADE,
    member_id       UUID REFERENCES firm_members(id),
    
    -- Outreach details
    outreach_type   TEXT NOT NULL,
    -- Values: cold_email / warm_intro_request / warm_intro_sent /
    --         linkedin_dm / conference_followup / inbound_response /
    --         re_engagement  (reaching back out to a previously passed company)
    
    -- Intro path (if warm)
    intro_via       TEXT,           -- name of person who made the intro
    intro_relationship TEXT,        -- portfolio_founder / lp / co_investor /
                                    -- advisor / personal / conference
    
    -- Message analysis
    thesis_framing  TEXT,
    -- What thesis angle did the outreach lead with?
    -- Extracted from the email by Claude Haiku.
    -- "AI-native GTM automation for enterprise" vs
    -- "founder with relevant prior exit in the space" —
    -- these reveal what the fund found most compelling.
    
    first_question  TEXT,
    -- The first question asked of the founder, if any.
    -- Reveals the fund's primary diligence concern at first contact.
    
    -- Response tracking
    founder_responded   BOOLEAN DEFAULT FALSE,
    response_hours      INTEGER,
    -- Hours from outreach to founder response.
    -- Response latency is a signal about the founder's fundraising
    -- posture and interest level.
    
    founder_response_tone TEXT,     -- eager / professional / lukewarm / no_response
    
    -- Outcome
    resulted_in_call BOOLEAN DEFAULT FALSE,
    
    sent_at         TIMESTAMPTZ NOT NULL,
    responded_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_outreach_firm ON outreach_events(firm_id);
CREATE INDEX idx_outreach_firm_company ON outreach_events(firm_company_id);
```


### `calendar_events`

Raw calendar events received from the calendar integration. This is a
staging table — events arrive here before Reidar has matched them to a
company. A background agent processes each record, attempts company
matching, and creates a linked `interactions` record when a match is
found. Without this staging table, calendar events that arrive before
Reidar knows which company is involved would be lost.

Recurrence patterns (RRULE) are stored here because they are critical
for detecting meeting escalation signals — a founder meeting that recurs
weekly within 10 days signals a different conviction level than a
one-time call.

```sql
CREATE TABLE calendar_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    member_id       UUID NOT NULL REFERENCES firm_members(id) ON DELETE CASCADE,

    -- Raw calendar data
    calendar_event_id   TEXT NOT NULL,  -- external calendar provider ID
    title               TEXT,           -- event title (may contain founder/company name)
    description         TEXT,           -- event body/notes
    location            TEXT,

    -- Timing
    started_at          TIMESTAMPTZ NOT NULL,
    ended_at            TIMESTAMPTZ,
    duration_minutes    INTEGER,

    -- Attendees (structured — same JSONB pattern as interactions.participants)
    attendees           JSONB,
    -- [{ "name": "...", "email": "...", "role": "...", "affiliation": "..." }]

    -- Recurrence
    is_recurring        BOOLEAN DEFAULT FALSE,
    recurrence_rule     TEXT,           -- RRULE string, e.g. "FREQ=WEEKLY;COUNT=4"
    recurrence_parent_id UUID REFERENCES calendar_events(id),
    -- Links recurring instances back to the original event.
    -- Recurrence patterns are reasoning signals:
    -- weekly founder meetings = escalating conviction.

    -- Company matching state
    matching_status     TEXT DEFAULT 'pending',
    -- Values: pending / matched / no_match / ambiguous
    matched_company_id  UUID REFERENCES companies(id),
    matched_firm_company_id UUID REFERENCES firm_companies(id),
    match_confidence    TEXT,           -- high / medium / low

    -- Downstream linkage
    interaction_id      UUID REFERENCES interactions(id),
    -- Set after a matched calendar event creates an interactions record.

    -- Source
    source              TEXT NOT NULL DEFAULT 'google_calendar',
    raw_payload         JSONB,          -- full raw event from calendar API

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_calendar_events_firm ON calendar_events(firm_id);
CREATE INDEX idx_calendar_events_member ON calendar_events(member_id);
CREATE INDEX idx_calendar_events_started ON calendar_events(started_at DESC);
CREATE INDEX idx_calendar_events_matching ON calendar_events(matching_status)
    WHERE matching_status = 'pending';
CREATE INDEX idx_calendar_events_company ON calendar_events(matched_company_id)
    WHERE matched_company_id IS NOT NULL;
```

**Why this exists:** The `interactions` table requires a `firm_company_id`
at creation time. Calendar events arrive before Reidar knows which company
a meeting is about. This staging table receives all calendar events,
runs company matching asynchronously, and creates the linked interaction
record only when a match is confirmed. It also preserves recurrence data
which is a distinct reasoning signal not available on the interaction record.

---

### `slack_messages`

Slack messages from connected workspaces that are relevant to deal flow.
This is the highest-fidelity unfiltered reasoning signal in the system —
partners and analysts say what they actually think in Slack before they
have had time to rationalize it. A post-call Slack message written in
the 10 minutes after hanging up is more honest than anything that goes
into a formal CRM note.

This table only stores deal-relevant messages — not every message in
every channel. The Slack integration uses keyword matching, channel
scoping, and entity detection to identify deal-related messages before
storing them here.

```sql
CREATE TABLE slack_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    member_id       UUID REFERENCES firm_members(id),
    -- Which firm member sent or received this message?

    -- Slack metadata
    slack_message_id    TEXT NOT NULL UNIQUE,   -- Slack message ts identifier
    slack_channel_id    TEXT NOT NULL,
    slack_channel_name  TEXT,
    slack_thread_ts     TEXT,           -- NULL if not a thread reply
    slack_user_id       TEXT,           -- Slack user ID of the sender

    -- Content
    raw_content         TEXT NOT NULL,  -- raw message text
    message_type        TEXT NOT NULL,
    -- Values: post_call_reaction / deal_commentary / partner_discussion /
    --         intro_request / signal_share / pass_discussion /
    --         conviction_signal / question / general

    -- Company linkage (may be NULL if not yet matched)
    firm_company_id     UUID REFERENCES firm_companies(id),
    company_id          UUID REFERENCES companies(id),

    -- Timing
    sent_at             TIMESTAMPTZ NOT NULL,

    -- Extraction state
    extraction_status   TEXT DEFAULT 'pending',
    -- Values: pending / processing / complete / failed
    extracted_at        TIMESTAMPTZ,

    -- Extracted signals (high-level, before full extraction pipeline)
    detected_sentiment  TEXT,           -- positive / negative / neutral / mixed
    detected_conviction TEXT,           -- increasing / decreasing / unchanged
    mentions_company    BOOLEAN DEFAULT FALSE,
    mentions_founder    BOOLEAN DEFAULT FALSE,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_slack_messages_firm ON slack_messages(firm_id);
CREATE INDEX idx_slack_messages_company ON slack_messages(firm_company_id)
    WHERE firm_company_id IS NOT NULL;
CREATE INDEX idx_slack_messages_sent ON slack_messages(sent_at DESC);
CREATE INDEX idx_slack_messages_extraction ON slack_messages(extraction_status)
    WHERE extraction_status = 'pending';
CREATE INDEX idx_slack_messages_type ON slack_messages(firm_id, message_type);
```

**Why this exists:** The `interactions` table is designed for structured
interactions between the firm and a founder. Slack messages are internal
— between members of the same firm — and require different extraction
logic. The reasoning signals embedded in internal deal commentary are
among the most valuable in the system: they capture what partners actually
think before they have formalized their position.

---

### `documents`

Documents received or referenced during the deal flow — pitch decks,
one-pagers, financial models, technical due diligence reports. A document
is a distinct entity with its own lifecycle: received, opened, forwarded,
re-requested. This lifecycle is itself a reasoning signal. The email that
delivered a pitch deck is captured in `interactions`, but subsequent
engagements with the same document cannot be linked without a document
entity.

```sql
CREATE TABLE documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    firm_company_id UUID REFERENCES firm_companies(id),
    -- NULL if document arrived before company was matched.

    -- Document identity
    document_type   TEXT NOT NULL,
    -- Values: pitch_deck / one_pager / financial_model / cap_table /
    --         technical_dd / reference_doc / term_sheet / loi /
    --         portfolio_update / market_map / other

    title           TEXT,
    file_name       TEXT,
    file_size_bytes INTEGER,
    mime_type       TEXT,

    -- Source
    source          TEXT NOT NULL,
    -- Values: email_attachment / shared_link / uploaded / slack_share
    source_interaction_id UUID REFERENCES interactions(id),
    -- The interaction record that delivered this document (email case).

    source_slack_message_id UUID REFERENCES slack_messages(id),
    -- The slack_messages record that delivered this document (slack_share case).
    -- Exactly one of source_interaction_id or source_slack_message_id should
    -- be set depending on the value of source. Both may be NULL for
    -- manually uploaded documents.

    -- Storage
    storage_url     TEXT,           -- internal storage reference if saved
    content_hash    TEXT,           -- for deduplication across re-sends

    -- Engagement tracking
    first_opened_at     TIMESTAMPTZ,
    last_opened_at      TIMESTAMPTZ,
    open_count          INTEGER DEFAULT 0,
    forwarded_to        JSONB,
    -- Array of people this document was forwarded to:
    -- [{ "name": "...", "email": "...", "forwarded_at": "..." }]
    -- Forwarding behavior is a conviction and network signal.

    re_requested        BOOLEAN DEFAULT FALSE,
    -- Did the firm ask the founder to resend or update this document?
    -- Re-requesting a deck or model is a high-conviction signal.

    -- Extraction state
    extraction_status   TEXT DEFAULT 'pending',
    -- Values: pending / processing / complete / failed / skipped
    -- Claude Haiku can extract key data points from pitch decks.
    extracted_at        TIMESTAMPTZ,
    extracted_data      JSONB,
    -- Structured extraction from the document content.
    -- For pitch_deck: { "problem": "...", "solution": "...",
    --   "market_size": "...", "traction": "...", "ask": "..." }

    received_at         TIMESTAMPTZ NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_documents_firm ON documents(firm_id);
CREATE INDEX idx_documents_firm_company ON documents(firm_company_id)
    WHERE firm_company_id IS NOT NULL;
CREATE INDEX idx_documents_type ON documents(firm_id, document_type);
CREATE INDEX idx_documents_extraction ON documents(extraction_status)
    WHERE extraction_status = 'pending';
CREATE INDEX idx_documents_received ON documents(received_at DESC);
```

**Why this exists:** A pitch deck is not just an email attachment — it is
a document with its own engagement lifecycle. How many times was it opened?
Was it forwarded internally? Was a newer version requested? These engagement
patterns are reasoning signals that cannot be captured on the email record
alone. The `documents` table gives documents first-class entity status so
their full lifecycle can be tracked and extracted.

---

---

### `firm_embeddings` (Pool 2)

Vector embeddings of reasoning signals from the per-firm intelligence
layer. This is the core retrieval index for the firm's reasoning history.

Every record in firm_reasoning_signals gets an embedding here.
firm_id is ALWAYS set. These never cross firm boundaries.

```sql
CREATE TABLE firm_embeddings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    
    -- Source linkage
    source_type     TEXT NOT NULL,
    -- Values: reasoning_signal / interaction_summary / thesis_statement /
    --         pass_pattern / conviction_pattern / memo_section
    
    source_id       UUID NOT NULL,
    -- UUID of the source record (firm_reasoning_signals.id, interactions.id, etc.)
    
    -- Scope for retrieval filtering
    related_company_id  UUID REFERENCES companies(id),
    related_sector      TEXT,
    related_stage       TEXT,
    signal_type         TEXT,    -- mirrors firm_reasoning_signals.signal_type
    
    -- The embedded content
    content_text    TEXT NOT NULL,
    -- The text that was embedded. For reasoning signals, this is
    -- firm_reasoning_signals.signal_text.
    
    content_hash    TEXT NOT NULL,  -- for detecting stale embeddings
    
    embedding       VECTOR(1536) NOT NULL,
    model_version   TEXT NOT NULL DEFAULT 'text-embedding-3-small',
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT pool2_requires_firm_id CHECK (firm_id IS NOT NULL)
);

CREATE INDEX idx_firm_embeddings_firm ON firm_embeddings(firm_id);
CREATE INDEX idx_firm_embeddings_source ON firm_embeddings(firm_id, source_type);
CREATE INDEX idx_firm_embeddings_company ON firm_embeddings(related_company_id);
CREATE INDEX idx_firm_embeddings_sector ON firm_embeddings(firm_id, related_sector);
-- pgvector index — scoped per firm via partial index pattern
CREATE INDEX idx_firm_embeddings_vector
    ON firm_embeddings USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
```

---

### `investment_memos`

Generated investment memos. Each memo is a point-in-time snapshot of
Reidar's analysis of a company for a specific firm. Memos are versioned —
multiple versions may exist as new information arrives.

```sql
CREATE TABLE investment_memos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    firm_company_id UUID NOT NULL REFERENCES firm_companies(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL DEFAULT 1,
    
    -- Generated content (all produced by Claude Sonnet)
    positioning     TEXT,       -- one-liner positioning sentence
    what_they_do    TEXT,       -- product, customer, mechanism
    market_timing   TEXT,       -- why now
    
    fit_score       SMALLINT,   -- 1-5
    fit_rationale   TEXT,       -- why this score
    thesis_alignment TEXT,      -- specific alignment with firm mandate
    thesis_gaps     TEXT,       -- where it falls short
    
    traction_signals TEXT,      -- evidence of real progress
    team_assessment TEXT,       -- founder-market fit analysis
    competitive_landscape TEXT, -- top competitors and differentiation
    
    risks           JSONB,
    -- Array of risk objects:
    -- [{ "risk": "...", "likelihood": "high/medium/low",
    --    "impact": "critical/major/moderate/minor",
    --    "mitigation": "..." }]
    
    comparables     JSONB,
    -- Array of comparable company references:
    -- [{ "company": "...", "differentiation": "...",
    --    "from_portfolio": true/false, "outcome": "..." }]
    
    bull_case       TEXT,       -- "If X proves true, then Y"
    recommended_next_step TEXT, -- pass / monitor / request_intro / diligence
    conviction_level TEXT,      -- pass / watch / interested / excited / high_conviction
    
    -- RAG context used (for auditability)
    pool1_records_used INTEGER,     -- how many Pool 1 records were retrieved
    pool2_records_used INTEGER,     -- how many Pool 2 records were retrieved
    pool2_signals_used JSONB,       -- which specific reasoning signals were injected
    -- This field makes the memo auditable: you can see exactly what prior
    -- reasoning Reidar pulled when generating this output.
    
    -- Generation metadata
    model_used      TEXT NOT NULL DEFAULT 'claude-sonnet-4-5',
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Human feedback
    analyst_rating  SMALLINT,   -- 1-5: how useful was this memo?
    analyst_notes   TEXT,       -- free-text feedback on the memo
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(firm_company_id, version)
);

CREATE INDEX idx_memos_firm ON investment_memos(firm_id);
CREATE INDEX idx_memos_firm_company ON investment_memos(firm_company_id);
```

---

### `firm_notifications`

The unified notification feed for a firm. Every alert — new top match,
signal on a pipeline company, stale deal, pre-meeting brief — is written
here and surfaced through the Command Center bell drawer and Slack.

```sql
CREATE TABLE firm_notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    member_id       UUID REFERENCES firm_members(id),
    -- NULL = notification for the whole firm. Set = for a specific member.
    
    notification_type TEXT NOT NULL,
    -- Values: new_top_match / new_strong_fit / signal_on_pipeline_company /
    --         pre_meeting_brief / stale_deal / second_encounter /
    --         research_complete / weekly_digest / thesis_pattern_detected /
    --         conviction_shift_detected / agent_action_taken
    
    title           TEXT NOT NULL,
    body            TEXT,
    
    related_company_id UUID REFERENCES companies(id),
    related_event_id   UUID REFERENCES events(id)   -- links to events table
    
    -- Delivery
    delivered_in_app    BOOLEAN DEFAULT FALSE,
    delivered_via_slack BOOLEAN DEFAULT FALSE,
    delivered_via_email BOOLEAN DEFAULT FALSE,
    
    read_at         TIMESTAMPTZ,
    acted_on_at     TIMESTAMPTZ,  -- did the analyst click through and take action?
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notifications_firm ON firm_notifications(firm_id);
CREATE INDEX idx_notifications_unread ON firm_notifications(firm_id, read_at) 
    WHERE read_at IS NULL;
```

---

## Schema: Layer 3 — Event Infrastructure

---

### `events`

The central event log for the entire system. This table is the heartbeat
of Reidar's agentic behavior. Every meaningful thing that happens — system
or human — is written here as an immutable record.

V3 replaces V2's APScheduler cron jobs with event-driven agents. Instead
of "run this job every night at 4AM," V3 says "when this event type occurs,
dispatch this agent." Agents read from this table, process events, and mark
them as processed.

This table is APPEND-ONLY. Records are never updated except to set
processed_at. Records are never deleted.

```sql
CREATE TABLE events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    event_type      TEXT NOT NULL,
    -- System events (triggered by Reidar autonomously):
    -- company_sourced / company_enriched / signal_detected /
    -- memo_generated / embedding_created / scrape_completed /
    -- yc_batch_published / hn_launch_detected / ph_launch_detected
    --
    -- User events (triggered by human action):
    -- pipeline_stage_changed / score_overridden / memo_rated /
    -- outreach_sent / note_added / company_added_manually
    --
    -- Integration events (triggered by external services):
    -- email_received / email_sent / calendar_event_created /
    -- transcript_uploaded / slack_message_sent / founder_replied
    --
    -- Agent events (triggered by other agents):
    -- research_agent_started / research_agent_completed /
    -- pre_meeting_brief_generated / signal_agent_completed /
    -- extraction_agent_completed
    
    -- Scope
    firm_id         UUID REFERENCES firms(id),
    -- NULL for system-wide events (company_sourced, yc_batch_published).
    -- Set for firm-specific events.
    
    member_id       UUID REFERENCES firm_members(id),
    -- NULL unless a specific human triggered this event.
    
    -- Entity reference
    entity_type     TEXT,
    -- What is this event about?
    -- Values: company / firm / firm_company / interaction / memo /
    --         founder / signal / scrape_job / agent_run /
    --         calendar_event / slack_message / document
    
    entity_id       UUID,
    -- The UUID of the entity this event concerns.
    
    -- Event data
    payload         JSONB NOT NULL DEFAULT '{}',
    -- All event-specific data. Schema varies by event_type.
    --
    -- For email_received:
    -- { "gmail_message_id": "...", "from": "founder@startup.com",
    --   "subject": "Following up on our call", "company_matched": true,
    --   "company_id": "..." }
    --
    -- For pipeline_stage_changed:
    -- { "from_stage": "first_call", "to_stage": "diligence",
    --   "reason": "strong first call, want to go deeper",
    --   "firm_company_id": "..." }
    --
    -- For yc_batch_published:
    -- { "batch": "S26", "company_count": 247,
    --   "companies_ingested": 247, "top_matches": ["...", "..."] }
    
    -- Processing state
    processed_at    TIMESTAMPTZ,
    -- NULL = not yet processed. Set when an agent has consumed this event.
    -- Three fields may be updated after insert (and only these three):
    -- processed_at, processing_attempts, last_error.
    -- All other fields are immutable. The event record itself is never modified.
    
    processing_attempts INTEGER DEFAULT 0,
    -- How many times has an agent tried to process this event?
    -- Used for retry logic and dead-letter detection.
    
    last_error      TEXT,
    -- If processing failed, what was the error?
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_firm ON events(firm_id) WHERE firm_id IS NOT NULL;
CREATE INDEX idx_events_unprocessed ON events(created_at ASC) 
    WHERE processed_at IS NULL;
-- This index is critical — agents poll for unprocessed events efficiently.
CREATE INDEX idx_events_entity ON events(entity_type, entity_id);
```

**Why this exists:** The events table is what makes Reidar agentic rather
than scheduled. Every trigger for autonomous agent behavior flows through
here. A founder replies to an email → email_received event written →
research_agent sees the event → refreshes the company brief → writes a
firm_notification → marks event as processed. No human initiated any of
this. The event was the trigger.

---

### `agent_runs`

A log of every agent execution — what triggered it, what it did, how
long it took, and whether it succeeded. This provides observability into
Reidar's autonomous behavior and enables debugging when agents fail.

```sql
CREATE TABLE agent_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    agent_type      TEXT NOT NULL,
    -- Values: research_agent / pre_meeting_agent / signal_agent /
    --         extraction_agent / embedding_agent / sourcing_agent /
    --         yc_batch_agent / notification_agent / outreach_agent /
    --         second_encounter_agent
    
    trigger_event_id UUID REFERENCES events(id),
    -- Which event triggered this run? NULL if manually triggered.
    
    firm_id         UUID REFERENCES firms(id),
    entity_type     TEXT,
    entity_id       UUID,
    
    -- Execution
    status          TEXT NOT NULL DEFAULT 'running',
    -- Values: running / completed / failed / timed_out
    
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    duration_ms     INTEGER,
    
    -- What the agent did
    actions_taken   JSONB NOT NULL DEFAULT '[]',
    -- Array of action records:
    -- [{ "action": "fetched_company_data", "source": "harmonic",
    --    "company_id": "...", "success": true },
    --   { "action": "generated_memo", "model": "claude-sonnet-4-5",
    --    "tokens_used": 4821, "success": true }]
    
    -- Output
    output_summary  TEXT,
    -- Human-readable summary of what the agent produced.
    -- Used in the Activity Feed in the Command Center.
    
    error_message   TEXT,
    retry_count     INTEGER DEFAULT 0,
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agent_runs_type ON agent_runs(agent_type);
CREATE INDEX idx_agent_runs_firm ON agent_runs(firm_id) WHERE firm_id IS NOT NULL;
CREATE INDEX idx_agent_runs_status ON agent_runs(status, started_at DESC);
CREATE INDEX idx_agent_runs_trigger ON agent_runs(trigger_event_id);
```

---

### `scrape_jobs`

Tracks the execution of each scraping run — which source was scraped,
how many companies were found, and what the outcome was. Used for
observability and deduplication.

```sql
CREATE TABLE scrape_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    source          TEXT NOT NULL,
    -- Values: yc_api / hn_algolia / producthunt / rss_techcrunch /
    --         rss_venturebeat / rss_strictlyvc / brave_search / harmonic
    
    status          TEXT NOT NULL DEFAULT 'running',
    -- Values: running / completed / failed
    
    companies_found     INTEGER DEFAULT 0,
    companies_new       INTEGER DEFAULT 0,   -- net new records created
    companies_updated   INTEGER DEFAULT 0,   -- existing records updated
    companies_duplicate INTEGER DEFAULT 0,   -- skipped as duplicates
    
    query           TEXT,       -- search query used (for Brave, HN Algolia)
    batch           TEXT,       -- YC batch if applicable (e.g. "S26")
    
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    error_message   TEXT,
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scrape_jobs_source ON scrape_jobs(source, started_at DESC);
CREATE INDEX idx_scrape_jobs_status ON scrape_jobs(status);
```

---

## Key Query Patterns

These are the most common query patterns in the system. Every developer
working on V3 should know these by heart.

### 1. Get a firm's pipeline companies at a specific stage

```sql
SELECT c.*, fc.*
FROM firm_companies fc
JOIN companies c ON c.id = fc.company_id
WHERE fc.firm_id = :firm_id          -- ALWAYS scope by firm_id
  AND fc.pipeline_stage = :stage
ORDER BY fc.updated_at DESC;
```

### 2. Pool 1 retrieval — find globally similar companies

```sql
SELECT c.name, c.one_liner, c.sector, c.stage,
       1 - (ce.embedding <=> :query_embedding) AS similarity
FROM company_embeddings ce
JOIN companies c ON c.id = ce.company_id
WHERE ce.firm_id IS NULL             -- Pool 1: firm_id must be NULL
  AND ce.embedding_type = 'full_profile'
ORDER BY ce.embedding <=> :query_embedding
LIMIT 10;
```

### 3. Pool 2 retrieval — find firm-specific reasoning signals

```sql
SELECT fe.content_text, fe.signal_type, fe.source_type,
       1 - (fe.embedding <=> :query_embedding) AS similarity
FROM firm_embeddings fe
WHERE fe.firm_id = :firm_id          -- Pool 2: firm_id MUST be set
ORDER BY fe.embedding <=> :query_embedding
LIMIT 15;
```

### 4. Combined RAG retrieval (what runs before every generation)

```python
# Run both queries in parallel, merge, weight Pool 2 2x
pool1_results = await retrieve_pool1(query_embedding, limit=10)
pool2_results = await retrieve_pool2(query_embedding, firm_id, limit=15)

# Build context window
context = build_rag_context(
    pool1=pool1_results,
    pool2=pool2_results,
    pool2_weight=2.0
)

# Pass to Claude Sonnet
response = await claude.generate(
    system=firm_mandate_prompt,
    context=context,
    user_query=query
)
```

### 5. Get unprocessed events for agent dispatch

```sql
SELECT * FROM events
WHERE processed_at IS NULL
  AND processing_attempts < 3      -- don't retry indefinitely
ORDER BY created_at ASC
LIMIT 50
FOR UPDATE SKIP LOCKED;            -- prevents race conditions between
                                   -- multiple agent workers
```

### 6. Get a company's full reasoning history for a firm

```sql
SELECT frs.signal_type, frs.signal_text, frs.structured_data,
       frs.signal_date, frs.confidence
FROM firm_reasoning_signals frs
WHERE frs.firm_id = :firm_id
  AND frs.firm_company_id = :firm_company_id
ORDER BY frs.signal_date DESC;
```

---

## Design Rules — Never Violate

1. **Global tables never have firm_id.** If you find yourself adding
   firm_id to companies, founders, investors, or funding_rounds — stop.
   You are solving the wrong problem.

2. **Per-firm tables always have firm_id.** Every query against
   firm_companies, interactions, firm_reasoning_signals, firm_embeddings,
   or any other Layer 2 table must include WHERE firm_id = :firm_id.
   Missing this is the most common bug in multi-tenant systems.

3. **Pool 1 embeddings: firm_id IS NULL. Enforced by CHECK constraint.**
   Pool 2 embeddings: firm_id IS NOT NULL. Enforced by CHECK constraint.
   Never cross-contaminate the pools.

4. **The events table is append-only.** Three fields may be updated
   after insert: processed_at (set when consumed), processing_attempts
   (incremented on each retry), and last_error (set on failure).
   No other field may ever be updated. No row may ever be deleted.

5. **Reasoning signals are extracted, not entered.** firm_reasoning_signals
   is written by the extraction pipeline (Claude Haiku), not by humans
   filling out forms. The schema should never require a human to explicitly
   document their reasoning.

6. **firm_reasoning_signals.signal_text is what gets embedded.** Not the
   raw artifact. Not the full transcript. The extracted, structured,
   compact signal text.

7. **Alembic for all schema changes.** Never modify tables directly in
   Supabase. Every change goes through a migration file.

8. **All timestamps are UTC.** No exceptions.

9. **UUIDs as primary keys throughout.** No integer sequences.

10. **JSONB for structured variable-schema data** (signal payloads, agent
    actions, RAG context records). TEXT for free-form human writing.
    Never store structured data in TEXT fields.
