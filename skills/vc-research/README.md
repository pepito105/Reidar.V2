# VC Research Skills

Reidar's agent stack — 11 specialized capabilities across the full
deal lifecycle. One intelligence, deployed at the right moment,
across the entire workflow.

---

## Invocation Hierarchy

**Tier 1 — Automatic (fires on every company):**
- `vc-sourcing-signal` — triggered by email_received, company_sourced,
  company_added_manually. 60-second triage before the GP opens the email.

**Tier 2 — Standard pipeline (fires when company passes triage):**
- `vc-market-research` — market sizing, timing signals, investment landscape
- `vc-competitive-intelligence` — 6 agents, 3 waves, battle cards
- `vc-founder-assessment` — backgrounds, pattern match, personal lens
- `vc-diligence-brief` — orchestrates all of the above, Pool 2 injected

**Tier 3 — Depth layer (fires when warranted):**
- `vc-positioning-assessment` — when deal passes first_call
- `vc-dataroom-analysis` — when documents are shared
- `vc-ic-prep` — when deal moves to ic_review

**Tier 4 — Final output:**
- `vc-investment-research` — formal investment memo and recommendation

**Tier 5 — Always-on background agents:**
- `vc-meeting-recap` — fires on every transcript_ingested event
- `vc-portfolio-monitor` — scheduled weekly + on signal_detected
- `vc-weekly-brief` — every Monday 8am, mandate-filtered market intel

---

## Pipeline Stage Mapping

| Stage | Skill |
|-------|-------|
| watching | vc-sourcing-signal |
| outreach | vc-diligence-brief (full pipeline) |
| first_call | vc-positioning-assessment |
| diligence | vc-dataroom-analysis |
| ic_review | vc-ic-prep → vc-investment-research |
| any stage | vc-meeting-recap (on transcript) |
| portfolio | vc-portfolio-monitor (continuous) |
| firm-wide | vc-weekly-brief (Monday morning) |

---

## Surfaces

| Skill | Dashboard | Slack | Email | Autonomous |
|-------|-----------|-------|-------|------------|
| vc-sourcing-signal | — | ✓ | — | ✓ |
| vc-diligence-brief | ✓ | ✓ | — | ✓ |
| vc-positioning-assessment | ✓ | ✓ | — | ✓ |
| vc-dataroom-analysis | ✓ | — | — | ✓ |
| vc-ic-prep | ✓ | ✓ | — | ✓ |
| vc-investment-research | ✓ | — | — | — |
| vc-meeting-recap | ✓ | ✓ | — | ✓ |
| vc-portfolio-monitor | ✓ | ✓ | — | ✓ |
| vc-weekly-brief | ✓ | ✓ | ✓ | ✓ |

---

## The Two Learning Modes

Every skill in this stack learns two ways:

**Passive** — every score override, pass reason, IC objection, and
conviction shift is automatically extracted as a Pool 2 reasoning signal.
Skills become more calibrated over time without any configuration.

**Active** — tell Reidar something directly ("we never back first-time
founders in healthcare without a clinical operator") and the relevant
skill updates immediately. The next output reflects what you told it.

Both update the same underlying skill stack. Neither requires a
training session.

---

## What the Stack Knows After 12 Months

On day one: generic baseline calibrated to your stated mandate.

After 12 months:
- Your highest-conviction founder pattern (from 847 evaluations)
- Which partners raise which objections at IC (from transcript signals)
- Your pass patterns and what conditions would reverse them (second encounter)
- Which sectors are drifting from your stated thesis (proactive intelligence)
- What moved in your thesis areas this week (weekly brief)

This context exists nowhere else. It compounds with every decision.
