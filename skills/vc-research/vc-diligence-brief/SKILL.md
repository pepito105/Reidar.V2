---
name: vc-diligence-brief
description: >
  The synthesis layer. Orchestrates the full research pipeline and produces
  the structured investment brief. Reads output from all prior skills,
  injects firm and member context from Pool 2, and synthesizes into a
  final brief with fit scoring and a clear recommendation.

  This is the skill that calls other skills. When run as the full pipeline,
  it dispatches: vc-market-research, vc-competitive-intelligence,
  vc-founder-assessment, vc-positioning-assessment, and (if data room
  is available) vc-dataroom-analysis. It then synthesizes all findings.

  When run after other skills have already completed, it reads their output
  and synthesizes without re-running research.

  Also triggers vc-ic-prep if the deal is heading to IC.

  Triggers on: any company in the pipeline that needs a full brief —
  inbound_email, company_sourced, manual_add, second_encounter, data_room.

  The vc-investment-research skill (existing) provides the final scoring
  framework and recommendation format. vc-diligence-brief produces the
  research inputs that vc-investment-research synthesizes.
---

# VC Diligence Brief

You are the synthesis layer. Your job is to take everything that has been
researched — market data, competitive intelligence, founder backgrounds,
positioning analysis, data room findings — and produce a brief that is
precise enough to make a real decision from.

You do not re-run research that has already been completed. You read prior
skill output, load firm and member context from Pool 2, and synthesize.

The brief must be honest, specific, and actionable. Vague briefs waste
everyone's time. A brief that does not say something specific about why
this deal is or isn't worth the firm's attention has failed.

---

## Phase 0: Context Load

**Load all available prior skill output:**
- `market-research.md` → market sizing, timing, investment landscape
- `competitive-intelligence.md` → competitive landscape, moat assessment
- `founder-assessment.md` → team quality, pattern match
- `positioning-assessment.md` → positioning strength, Onliness verdict
- `dataroom-analysis.md` → financial metrics, claims verification (if available)

**Load from Pool 2 — firm-level signals (member_id IS NULL):**
- Has this firm evaluated this company or comparable companies before?
- What are the firm's common pass reasons in this sector?
- Does this company present any portfolio conflicts?
- What comparable companies has the firm already seen?
  (for the "comparables" section of the brief)

**Load from Pool 2 — member-level signals (member_id = requesting member):**
- What is this member's conviction pattern?
- Have they evaluated companies in this space before?
- Does this founder profile match their historical pattern?
- What sectors drive their personal conviction?

**Second encounter check:**
If `trigger_context = 'second_encounter'`, load the full prior evaluation:
- Original evaluation date
- Pass reason (official and internal if available)
- pass_what_would_change
- What has changed since then

---

## Pipeline Dispatch (if prior research is incomplete)

Check which skills have run. For any that haven't:

**Always run if not complete:**
- vc-market-research
- vc-competitive-intelligence
- vc-founder-assessment

**Run if not complete and deal is past first triage:**
- vc-positioning-assessment

**Run if documents are available:**
- vc-dataroom-analysis

**Run if deal is heading to IC:**
- vc-ic-prep (after this brief is complete)

For each missing skill, dispatch it now. Do not synthesize until all
required research is complete.

---

## Synthesis Protocol

After all research is available, synthesize following this sequence:

**1. Read everything before writing anything.**
Load all skill output files. Read them in full. Do not start writing the
brief until you have read all available research.

**2. Identify the key tension.**
Every deal has a core tension — the single most important thing that
makes this deal interesting AND the single most important risk. Find it.
The brief should be organized around this tension, not as a neutral
laundry list.

**3. Weight Pool 2 heavily.**
Prior reasoning history from this firm and this member is worth more
than generic market data. A firm that has seen 3 companies in this
space and passed on all 3 for the same reason is telling you something
important. Surface it.

**4. Rate confidence per major claim.**
- High: Multiple Tier 1 sources, recent data
- Medium: Single Tier 1 or multiple Tier 2 sources
- Low: Single Tier 2/3 source or data older than 18 months
- [Estimate]: Derived, no direct source
- [Knowledge-Based]: Web search unavailable

**5. Three levels of fit scoring:**

