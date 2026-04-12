---
name: vc-positioning-assessment
description: >
  Positioning strength analysis using April Dunford's framework — from
  an investor's perspective. Assesses whether a company has a genuinely
  defensible market position or is competing head-to-head with better-funded
  players.

  Standalone or chained. Run when assessing competitive defensibility,
  when a deal is heading to IC and the moat question is unresolved,
  or as part of the full vc-diligence-brief pipeline.

  Consumes prior output from: vc-competitive-intelligence (if available).
  Output feeds into: vc-diligence-brief, vc-ic-prep.

  Triggers on: vc-diligence-brief pipeline call, or direct invocation
  ("how defensible is this", "what's their moat", "positioning analysis",
  "can they hold this position", "Onliness test").
---

# VC Positioning Assessment

You are assessing whether this company has a genuinely defensible market
position — not whether their messaging is compelling, but whether the
underlying position is real and can be held over time.

The investor's question is:
**If this company succeeds, can they sustain it? Or does their position
erode as competitors copy features and incumbents enter the market?**

You use April Dunford's 5+1 positioning framework, adapted for investment
evaluation. The goal is not to help them position better — it's to assess
whether their current position is investable.

---

## Check for Prior Output

Before running research, check for:
- `positioning-assessment.md` from a prior session
- `positioning-doc.md` from startup-positioning session
- `competitive-intelligence.md` or `01-discovery/competitor-landscape.md`
  — competitive alternatives already mapped

If competitive intelligence exists, use it to seed the alternatives map
and skip re-researching competitors already profiled.

---

## Phase 1: Competitive Alternatives Map

**From an investor's perspective, the alternatives map is more important
than the competitor list.** Customers don't just choose between direct
competitors — they choose between all available options including:
- Direct competitors (same customer, same use case)
- Adjacent tools (different approach, same problem)
- Broader platforms that include this as a feature
- Manual processes and workarounds
- Hiring someone
- Doing nothing / status quo

If vc-competitive-intelligence has already run, extract the alternatives
from its output. If not, run targeted research:

Minimum 4 searches:
- "[problem this company solves] solutions"
- "[customer type] workflow [problem area]"
- "how do [customer type] currently [solve this problem]"
- "[company name] alternatives"

For each alternative:
- What job does the customer hire it for?
- Where does it fall short?
- What triggers switching away from it?
- What is the switching cost?

---

## Phase 2: Dunford 5+1 Assessment

Work through each component in order. The sequence matters — each builds
on the previous.

**Component 1: Competitive Alternatives (from Phase 1)**
What would customers use if this company didn't exist?
This is the anchor. Positioning is always relative to alternatives.

**Component 2: Unique Attributes**
What does this company have that the alternatives lack?
Be specific and honest. Assess each claimed attribute:
- Is it real? (does the evidence support it?)
- Is it unique? (do competitors have it too?)
- Is it defensible? (how long before competitors copy it?)

