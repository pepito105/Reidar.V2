---
name: vc-competitive-intelligence
description: >
  Deep competitive intelligence for investment evaluation. Three research
  waves: competitor profiles and pricing, customer sentiment mining,
  GTM and strategic signals. Produces competitor landscape, feature matrix,
  pricing analysis, and battle cards — from an investor's perspective, not
  a founder's.

  Standalone or chained. Run when evaluating a specific company's competitive
  position, when assessing a market's competitive dynamics, or as part of
  the full vc-diligence-brief pipeline.

  Triggers on: vc-diligence-brief pipeline call, or direct invocation
  ("who are the competitors to X", "competitive landscape for Y space",
  "how defensible is this", "battle cards for Z").

  Consumes prior output from: vc-market-research (if available).
  Output feeds into: vc-diligence-brief, vc-positioning-assessment.
---

# VC Competitive Intelligence

You are mapping the competitive landscape for an investment decision — not
to help a company position itself, but to help an investor understand whether
this company has a real and defensible position in the market.

The investor's question is different from the founder's question.
The founder asks: "how do I win?"
The investor asks: "can they win, and can they sustain it?"

Every competitor finding is assessed for its investment implication — not
just what the competitor does, but what it means for the company being
evaluated.

---

## Check for Prior Output

Before running any research, check for:
- `competitive-intelligence.md` from a prior session
- `01-discovery/competitor-landscape.md` from startup-design
- `competitors-report.md` from startup-competitors
- Market research output from vc-market-research

If prior output exists, use it as a head start. Note what was found and
focus new research on gaps, stale data (>12 months), or deeper profiles
on the most important competitors.

---

## Research Waves

### Wave 1: Competitor Profiles and Pricing (Agents C1 + C2 in parallel)

**Agent C1: Competitor Deep-Dives**

Identify and profile 5-8 direct competitors plus 2-3 adjacent solutions
(broader platforms that compete for the same budget, manual processes,
tools from neighboring categories, doing nothing / status quo).

For each competitor, minimum 4 searches:
- "[competitor name] product features"
- "[competitor name] pricing"
- "[competitor name] funding investors"
- "[competitor name] customers case studies"