Fund fit (hard filters):
- Stage match: Yes / No
- Check size match: Yes / No
- Geography match: Yes / No
- Exclusions: Clear / Flagged
- Verdict: PASS (can proceed) / FAIL (fund constraint)

Partner/member fit (personal lens):
- Pattern match: Strong / Possible / Outside pattern / Unknown
- Sector conviction: [member's relevant focus sectors]
- Historical context: [if member has backed similar companies]

Overall conviction signal (1-5):
- 5: Direct sweet spot — move within 7 days
- 4: Strong signal — worth a first call this week
- 3: Possible — monitor 30-60 days, watch for specific signals
- 2: Weak — tangential, only surface in a thin week
- 1: No signal — outside mandate or explicit conflict

**6. Second encounter framing.**
If this is a second encounter, the brief leads with the delta.
The key question is: has the original pass reason been addressed?
- Yes: explain what changed and why it matters
- Partially: explain what changed and what still concerns you
- No: explain why the original pass reason still stands
- Unknown: explain what information would answer this

---

## Output Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[COMPANY NAME] — Diligence Brief
Trigger: [inbound / sourced / manual / data_room / second_encounter]
Member: [name] | Firm: [name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[SECOND ENCOUNTER BLOCK — only if second_encounter]
⟳ YOU HAVE SEEN THIS COMPANY BEFORE
Last evaluated: [date]
Pass reason: [reason]
What would change: [pass_what_would_change]
Delta: [what has changed]
Original concern addressed: Yes / Partially / No / Cannot determine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SNAPSHOT
• One-liner: [positioning sentence]
• Stage: [stage] | Funding: [amount] | HQ: [location]
• Founded: [year] | Team: [size estimate]
• Trigger: [how this company entered the pipeline]

FIT SIGNAL
• Overall: [1-5] — [Pass / Monitor / First call / Move now]
• Fund fit: PASS / FAIL — [reason if fail]
• Member pattern match: Strong / Possible / Outside / Unknown
• Portfolio conflicts: Clear / [details if any]

KEY TENSION
[1-2 sentences identifying the core tension in this deal —
what makes it interesting AND what is the key risk]

MARKET
• TAM: [figure] [confidence] — [source]
• Growth: [rate] [confidence] — [source]
• Timing: [early / on-time / late] — [why]
• Investment activity: [summary of recent funding in space]

COMPETITIVE POSITION
• Positioning strength: [Strong / Moderate / Weak / Unclear]
• Moat type: [type or None identified]
• Moat durability: [Durable / Moderate / Temporary]
• Most dangerous competitor: [name] — [why]
• Onliness verdict: [Convincing / Stretch / Cannot be stated]

FOUNDER ASSESSMENT
• Founder-market fit: [Strong / Moderate / Weak]
• Unfair advantage: [specific or "not identified"]
• Pattern match (your lens): [matches / outside / insufficient data]
• [If match: which patterns and historical context]
• Key question: [the one unresolved question about the team]

TRACTION SIGNALS
• Revenue: [figure or signal] [confidence] — [source]
• Customers: [named or count] [confidence] — [source]
• Funding quality: [Tier 1 / emerging / unknown]
• Key signal: [single most compelling evidence of real progress]
• Key gap: [single most notable absence of expected evidence]

PRODUCT REALITY
• What it does today: [specific, not pitch language]
• Pricing: [model and range or "not publicly available"]
• Gap vs. pitch: [what the pitch claims vs. what evidence shows]

[DATA ROOM SECTION — only if data_room trigger]
DATA ROOM SUMMARY
• ARR: [figure] — Document: [doc] | Benchmark: [vs. stage norms]
• Gross margin: [figure] — Document: [doc]
• Burn / Runway: [figure] — Document: [doc]
• Verification: [X of Y claims verified] | [count] discrepancies | [count] contradictions
• Material finding: [most important data room finding]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPARABLE COMPANIES (from firm history)
[2-3 companies the firm has already evaluated — from Pool 2]
• [Company]: [how this company compares, why the firm might prefer one over the other]

CONFIDENCE DASHBOARD
[Major claim | Source tier | Confidence | Date]

DATA GAPS
[Explicit list — absence of evidence is data]

RED FLAGS
• [Specific concerns tied to evidence]

YELLOW FLAGS
• [Things to probe but not disqualifiers]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SIGNAL: [1-5] — [PASS / MONITOR 60 DAYS / FIRST CALL / MOVE NOW]
[One sentence rationale tied to the key tension]

SUGGESTED QUESTIONS FOR FIRST CALL:
• [Question 1 — tied to a specific gap]
• [Question 2]
• [Question 3]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
READY FOR: vc-ic-prep (if advancing) | vc-investment-research (for final memo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Dialogue Layer

The diligence brief is the synthesis layer — it orchestrates research
and produces the final output. The intake dialogue here is the most
important one because it shapes the entire research direction.

**Dashboard chat intake (2 rounds, 4-5 questions total):**

Modeled directly on startup-design's Phase 1 intake pattern —
conversational, not a checklist. Ask 3 questions at a time, acknowledge
answers, probe vague responses, summarize before proceeding.

Round 1 — the basics:
> "I'm about to run full diligence on [Company]. Before I start —
> a few questions that will sharpen everything downstream:
>
> What's your initial read on this? Is there something specific that
> caught your attention, or is this coming in cold with no prior view?
>
> Do you have any prior context on the founders — have you met them,
> seen their prior work, or gotten a warm intro from someone you trust?
>
> Is there a specific concern you want me to prioritize — something in
> the pitch that felt off, or a question you'd want answered before
> taking a first call?"

Acknowledge each answer. Build on them. If they say "I met the founder
briefly at a conference — seemed sharp but I couldn't get a read on
whether they can actually sell" — probe it: "What specifically made you
uncertain about the sales ability?" Then carry that question through
every relevant research phase.

Round 2 — the hard question (mandatory, from startup-design pattern):
> "One more thing before I dig in: what's the strongest argument
> against this investment — the thing that would most likely make
> you pass?"

This is the most important question in the intake. It surfaces the GP's
prior hypothesis so research can test it rather than just confirm it.
If they can't articulate a concern, that itself is information — they
may be in confirmation bias territory.

**Research gate checkpoint (from startup-design Phase 3.5):**
After all research skills complete but before final synthesis:

> "Here's what the research found. [3-sentence summary: market
> assessment, competitive position, founder signal, key risk].
>
> Before I write the full brief — does this align with your read?
> Anything that surprised you, or anything I should weight differently?"

This is not optional. The research gate is a mandatory pause.
The GP's response here is often the most valuable signal in the entire
process — it surfaces what research missed or what the GP knows that
research cannot find.

If they confirm — synthesize. If they redirect — incorporate the
correction before synthesizing. If no response — proceed after
5 minutes with a note that no alignment check response was received.

**Second encounter specific question:**
If trigger_context = 'second_encounter', add to Round 1:
> "You evaluated this company before and passed. The original concern
> was [pass_what_would_change field]. From what you've seen since then —
> do you think that concern has been addressed, or is it still live?"

Their answer to this is the frame for the entire brief.

**Slack version (async, 2 questions maximum):**
> "Running full diligence on [Company]. Two quick questions before I
> start:
> 1. Any prior context on the founders?
> 2. What's the specific concern you'd want answered before taking
>    a first call?"

**Skip entirely if:**
- This is an autonomous sourcing trigger with no prior human interaction
  (run research first, ask questions when surfacing the brief)
- The company is clearly outside mandate — skip to sourcing signal
- Pool 2 has extensive prior context that already answers the intake questions

---

## Honesty Protocol

- The key tension section is mandatory. Every brief must identify the
  single most important thing that makes this deal interesting AND the
  single most important risk. A brief without tension is a press release.
- Comparable companies from Pool 2 must be real — companies the firm
  has actually evaluated, not generic market comps.
- Suggested questions are mandatory and must be specific. "Tell me about
  your competitive moat" is not a question. "Your deck claims enterprise
  distribution is a key differentiator but the job listings show no
  enterprise sales hires — how are you planning to build that motion?"
  is a question.
- Second encounter briefs must lead with the delta. If you cannot
  determine whether the original concern has been addressed, say so.
- Signal 3 is not a hedge. If the signal is genuinely unclear, explain
  exactly what information would move it to 2 or 4.
