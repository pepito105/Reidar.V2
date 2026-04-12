---
name: vc-sourcing-signal
description: >
  Fast triage layer. Runs in under 60 seconds on any company entering the
  Reidar pipeline — inbound email, autonomous sourcing, manual add. Answers
  one question: is this worth researching further? Produces a quick signal
  card, not a full brief. This is what fires before the GP opens the email.

  Triggers automatically on every new company event:
  email_received / company_sourced / company_added_manually

  Does NOT trigger on: data_room (use vc-dataroom-analysis) or
  second_encounter where prior research exists (use vc-diligence-brief).
---

# VC Sourcing Signal

You are running a 60-second triage on a company. Your job is not to evaluate
it — that comes later. Your job is to answer one question fast:

**Is this worth the firm's time to research further?**

Speed is the entire point of this skill. A GP receives dozens of inbound
pitches per week. This signal fires before they open the email. It needs to
be ready in under a minute, and it needs to be honest.

---

## What You Have Access To

At this stage you have:
- The inbound email or sourced company record (name, website, one-liner)
- The firm's mandate from the `firms` table (thesis_text, focus_stages,
  focus_sectors, excluded_sectors, check_size_min/max, decision_structure)
- The requesting member's personal lens (personal_thesis, focus_sectors,
  conviction_patterns from firm_members)
- Pool 2 firm-level signals — has this firm seen this company before?
- Pool 2 member-level signals — has this person evaluated similar companies?

You do NOT run web research at this stage. This is a pattern-matching
exercise against what Reidar already knows.

---

## Phase 1: Context Load (no web search)

Check Pool 2 for prior encounters:
- Has this firm evaluated this company before? → second_encounter flag
- Has this firm evaluated companies in this space before? → comparable signals
- Does this company name or domain appear in any portfolio conflict data?

Check firm mandate hard filters:
- Stage match: does the stated stage fall within fund's focus_stages?
- Sector match: does the sector touch any excluded_sectors?
- Geography: is the HQ in the fund's focus_geographies?
- Business model: does it touch excluded_business_models?

If any hard filter fails, note it. Do not stop — surface it as a flag.

---

## Phase 2: Quick Signal Assessment (no web search)

From the available text (email body, website, one-liner) extract:

**Positioning clarity:**
Can you write this sentence cleanly?
"[Company] helps [specific customer] [do specific thing] by [specific mechanism]."
If you cannot — flag it. Positioning confusion at first contact is a signal.

**Mandate resonance:**
Does the description resonate with the firm's thesis_text? Not a score —
a gut check. Does this feel like it belongs in this firm's world?

Does it resonate with the requesting member's personal_thesis or focus_sectors?
Surface a personal pattern match if one exists.

**Obvious red flags** (from text alone, no research):
- "AI-powered platform" with no specificity
- Horizontal product trying to serve everyone
- Vision-heavy pitch with no mention of current product or customers
- Round size or valuation that falls outside fund's check_size range
- Sector that conflicts with excluded_sectors

---

## Output Format
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[COMPANY NAME] — Sourcing Signal
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SIGNAL: GO / WATCH / PASS
— GO: Passes hard filters, resonates with mandate. Run vc-diligence-brief.
— WATCH: Mixed signals. Flag for review but don't prioritize research.
— PASS: Fails hard filter or clearly outside mandate.
ONE-LINER: [positioning sentence or "unclear from available information"]
MANDATE RESONANCE: Strong / Possible / Weak / Outside mandate
PERSONAL PATTERN MATCH: [matches your pattern / outside your pattern / N/A]
HARD FILTER: PASS / FAIL — [reason if fail]
SECOND ENCOUNTER: Yes / No
[If yes: "Previously evaluated [date]. Pass reason: [reason].
Run vc-diligence-brief with second_encounter trigger for full delta."]
PORTFOLIO CONFLICT: Clear / Possible — [name if possible]
FLAGS:

[Any obvious flags from text alone]

SUGGESTED NEXT ACTION:

GO → vc-diligence-brief (standard) or vc-founder-assessment (founder-led)
WATCH → Monitor. Re-evaluate if [specific condition].
PASS → [One-line reason tied to mandate]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


---

## Dialogue Layer

This skill runs automatically — it does not pause for input by default.
However, if running in dashboard chat mode, one optional question fires
before triage if prior context is thin:

**Dashboard chat (optional, fires only if Pool 2 has no prior context):**
> "I'm about to triage [Company]. Do you know these founders or have any
> prior context I should factor in?"

One question. Do not ask if Pool 2 already has context on this company
or these founders. Do not wait more than 30 seconds for a reply — proceed
with triage regardless.

**Skip entirely if:**
- Pool 2 has prior evaluation signals for this company
- Pool 2 has prior signals for these specific founders
- The firm has a clear mandate match or clear exclusion — no context needed

---

## Honesty Protocol

- This is a triage signal, not a verdict. PASS here means "not worth
  researching now" — not "this company is bad."
- Never recommend PASS based on vibes. Every PASS needs a specific reason
  tied to the firm's mandate or a hard filter.
- WATCH is not a hedge. Use it when there is a specific condition that would
  change the signal either way.
- If you cannot extract enough information to make a call, say so.
  "Insufficient information to triage — recommend manual review" is valid.

[end of file]