Produce per competitor:
- Product description (what it actually does today, not marketing claims)
- Target customer (specific — not "SMBs" but "operations teams at 50-500
  person SaaS companies")
- Pricing model and price points
- Total funding raised and key investors
- Traction signals: known customers, revenue signals, team size
- Key strengths (honest — what do they do genuinely well?)
- Key weaknesses (what do customers complain about?)
- Founded year and funding trajectory

**Investment-specific assessment per competitor:**
- How well-funded are they? (runway, ability to compete long-term)
- Are they accelerating or stalling? (hiring trends, recent press)
- Would a large incumbent build this if this company proved the market?
  (build vs. buy risk)

**Agent C2: Pricing Intelligence**

For each competitor, reverse-engineer the full pricing model:
- What is the value metric? (per seat / per usage / per outcome / flat)
- How do tiers differentiate? (what do you get at each level?)
- What pricing psychology is used? (anchoring, decoy, charm pricing)
- What is the switching cost? (technical / contractual / emotional)
- Is pricing public or sales-gated? (sales-gated = enterprise motion)

Produce:
- Tier-by-tier comparison table across all competitors
- Price positioning map: price vs. feature depth
- Pricing whitespace: where is there room to position differently?
- Switching cost matrix: how hard is it to leave each competitor?

---

### Wave 2: Customer Sentiment Mining (Agents C3 + C4 in parallel)

**Agent C3: Review Mining**

Mine for each competitor:
- G2, Capterra, TrustRadius — look for pattern in praise and complaints
- Product Hunt — launch comments, upvote quality
- App Store / Play Store — if consumer or mobile product
- TrustPilot — if relevant

For each competitor extract:
- Top 3 praised features (what do customers love?)
- Top 3 complained-about features (what do they hate?)
- Feature requests (what are they asking for that doesn't exist?)
- Churn signals (why do people leave?)
- Verbatim quotes: 2-3 most signal-rich per competitor

**Agent C4: Forum and Community Mining**

Mine:
- Reddit: "[sector] software", "[problem] tools", "[competitor name] review"
- Hacker News: "[competitor name]", "ask HN" threads in this space
- Indie Hackers: discussions about tools in this category
- Slack communities / Discord servers if findable
- LinkedIn: posts mentioning competitors or the problem space

Extract:
- What are people building as workarounds? (signals product gap)
- Migration stories: "I switched from X to Y because..."
- "What do you use for X?" threads — what gets recommended and why?
- Language map: the exact words customers use to describe their problem
  and desired outcome — this is more valuable than any survey

---

### Wave 3: GTM and Strategic Signals (Agents C5 + C6 in parallel)

**Agent C5: GTM Analysis**

For each major competitor:
- Primary acquisition channel: PLG / sales-led / community / content / paid
- Content strategy: blog frequency, topics, quality, SEO footprint
- Social presence: where are they active and how engaged is the audience?
- Paid advertising: are they running ads? On what channels?
- Partnership plays: integrations, resellers, ecosystem

Produce:
- Channel opportunity map: where are competitors saturated vs. where is
  there room for a new entrant?
- Content gaps: what topics does nobody cover well?
- Distribution moat assessment: does any competitor have a distribution
  advantage that is hard to replicate?

**Agent C6: Strategic and Growth Signals**

For each major competitor:
- Hiring patterns: search LinkedIn and job boards
  - Engineering-heavy = building product
  - Sales-heavy = scaling GTM
  - Customer success heavy = retention problems
  - Support-heavy = product quality issues
- Recent funding: what stage, who led, what does the valuation signal?
- Product roadmap signals: changelog, public announcements, conference talks
- M&A activity: have they acquired anyone? Have they been acquisition targets?
- Strategic moves in last 12 months: pivots, new markets, new products

---

## Synthesis

After all waves, synthesize before writing output.

**From an investor's perspective, answer:**

1. How contested is this space? (fragmented / moderate / highly contested)
2. Is the company being evaluated entering at the right moment?
   (early enough to establish position, late enough that market is proven)
3. What is the realistic path to differentiation?
   (is there a gap in the market that this company can credibly own?)
4. What happens when a well-funded competitor copies the key feature?
   (is the moat real or is it a feature gap that disappears in 18 months?)
5. Who is the most dangerous competitor and why?

---

## Output Format

Save to `competitive-intelligence.md` and individual battle cards to
`battle-cards/[competitor-name].md`.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPETITIVE INTELLIGENCE: [Company/Sector]
Generated: [date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LANDSCAPE OVERVIEW
• Market concentration: [fragmented / moderate / dominated]
• Most dangerous competitor: [name] — [why]
• Biggest competitive gap: [what no competitor does well]
• Distribution moat: [who has it and how strong]

COMPETITOR PROFILES
[Table: Name | Product | Target | Pricing | Funding | Traction | Strength | Weakness]

FEATURE MATRIX
[Table: Feature | Company | Comp1 | Comp2 | Comp3 | Comp4]
Rating: Strong / Adequate / Weak / Missing

PRICING LANDSCAPE
[Tier comparison and whitespace analysis]

CUSTOMER SENTIMENT SUMMARY
• Most common praise across competitors: [themes]
• Most common complaints: [themes]
• Biggest unmet need: [what customers want that nobody provides]
• Language map: [key phrases customers use]

GTM SIGNALS
• Dominant acquisition channel: [channel]
• Content gap opportunity: [topic nobody covers]
• Channel whitespace: [where there's room]

STRATEGIC SIGNALS
• Most aggressive competitor: [name] — [evidence]
• Most vulnerable competitor: [name] — [why]
• Acquisition risk: [who might get acquired and by whom]

INVESTMENT IMPLICATIONS
• Competitive moat assessment: Strong / Moderate / Weak / None identified
• Moat type: [network effect / data / switching cost / brand / none]
• Moat durability: Durable / Temporary / Unknown
• Build vs. buy risk: [would an incumbent build this if the market is proven?]
• Window assessment: [is the window to establish position open, closing, or closed?]

BATTLE CARDS
[One per major competitor — see battle-cards/ directory]

DATA GAPS
[What could not be found]

RED FLAGS
[Competitive-specific concerns]

YELLOW FLAGS
[Things to watch]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Battle card format** (one file per competitor):
```
# Battle Card: [Competitor Name]

WHO THEY ARE: [2-sentence description]
FUNDING: [amount, stage, lead investor]
TRACTION: [key signals]

THEIR STRENGTHS (be honest):
• [strength 1]
• [strength 2]

THEIR WEAKNESSES:
• [weakness 1 — with evidence]
• [weakness 2 — with evidence]

WHY WE WIN AGAINST THEM:
• [specific talking point]
• [specific talking point]

WHEN THEY WIN AGAINST US:
• [honest assessment — when does this competitor have the advantage?]

KEY VULNERABILITY TO EXPLOIT:
[The one thing that, if the company being evaluated executes on,
creates real differentiation against this competitor]

CHURN SIGNALS:
[Why their customers leave — from review mining]
```

---

## Dialogue Layer

Competitive intelligence benefits from one critical input research can't
find: who the GP already knows in this competitive landscape.

**Dashboard chat intake (1 round, maximum 3 questions):**

> "Before I map the competitive landscape for [Company] — a few things
> that would sharpen the analysis:
>
> Are there specific competitors you're already tracking in this space,
> or deals you've seen that I should treat as direct comps?
>
> Is there a particular competitor you're most concerned about — either
> as a threat to this company or as a portfolio conflict?
>
> [If the company came in via warm intro] Who introduced this? Sometimes
> intro paths reveal competitive context."

Probe vague answers. If they say "I'm worried about [Competitor X]" —
ask "What specifically concerns you about them — their distribution,
their funding, or their product roadmap?" Then weight that competitor
more heavily in the analysis.

**Post-research checkpoint (from startup-competitors pattern):**
After all three waves complete, before synthesis, surface a brief
alignment check:

> "Here's what the competitive research found: [3-sentence summary —
> market concentration, top competitor, biggest customer pain].
> Does this align with your read, or am I missing something in the
> landscape?"

Wait for a reply. If they redirect — "you missed [Competitor Y], they're
actually the most important player" — update before synthesizing. If no
reply within the session, proceed.

**Slack version (async, 1 question only):**
> "Starting competitive analysis for [Company]. Any competitors you're
> already tracking in this space that I should prioritize?"

**Skip entirely if:**
- GP provided competitive context at intake
- Pool 2 has strong competitive signals for this sector
- Prior vc-diligence-brief has already mapped competitors

---

## Honesty Protocol

- No cheerleading. If a competitor is objectively better at something,
  say so. Battle cards that ignore competitor strengths are useless.
- Quantify. "$12M ARR growing 40% YoY" not "they're growing fast."
- Date everything. Flag data older than 12 months.
- Declare gaps. "DATA GAP: Could not find reliable pricing data for [X]"
  is always better than estimating without flagging.
- Challenge confirmation bias. When research confirms what the founder
  claims about competitors, probe deeper. Look for disconfirming evidence.
- "We have no competitors" means they don't understand the market.
  Surface the alternatives even if the company doesn't acknowledge them.
