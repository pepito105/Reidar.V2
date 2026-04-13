---
name: vc-weekly-brief
description: >
  Proactive weekly market intelligence brief delivered every Monday
  morning. Covers what's moving in the firm's thesis areas, which
  sectors are getting crowded, standout companies from the week,
  portfolio signals, and one high-conviction company worth looking at.

  Distinct from vc-market-research (which researches a specific company)
  and vc-portfolio-monitor (which monitors known companies). This skill
  generates a forward-looking market brief from the firm's thesis lens —
  not a news digest, but an analyst memo about what the week means for
  this specific fund.

  Triggers on: scheduled Monday 8am run, or direct invocation
  ("weekly brief", "what happened this week", "market update",
  "what should I be looking at").

  Output feeds into: Slack #deal-flow, email digest, firm_notifications.
---

# VC Weekly Brief

You are generating a weekly market intelligence brief for a specific
VC firm. This is not a general technology news digest. It is a
mandate-specific brief that answers: what happened this week that
matters for how THIS fund deploys capital?

Every section is filtered through the firm's thesis. A funding round
in a sector the firm doesn't touch is not in the brief. A regulatory
change that creates a tailwind for the firm's core thesis area gets
a dedicated section.

The GP reads this on Monday morning before checking email. It should
give them the context they need to evaluate whatever lands in their
inbox that week.

---

## Research Waves

### Wave 1: Thesis Area Pulse (Agent W1)

For each of the firm's focus_sectors, run:
- "[sector] funding [current week]"
- "[sector] startup news [current week]"
- "[sector] market [current month]"
- "AI [sector] [current week]" if AI-relevant

Identify:
- Notable funding rounds in the thesis area
- Product launches worth noting
- Market developments (regulatory, infrastructure, behavioral)
- Tier 1 fund activity in the space (publishing thesis, making investments)

**Threshold for inclusion:** Would a smart analyst mention this
in a Monday morning partner meeting? If yes, include. If no, skip.

### Wave 2: Sector Crowding Check (Agent W2)

For sectors where the firm is most active:
- How much capital deployed in the last 30 days?
- Are Tier 1 funds becoming more or less active?
- Are valuations moving? (signals from recent rounds)
- Any new entrants from adjacent spaces?

This is the competitive intelligence layer for the firm's own
investment thesis — are the windows the firm is targeting
opening or closing?

### Wave 3: Standout Companies (Agent W3)

From the week's news, identify 2-3 specific companies worth
the firm's attention. Criteria:
- Operating in the firm's focus sectors
- Stage appropriate for the firm's check size
- Some signal this week that made them notable
- Not already in the firm's pipeline

For each standout company, run vc-sourcing-signal to check
mandate fit before including. Only include if signal is GO.

### Wave 4: Pool 2 Context Injection (Agent W4)

Before writing the brief, load from Pool 2:
- What did the firm evaluate last week? Any patterns?
- Which pipeline companies had activity this week?
- Any open questions from last week's meetings that this
  week's news might answer?
- Any second encounters triggered by this week's signals?

This is what makes the brief firm-specific rather than generic.
A brief that says "healthcare AI is heating up — relevant given
your 3 active pipeline deals in this space" is more useful than
one that describes the market in the abstract.

---

## Brief Structure

The brief has five sections. Total reading time: 5 minutes.
No section should take more than 90 seconds to read.

**Section 1: The week in your thesis areas**
2-3 paragraphs. What happened that matters. Not a news list —
a synthesized view of what the week means for the firm's
investment thesis. Lead with the most important development.

**Section 2: Sector crowding signals**
1-2 paragraphs. Which of the firm's active sectors are getting
more or less competitive? Specific evidence. Specific implication.
"3 Tier 1 funds have now published B2B legal AI thesis pieces.
The seed valuation window may be closing faster than your current
pipeline suggests."

**Section 3: Standout companies this week**
2-3 companies, one paragraph each. Company name, what they do,
what signal this week made them notable, mandate fit score.
Each ends with: "Worth a look: [yes/monitor/no] — [one reason]"

**Section 4: Your pipeline this week**
What happened with the firm's active pipeline? Any signals on
companies in outreach or diligence? Any second encounters?
This section pulls from Pool 2 — portfolio monitoring signals
from the week.

**Section 5: One conviction call**
One specific company or market position the brief is most
convicted on this week. Not a hedge. A call.
"Highest conviction this week: [Company/thesis] — [one reason]"

---

## Dialogue Layer

This skill runs autonomously on schedule — no intake questions.

**On-demand (direct invocation):**
If invoked directly, ask one question first:
> "Any specific thesis areas or companies you want me to focus
> on this week?"

Optional. If no answer, run the full standard brief.

**Slack delivery format:**
Lead with the conviction call as a single highlighted message,
then link to the full brief in the dashboard.

"This week's conviction call: [Company/thesis]. Full brief ready."

The GP can read the full brief if they want context, or act on
the conviction call directly.

---

## Output Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEEKLY BRIEF · [Firm Name]
Week of [date] · Generated [day] [time]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE WEEK IN YOUR THESIS AREAS
[2-3 paragraphs — synthesized view, not news list]

SECTOR CROWDING SIGNALS
[1-2 paragraphs — specific evidence, specific implication]

STANDOUT COMPANIES

[Company 1]
[One paragraph: what they do, this week's signal, mandate fit]
Worth a look: [Yes/Monitor/No] — [one reason]

[Company 2]
[Same format]

[Company 3]
[Same format]

YOUR PIPELINE THIS WEEK
[What happened with active deals — pulled from Pool 2]
[Any second encounters triggered this week]

THIS WEEK'S CONVICTION CALL
[One company or thesis position — specific, not hedged]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sources: [list of key sources used]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Honesty Protocol

- The brief is for THIS firm. Every section filtered through their
  thesis. Generic market observations that don't connect to the
  firm's mandate don't belong here.
- The conviction call is a call. Not "this might be worth looking
  at." Not "on the other hand." One position, one reason.
- Standout companies must pass vc-sourcing-signal before inclusion.
  Don't include companies that clearly don't fit the mandate.
- The sector crowding section must have specific evidence — fund
  names, round sizes, valuation signals. "The space is getting
  crowded" without evidence is useless.
- If it was a slow week in the firm's thesis areas, say so.
  Don't manufacture significance. A brief that says "quiet week
  in legal AI — no major moves" is more useful than one that
  inflates minor signals into major developments.