Attribute types (in order of durability):
- Proprietary data or network: very durable
- Technical architecture: moderately durable (12-24 months to copy)
- Integration depth: moderately durable (switching cost)
- Team expertise: moderately durable (can't be hired away easily)
- Feature advantage: temporary (weeks to months to copy)
- UX advantage: temporary (easiest thing to copy)

**Component 3: Value Translation**
Do their unique attributes translate into outcomes customers care about?
The investor question: "So what?" — what does each unique attribute
actually enable for the customer?

**Component 4: Best-Fit Customers**
Who gets the most value from this company's unique attributes?
Not "SMBs" — "operations managers at 50-500 person SaaS companies who
are spending 4+ hours per week on manual reporting."
The more specific the best-fit customer, the more credible the position.
Vague customer definition is a positioning red flag.

**Component 5: Market Category**
What category frame makes their unique attributes most obvious?
Assess the category strategy:
- **Head-to-head**: competing in an existing category dominated by
  established players. Difficult without significant differentiation
  or a much better-funded war chest.
- **Subcategory**: carving a specific niche within a larger category.
  Viable — but niche must be defensible and large enough to matter.
- **Category creation**: defining a new category. Expensive — requires
  educating the market. Only viable if the company has the resources
  and the category is genuinely new.

**Component 6: Trend Overlay (optional)**
Is there a genuine trend that makes this positioning stronger over time?
Avoid forced trend alignment — only include if the trend materially
changes buyer expectations in a way that favors this company.

---

## Phase 3: Stress Tests

**Onliness Test (Neumeier):**

Basic form:
"[Company] is the only [category] that [differentiator] for [target]."

Extended form:
"[Company] is the only [category] that [differentiator] for [target]
who [need] in [context]."

Assessment:
- Convincing: the "only" claim is specific, defensible, and not easily
  contested by a competitor with a minor feature update
- Stretch: the claim is technically true but a competitor could make
  the same claim within 12-18 months
- Cannot be stated: no defensible "only" claim exists — the company
  is competing on degree, not kind

**Mental Ladder Test (Ries/Trout):**
- Is the position simple enough to remember?
- Does it claim one clear rung?
- Is that rung available — not already owned by a competitor?
- Can it be explained in one sentence?

**Incumbent Response Test:**
What happens if the most well-funded competitor in this space launches
a direct attack on this position in 18 months?
- Does the unique attribute survive? (proprietary data and network effects do)
- Does the customer relationship survive? (switching costs matter here)
- Does the distribution advantage survive? (first-mover SEO, integrations)

---

## Output Format

Save to `positioning-assessment.md`.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POSITIONING ASSESSMENT: [Company Name]
Generated: [date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DUNFORD 5+1 ASSESSMENT

1. Competitive Alternatives
[What customers use today instead — full list including status quo]

2. Unique Attributes
[What this company has that alternatives don't — with durability rating]
• [Attribute 1]: [Durable / Temporary / Unverified] — [evidence]
• [Attribute 2]: [Durable / Temporary / Unverified] — [evidence]

3. Value Translation
[What each unique attribute enables for the customer]
• [Attribute] → [Customer outcome]

4. Best-Fit Customer
[Specific description — not demographic, behavioral]

5. Market Category
• Strategy: [Head-to-head / Subcategory / Category creation]
• Assessment: [why this category, and whether it's the right choice]
• Risk: [what's the downside of this category strategy?]

6. Trend Overlay
• [Relevant trend / None identified]

STRESS TESTS

Onliness Test:
"[Company] is the only [category] that [differentiator] for [target]."
Verdict: [Convincing / Stretch / Cannot be stated]
[1-sentence rationale]

Mental Ladder Test:
• Simple: [Yes / No]
• One rung: [Yes / No]
• Rung available: [Yes / No — if no, who owns it?]
Verdict: [Passes / Fails]

Incumbent Response Test:
• If [most dangerous competitor] launches a direct attack in 18 months:
  [What survives? What doesn't?]
• Verdict: [Position holds / Position at risk / Position does not survive]

POSITIONING STRENGTH SUMMARY
• Overall: Strong / Moderate / Weak / Unclear
• Moat type: [Network effect / Data moat / Switching cost / Brand / None]
• Moat durability: Durable (3+ years) / Moderate (1-2 years) / Temporary (<1 year)
• Biggest positioning risk: [specific]
• Biggest positioning opportunity: [specific]

DATA GAPS
[What could not be assessed]

RED FLAGS
[Positioning-specific concerns]

YELLOW FLAGS
[Things to probe at IC]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Dialogue Layer

Positioning assessment is analytical — it derives from research, not
from the GP's prior knowledge. The one exception is when the GP has a
specific positioning concern they want stress-tested.

**Dashboard chat intake (1 round, 1-2 questions):**

> "I'm about to assess [Company]'s market position. Is there a specific
> positioning concern you want me to focus on — for example, a competitor
> you think they're too similar to, or a moat claim in their pitch you're
> skeptical about?"

If they surface a specific concern — "their deck claims a proprietary
dataset moat but I'm not sure it's real" — make the Onliness Test for
that specific claim the primary output. If no specific concern, run the
full standard assessment.

**Mid-process component pause (from startup-positioning ⏸ pattern):**
After extracting unique attributes from research but before translating
to value themes:

> "Research suggests [Company]'s strongest unique attribute is
> [attribute]. Before I assess this as a moat — does this match
> your read from the pitch, or do you think their real differentiator
> is something else?"

This is the most important pause in positioning assessment. GPs
sometimes see differentiation in a pitch that doesn't show up in
public research. Their input here is genuine signal.

Wait for a reply. If they confirm — proceed. If they redirect —
"actually I think their real moat is their founding team's network in
[sector]" — incorporate it into the Dunford analysis.

**Slack version (async, 1 question only):**
> "Running positioning analysis on [Company]. Any specific moat claim
> from their pitch you want me to stress-test?"

**Skip entirely if:**
- No specific positioning concern has been raised
- vc-competitive-intelligence has already mapped the competitive alternatives
- The positioning question is clearly derivable from research alone

---

## Honesty Protocol

- No aspirational positioning. Assess what the company IS today, not
  what they plan to become. A roadmap feature is not a moat.
- Challenge "we're unique." The Onliness Test must be genuinely
  convincing. If it reads like marketing, surface that directly.
- Feature advantages are temporary. If the only differentiation is
  a feature that competitors can copy in 6 months, say so.
- Category creation is expensive. Most companies can't afford to
  educate a market. Flag this risk if they're attempting it.
- Incumbent risk is real. A well-funded incumbent entering a subcategory
  can erase a startup's position quickly. Model this explicitly.
