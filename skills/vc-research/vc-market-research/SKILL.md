---
name: vc-market-research
description: >
  Market sizing, timing analysis, and investment landscape research.
  Standalone or chained. Run when evaluating a company in a new sector,
  when a GP wants to understand a market independent of any specific company,
  or as part of the full vc-diligence-brief pipeline.

  Triggers on: vc-diligence-brief pipeline call, or direct invocation
  ("what's happening in legal AI", "size the market for X",
  "is now the right time for Y").

  Output feeds into: vc-diligence-brief (synthesis layer).
  Prior output consumed by: vc-competitive-intelligence, vc-positioning-assessment.
---

# VC Market Research

You are researching a market to answer three questions for an investor:

1. **Is this market large enough to matter?** (size)
2. **Is this the right moment to enter it?** (timing)
3. **Is capital flowing here, and what does that signal?** (investment landscape)

Every claim requires a source. Every figure requires a date. Estimates are
labeled as estimates. If you cannot find data, you say so.

---

## Check for Prior Output

Before running any research, check if market research has already been
completed for this company or sector in this session. Look for:
- `market-research.md` in the working directory
- `01-discovery/market-analysis.md` from a startup-design session

If prior output exists, read it and use it as a starting point. Note what
was found previously and focus new research on gaps or data older than
12 months.

---

## Research Waves

### Wave 1: Market Sizing (Agent M1)

**Minimum 6 searches:**
- "[sector] market size [current year]"
- "[sector] TAM total addressable market"
- "[sector] market growth rate CAGR forecast"
- "[sector] market research report [current year]"
- "[specific subsector] revenue [current year]"
- "[sector] market size enterprise vs SMB" (if B2B)

**Produce:**
- TAM with source, date, and confidence rating (High/Medium/Low)
- SAM — the serviceable portion given this company's specific focus
- SOM — realistic capture in 3-5 years
- Growth rate with CAGR and forecast horizon
- Market maturity: early-stage / growing / consolidating / mature
- Unit economics benchmarks: CAC, LTV, gross margin typical for this category

**Source quality tiers:**
- Tier 1: Gartner, IDC, Forrester, McKinsey, BCG, government data, SEC filings
- Tier 2: TechCrunch, WSJ, FT, Bloomberg, Reuters, credible industry press
- Tier 3: Blogs, social media, vendor-produced reports

**Flag:** If market size estimates vary by more than 3x across sources,
report the full range and explain which source is most credible and why.
Never average conflicting figures. Never present Tier 3 data as Tier 1.

---

### Wave 2: Timing Signals (Agent M2)

Timing kills more startups than competition. This wave answers: why now?
What changed in the last 2-3 years that makes this possible or necessary today?

**Minimum 5 searches:**
- "[enabling technology] adoption rate [current year]"
- "[sector] regulatory changes [recent years]"
- "[sector] behavior shift post-[relevant event]"
- "[sector] infrastructure maturity [current year]"
- "[sector] venture investment activity [current year]"

**Assess each timing signal:**
- What specifically changed?
- When did it change?
- How does it make this company's approach possible or necessary now?
- Is this a genuine tailwind or a hype cycle?

**Timing categories:**
- Regulatory tailwind: new rules create demand or remove barriers
- Infrastructure tailwind: enabling technology reached sufficient maturity
- Behavioral shift: customer behavior changed in a durable way
- Market event: incumbent failure, consolidation, or exodus created a gap
- Economic shift: cost structure changed to make the model viable

**Timing verdict:**
- Too early: infrastructure or behavior not yet there
- On time: genuine tailwinds present, market is ready
- Late: established players have locked in customers, window closing

**Flag:** "The market will be ready in 3 years" is hope, not a timing signal.
If the only timing signals are aspirational, flag this explicitly.

---

### Wave 3: Investment Landscape (Agent M3)

**Minimum 5 searches:**
- "[sector] venture funding [current year]"
- "[sector] startups funded [recent months]"
- "[sector] Series A Series B [current year]"
- "largest [sector] funding rounds [current year]"
- "[sector] M&A acquisitions [recent years]"

**Produce:**
- Total VC investment in this sector over last 24 months
- Notable recent rounds (company, amount, stage, lead investor)
- M&A activity: who is acquiring in this space and why?
- Investor thesis convergence: are top-tier funds articulating a thesis here?
- Capital concentration: is money going to a few leaders or distributed?

**Signal interpretation:**
- Heavy early-stage investment = market formation underway
- Growth-stage concentration = winners emerging, window for new entrants narrowing
- Strategic acquirer activity = incumbents taking the space seriously
- Tier 1 fund thesis published = institutional validation

---

## Output Format

Save to `market-research.md`.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MARKET RESEARCH: [Sector/Company]
Generated: [date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MARKET SIZE
• TAM: [figure] — Source: [source], [date] — Confidence: [H/M/L]
• SAM: [figure] — [rationale for addressable portion]
• SOM: [figure] — [rationale for realistic capture]
• Growth rate: [CAGR] through [year] — Source: [source]
• Market maturity: [early / growing / consolidating / mature]

UNIT ECONOMICS BENCHMARKS (this category)
• Typical CAC: [range] — Source: [source]
• Typical LTV: [range] — Source: [source]
• Typical gross margin: [range] — Source: [source]

TIMING SIGNALS
• [Signal 1]: [what changed, when, why it matters] — Source: [source]
• [Signal 2]: [what changed, when, why it matters] — Source: [source]
• [Signal 3]: [what changed, when, why it matters] — Source: [source]
• Timing verdict: [too early / on time / late] — [2-sentence rationale]

INVESTMENT LANDSCAPE
• Total VC investment (24 months): [figure] — Source: [source]
• Notable recent rounds: [list]
• M&A activity: [summary]
• Investor thesis signal: [are top funds publishing a thesis here?]

CONFIDENCE DASHBOARD
[Major claim | Source tier | Sources | Confidence | Date]

DATA GAPS
[What could not be found — be explicit]

RED FLAGS
[Market-specific concerns]

YELLOW FLAGS
[Things to watch]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Dialogue Layer

Market research is largely factual — questions that are answerable from
web research don't need to be asked. The exception is when the GP has
proprietary market knowledge that research can't surface.

**Dashboard chat intake (1 round, maximum 3 questions):**

Ask these conversationally, not as a checklist. Group naturally.
Only ask what Pool 2 context doesn't already answer.

> "Before I research the [sector] market — a few quick questions:
>
> What's your current read on this space? Are you bullish on the timing,
> or does something feel off to you about where the market is right now?
>
> [If applicable] Do you have any existing deals or portfolio companies in
> this sector I should factor into the analysis?"

Acknowledge the answer. If they say something specific — "I think the
market is moving faster than most people realize because of [X]" — probe
it: "What specifically makes you think [X] is accelerating?" Then run
research with their answer as context.

**Slack version (async, 1 question only):**
> "Running market research on [sector] for [Company]. Any specific timing
> concerns or thesis angles you want me to prioritize?"

**Skip entirely if:**
- GP has provided no context signal that suggests a specific angle
- Market research has already been completed in this session
- Pool 2 has strong market signals for this sector from prior evaluations

---

## Honesty Protocol

- Quantify everything. "The market is growing fast" is not useful.
  "$4.2B at 12.3% CAGR through 2028" is useful.
- Date all data. Flag anything older than 18 months.
- Surface contradictions. When analyst reports disagree significantly,
  report the range and explain which to trust.
- A large TAM is not a thesis. Many large markets are also heavily
  contested. Surface both the size and the competitive intensity.
