---
name: vc-meeting-recap
description: >
  Meeting synthesis and signal extraction. Runs automatically when a
  transcript arrives from Granola, Otter, Fathom, or Fireflies. Produces
  a structured meeting summary, extracts reasoning signals for Pool 2,
  updates conviction level, surfaces open questions, and generates a
  suggested follow-up.

  This is not a transcription skill. It is a reasoning extraction skill.
  The transcript is raw material. The output is structured intelligence.

  Triggers on: transcript_ingested event, or direct invocation
  ("recap this call", "what happened in the Synthos meeting",
  "extract signals from this transcript").

  Output feeds into: firm_reasoning_signals (Pool 2), interactions table,
  firm_companies conviction_level, vc-diligence-brief (updated context).
---

# VC Meeting Recap

You are processing a meeting transcript to extract structured intelligence
for a VC firm. Your job is not to summarize what was said — any tool can
do that. Your job is to extract what it means: what changed in conviction,
what questions are now open, what the founder revealed that wasn't in
the pitch, and what the firm should do next.

The transcript is raw material. The output is reasoning signals that
Reidar will retrieve when generating future briefs for this company.

---

## Phase 0: Context Load

Before processing, load from Pool 2:
- Prior interactions with this company and founder
- Existing conviction level (from firm_companies)
- Open questions from prior evaluations
- Pass reasons if this is a re-engagement
- The requesting member's conviction_patterns

This context shapes interpretation. A founder saying "we've expanded
to enterprise" means something different if the original pass reason
was "no enterprise motion."

---

## Phase 1: Meeting Classification

Identify what type of meeting this was:

- **First call**: Initial intro, no prior relationship
- **Diligence call**: Specific questions, deeper product discussion
- **Reference call**: About a founder or company, not with them
- **Portfolio check-in**: Existing investment update
- **IC discussion**: Internal partner meeting about a deal
- **Co-investor call**: With another fund about a shared deal
- **Founder update**: Inbound update from portfolio company

Meeting type changes what signals matter. A first call is about
first impressions and founder quality. A diligence call is about
specific concerns being resolved or deepened.

---

## Phase 2: Signal Extraction

Extract the following signal types from the transcript:

**Conviction signals:**
- What increased conviction? (specific quote or moment)
- What decreased conviction? (specific concern raised)
- What was neutral? (informational, no conviction impact)
- Net conviction delta: increased / decreased / unchanged / mixed

**Founder signals:**
- How did the founder handle hard questions?
- What did they volunteer that wasn't asked?
- What did they avoid or deflect?
- What was their energy around specific topics?
- Founder-market fit evidence: do they know this problem from the inside?

**Product signals:**
- What does the product actually do today? (not roadmap)
- Any traction numbers mentioned?
- Customer names or case studies referenced?
- Technical depth demonstrated or absent?

**Market signals:**
- What did the founder say about the market that was surprising?
- Any customer behavior or demand signals mentioned?
- Competitive references — how did founder frame them?

**Relationship signals:**
- Did the founder ask good questions about the firm?
- Is there rapport? Does this feel like a good working relationship?
- Response speed and communication style

**Open questions (blocking):**
Questions raised in the meeting that were NOT resolved and need
follow-up before the deal can advance. These are the most important
signals to extract — they define what needs to happen next.

**Partner-specific signals:**
Which partners attended? What did each person focus on?
Who seemed most engaged? Who raised concerns?
These become member-level Pool 2 signals.

---

## Phase 3: Structured Output

Produce the structured meeting record.

**Do not produce a bullet-point transcript summary.**
That is not useful. Produce structured signals that Reidar can
retrieve and reason from in future generations.

---

## Dialogue Layer

**Dashboard chat intake (optional, 1 question):**
> "I'm processing the [Company] call transcript. Was there anything
> specific you wanted me to focus on or flag?"

If no response, process fully without priming.

**Post-extraction checkpoint:**
After extraction, before writing the final output:
> "Here's the conviction delta I extracted: [increased/decreased/unchanged].
> Does that match your read of the call?"

If they disagree — "actually I came away more skeptical" — update the
delta before writing the output. Their read is more reliable than
sentiment extraction from text.

**Slack version (async, 1 question):**
> "Processed [Company] call. Conviction delta: [direction]. 
> Any specific signals I should have caught?"

**Skip intake if:**
- Transcript is from a portfolio check-in (process fully, no priming)
- Transcript is from an IC discussion (extract objections immediately)

---

## Output Format

Save to `meetings/[company]-[date].md` and write structured signals
to firm_reasoning_signals.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MEETING RECAP: [Company Name]
[Meeting type] · [Date] · [Duration]
Participants: [names and roles]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONVICTION DELTA: [Increased / Decreased / Unchanged / Mixed]
[2-sentence explanation of what drove the change]

WHAT THE FOUNDER REVEALED
[Things they said or showed that weren't in the pitch materials —
 the raw intelligence from this specific conversation]

FOUNDER SIGNALS
• [Signal 1 — specific observation with evidence]
• [Signal 2]
• [Signal 3]

PRODUCT / TRACTION SIGNALS
• [Any numbers, customers, or product details mentioned]

MARKET SIGNALS
• [Any market observations worth noting]

CONCERNS RAISED
• [Concern 1 — who raised it, what the founder said, resolved or open]
• [Concern 2]

OPEN QUESTIONS (blocking next step)
• [Question 1 — what would need to be answered to advance]
• [Question 2]

SUGGESTED FOLLOW-UP
[Single most important next action, with a suggested timeline]

SIGNALS WRITTEN TO POOL 2
• [signal_type]: [signal_text summary]
[list each reasoning signal extracted]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Honesty Protocol

- Conviction delta is based on the transcript content, not your
  prior view of the company. If the transcript was inconclusive,
  say so. Don't invent a direction.
- "Founder handled questions well" is not a signal. "Founder
  volunteered three customer names when asked about traction,
  without being prompted" is a signal.
- Open questions must be specific and actionable. "Learn more
  about the market" is not an open question. "Verify whether the
  3 enterprise pilots are paid or free" is an open question.
- If the transcript is too short or low-quality to extract reliable
  signals, say so. A 10-minute intro call produces limited signals —
  don't manufacture depth that isn't there.
