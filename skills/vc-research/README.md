# VC Research Skills

## Invocation Hierarchy

**Tier 1 — Automatic (fires on every company):**
- `vc-sourcing-signal` — triggered by email_received, company_sourced, company_added_manually

**Tier 2 — Standard pipeline:**
- `vc-market-research`
- `vc-competitive-intelligence`
- `vc-founder-assessment`
- `vc-diligence-brief` (orchestrates the above)

**Tier 3 — Depth layer:**
- `vc-positioning-assessment` — when deal passes first_call
- `vc-dataroom-analysis` — when documents are shared
- `vc-ic-prep` — when deal moves to ic_review

**Tier 4 — Final output:**
- `vc-investment-research` — formal memo and recommendation

## Pipeline Stage Mapping

| Stage | Skill |
|-------|-------|
| watching | vc-sourcing-signal |
| outreach | vc-diligence-brief |
| first_call | vc-positioning-assessment |
| diligence | vc-dataroom-analysis |
| ic_review | vc-ic-prep → vc-investment-research |
