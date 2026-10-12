# Information Extraction — Companion Notes

Supporting material for the *Five Problems, One Deep Dive* session. The deck is the talk;
this is the thing you read before presenting, and the thing you hand to anyone who asks
"where did that number come from."

Everything here is reproducible. Where a figure is illustrative rather than measured, it
says so.

---

## Part 0 — How to use this

- **Slides 2–7** cover the five problems. Sections 1–5 below give you the extra depth for
  questions from the floor.
- **Slides 8–16** are the deep dive. Sections 6–11 are the substance, including the math.
- **Section 12** is the objection handling. Read it last, twice.

---

# Part 1 — The five problems

## 1. The model can only read what we handed it

**Plain version.** We run OCR, then send text to the model. If OCR turned a table into a
jumble of words, no prompt recovers it.

**Technical name.** Input fidelity / layout loss.

**Why it happens.** A PDF stores glyphs at coordinates. There is no object in the file
saying "this is a table cell." Column boundaries, row membership and header association
are all inferred from spatial position. Any step that discards position — naive text
extraction, most OCR defaults — discards the meaning with it.

**The 30-second diagnostic.** Log the exact string passed to the prompt. Print it. Try to
reconstruct the table by eye. If you can't, the model can't either, and every hour spent
on the prompt is wasted.

**What actually fixes it.**
- Detect born-digital PDFs and use the embedded text layer; running OCR on a digital PDF
  throws away certainty you already had
- Layout-preserving extraction (keep coordinates, or emit Markdown/HTML with real table
  structure)
- Table structure recognition as its own pipeline stage, before extraction

---

## 2. Tables don't survive the trip

**Plain version.** Columns are a visual illusion. Nothing in the file says which number
belongs to which row.

**Technical name.** Table structure recognition.

**The four hard cases, in increasing order of pain.**

| Case | Why it breaks |
|---|---|
| Borderless tables | No ruling lines to anchor column detection |
| Merged cells | One label owns N rows; flattening duplicates or drops it |
| Nested headers | Two header rows combine into one logical column name |
| Page-spanning | Header on page 3, rows on page 4, no association |

**Known baseline.** Simple bordered tables with clear boundaries extract at roughly
95–99% with modern tools. The number collapses on the four cases above — which is why
"our table extraction is 97% accurate" is almost always a statement about the easy subset.

---

## 3. We never agreed what the field means

**Plain version.** Which date is *the* date? Is the tier rate on the units above the
threshold, or on all of them?

**Technical name.** Schema ambiguity. It is a specification defect, not a model defect.

### Worked example — marginal vs retroactive

Setup: 10,000 units at $10 each. Gross volume = $100,000.

| Tier | Volume band | Rate |
|---|---|---|
| 1 | 0 – 2,000 | 2% |
| 2 | 2,001 – 5,000 | 4% |
| 3 | 5,001 + | 6% |

**Marginal reading** — each band earns its own rate on the units inside it:

```
Tier 1:  2,000 units × $10 × 2%  =  $  400
Tier 2:  3,000 units × $10 × 4%  =  $1,200
Tier 3:  5,000 units × $10 × 6%  =  $3,000
                                    -------
                                    $4,600
```

**Retroactive reading** — hitting the top band applies its rate to every unit:

```
10,000 units × $10 × 6%          =  $6,000
```

**Difference: $1,400, or 30%.** One undefined word.

The document often doesn't disambiguate. If our schema doesn't either, the model picks —
and not necessarily the same way on two runs of the same document.

**What fixes it.** Field definitions, not field names. One rule plus one counterexample
per field:

```jsonc
"tier_rate_basis": {
  "enum": ["marginal", "retroactive"],
  "rule": "Marginal unless the document states the rate applies to all units, "
          "cumulative volume, or uses the phrase 'retroactive to first unit'.",
  "counterexample": "'6% on all purchases once 5,001 units is reached' -> retroactive, "
                    "NOT marginal, despite appearing in a tiered table."
}
```

---

## 4. Rows go missing and nothing tells us

**Plain version.** Six tiers in the document, five in the JSON. No error. Valid output.

**Technical name.** Completeness / recall failure.

This is the deep dive. Part 2 below.

---

## 5. Wrong answers look exactly like right answers

**Plain version.** A parser that fails returns nothing. A model that fails returns a
plausible number in correct JSON.

**Technical name.** Calibration.

**The key asymmetry.** A hallucinated field value is worse in production than a blank one,
because it passes downstream validation without triggering review. Blank fails loudly.
Wrong ships.

**Why the obvious fix doesn't work.** Token log-probabilities measure fluency under the
model's own distribution, not whether the value matches the page. They are not
P(correct), and empirically they are poorly calibrated for extraction.

**What the field is actually building.** Conformal prediction — calibrate an acceptance
threshold on held-out data and get a coverage guarantee under an exchangeability
assumption, without needing the underlying scores to mean anything. Sampling-based
variants exist for API-only models with no logit access.

Worth knowing but **out of scope for this session**: it needs a labelled eval set we
don't have yet. That's why we start with completeness.

---

# Part 2 — Deep dive: completeness

## 6. Why this one

### The asymmetry argument

A **wrong value** has an advocate. Finance notices the rebate is off. A customer
complains. Someone who knows the account says "that's not right." The error generates a
signal.

A **missing row** produces a confident, complete-looking answer. There is no gap on the
screen. Nobody knows to look. The error has no advocate.

Same underlying error rate, radically different detection probability. That asymmetry is
the entire argument for instrumenting completeness separately.

### External corroboration

Recent benchmark work on schema-guided enterprise extraction found that commercial vision
models perform well on short documents but often truncate record lists on long ones. Our
rebate tier tables *are* record lists. This is a measured, published phenomenon, not a
hunch.

---

## 7. Three mechanisms

They look identical in the output and have completely different fixes. Diagnosing which
one you have is most of the work.

### 7a. Page-break context loss

The table runs onto page 4. Page 4's rows have no header above them. The model either
drops them or assigns them to the wrong columns.

*Signature:* misses cluster at page boundaries. Plot missing-row position against page
position and you'll see it immediately.

*Fix:* per-page extraction with forced header carry-forward — explicitly prepend the
header row when processing continuation pages.

### 7b. Chunk boundary destruction

A naive chunker splits a record across chunks. Each half is processed independently and
neither sees the complete record. The result is partial extractions that look complete.

*Signature:* misses cluster at chunk boundaries, which are at fixed token offsets and
therefore at *arbitrary* document positions. Misses look random until you overlay chunk
offsets.

*Fix:* chunk on document structure (table regions, sections), never on token count.

### 7c. Generation truncation

The model is emitting a long JSON array and stops early. This is **not** a context-length
limit — it is degradation in long structured generation.

*Signature:* misses are always at the *tail* of the list. If your missing rows are
disproportionately the last ones, this is your mechanism.

*Fix:* bounded batches. Extract rows 1–20, then 21–40, with explicit continuation. Or
extract a row count first, then extract rows, then assert.

### Diagnostic summary

| Where the misses cluster | Mechanism | Fix |
|---|---|---|
| Page boundaries | Page-break context loss | Header carry-forward |
| Chunk offsets | Chunk boundary destruction | Structure-aware chunking |
| End of list | Generation truncation | Bounded batch extraction |

---

## 8. Layer 1 — Structural invariants

Deterministic, cheap, no labels, no model changes. Ship this first. For rebate tables the
invariants are unusually strong.

### 8a. Tier contiguity

Volume bands must tile the number line with no gaps and no overlaps.

```python
def check_contiguity(tiers):
    """tiers: list of dicts with 'lower' and 'upper' (upper=None for open-ended)."""
    t = sorted(tiers, key=lambda x: x["lower"])
    problems = []
    for a, b in zip(t, t[1:]):
        if a["upper"] is None:
            problems.append(("open_band_not_last", a))
            continue
        gap = b["lower"] - a["upper"]
        if gap > 1:
            problems.append(("gap", a["upper"], b["lower"]))   # a row is missing
        elif gap < 1:
            problems.append(("overlap", a["upper"], b["lower"]))
    return problems
```

A gap between tier 3 (ends 5,000) and tier 5 (starts 8,000) is proof a row was dropped.
This single check catches most page-break losses.

### 8b. Control totals

Documents frequently state their own cardinality: "6 tiers," "Page 3 of 7," a stated
subtotal. Parse and compare. Free ground truth, already on the page.

### 8c. Region coverage

Every table region the layout detector found must yield at least one output row. A
detected region producing zero rows is a silent failure made loud.

```python
assert all(len(rows_for_region(r)) > 0 for r in detected_table_regions)
```

### 8d. Edge adjacency

If the last extracted row sits within N points of a page bottom, and the following page
begins with numeric content, flag for a second look.

### 8e. Monotonicity (soft)

Rebate rates rarely decrease as volume increases. A decrease is not proof of an error,
but it is worth a flag.

**Expected yield.** These catch a large share of misses at essentially zero marginal cost
and zero labelling effort. This is the highest value-per-engineering-hour work available
to us.

---

## 9. Layer 2 — Synthetic ground truth

### The problem with labelling

Hand-labelling long tables is miserable, slow and error-prone. Annotators disagree.
It's the reason most teams never measure completeness at all.

### The trick

**Generate the values before the document exists.**

This is the methodology used by recent benchmark work: for synthetic long lists, values
are generated before rendering the document, so completeness can be scored at large row
counts.

### Pipeline

```
1. GENERATE   Pick tier boundaries and rates in code. You now have exact truth.
2. RENDER     Emit a PDF. Also emit a degraded variant (rasterize, add noise, skew 0.5°)
              so you test the OCR path, not just the text-layer path.
3. EXTRACT    Run the real production pipeline. No special casing.
4. COMPARE    Match extracted rows to generated rows. Compute recall.
```

### Sketch

```python
import random

def make_tiers(n, max_vol=200_000):
    cuts = sorted(random.sample(range(1_000, max_vol), n - 1))
    bounds = list(zip([0] + cuts, cuts + [None]))
    rate = 1.5
    tiers = []
    for lo, hi in bounds:
        rate += random.uniform(0.3, 1.2)          # monotone increasing
        tiers.append({"lower": lo, "upper": hi, "rate": round(rate, 2)})
    return tiers

def evaluate(n_rows, n_docs=40):
    hits = total = 0
    for _ in range(n_docs):
        truth = make_tiers(n_rows)
        pdf   = render_rebate_pdf(truth)          # your renderer
        got   = production_pipeline(pdf)          # your real pipeline
        hits  += len(match_rows(truth, got))
        total += len(truth)
    return hits / total                            # row recall
```

### The chart to produce

Sweep `n_rows` over `[5, 10, 20, 30, 40, 60, 80]` and plot row recall. You will almost
certainly see a knee — near-perfect recall on short tables, degradation on long ones.

**That chart is the single most persuasive artifact in the session,** because it is our
own data and it takes about a day to produce.

*Deck note:* slide 10's curve is illustrative. Replace it with the real one before
presenting if you can.

### Matching rows is its own small problem

You cannot compute recall until you decide when an extracted row "is" a generated row.
Extracted values are approximate; ordering may differ. Use a cost matrix and solve the
assignment problem:

```python
import numpy as np
from scipy.optimize import linear_sum_assignment

def match_rows(truth, got, tol=0.01):
    C = np.zeros((len(truth), len(got)))
    for i, t in enumerate(truth):
        for j, g in enumerate(got):
            C[i, j] = (abs(t["lower"] - g.get("lower", -9e9)) / max(t["lower"], 1)
                       + abs(t["rate"] - g.get("rate", -9e9)) / max(t["rate"], 1))
    ri, ci = linear_sum_assignment(C)
    return [(i, j) for i, j in zip(ri, ci) if C[i, j] < tol]
```

The Hungarian algorithm gives the optimal one-to-one matching. Greedy nearest-neighbour
matching will over-report recall — it can match two truth rows to the same extracted row.

---

## 10. Layer 3 — Capture–recapture

For what Layers 1 and 2 can't see: rows that **no** pass found.

Borrowed from ecology, where you cannot count all the fish in a lake.

### The setup

Run two **independent** extraction passes over the same table.

- $n_A$ = rows found by pass A
- $n_B$ = rows found by pass B
- $m$ = rows found by both

### The estimator

Assume each pass independently detects a row with some probability. The share of pass B's
rows that A also found estimates A's detection rate:

$$\hat{p}_A = \frac{m}{n_B}$$

Pass A found $n_A$ rows at detection rate $\hat p_A$, so the true total is:

$$\hat{N} = \frac{n_A}{\hat{p}_A} = \frac{n_A \cdot n_B}{m}$$

This is the **Lincoln–Petersen estimator**.

### Worked example

Pass A finds 18 tiers. Pass B finds 17. Fifteen match.

$$\hat{N} = \frac{18 \times 17}{15} = \frac{306}{15} = 20.4$$

Distinct rows actually observed:

$$|A \cup B| = n_A + n_B - m = 18 + 17 - 15 = 20$$

So the estimate says **≈ 0.4 rows** exist that neither pass found.

### Chapman correction

Lincoln–Petersen is biased upward on small samples and undefined when $m = 0$. Use:

$$\hat{N}_{\text{Chapman}} = \frac{(n_A+1)(n_B+1)}{m+1} - 1$$

$$= \frac{19 \times 18}{16} - 1 = \frac{342}{16} - 1 = 21.375 - 1 = 20.4$$

Same answer here. On small $m$ it diverges and Chapman is the one to trust.

### Uncertainty — read this before quoting a number

Seber's variance approximation:

$$\widehat{\operatorname{Var}}(\hat{N}) = \frac{(n_A+1)(n_B+1)(n_A-m)(n_B-m)}{(m+1)^2(m+2)}$$

$$= \frac{19 \times 18 \times 3 \times 2}{16^2 \times 17} = \frac{2052}{4352} = 0.472$$

$$\text{SE} = \sqrt{0.472} = 0.69$$

95% interval: $20.4 \pm 1.96 \times 0.69 = [19.0,\ 21.7]$.

**That interval contains 20.** On a *single* table, this analysis cannot tell you a row is
missing. Be honest about this in the room — it's the first thing a statistically literate
person will ask.

The value is in **aggregation**. Across 500 tables:

$$\text{estimated total misses} = \sum_{i=1}^{500} (\hat{N}_i - |A_i \cup B_i|) \approx 500 \times 0.4 = 200 \text{ rows}$$

and the standard error of the *mean* shrinks by $\sqrt{500} \approx 22$, so the aggregate
estimate is tight even though each individual one isn't. **Report it as a fleet-level
metric, never as a per-document judgement.**

### The independence assumption

Lincoln–Petersen assumes the two passes detect rows independently. They don't, quite.

- Two prompts against the same model miss the same rows → $m$ is inflated → $\hat N$ is
  biased **low** → you under-count misses
- The bias is conservative in direction (you never over-claim misses) but it means the
  estimate is a **floor**, not a point estimate

Maximize independence:

| Pair | Independence |
|---|---|
| Two prompts, same model | Poor |
| Same model, page-wise vs whole-document | Moderate |
| Two different model families | Good |
| VLM vs deterministic table parser | Best |

The last pairing is ideal because the failure modes are genuinely unrelated: a table
parser fails on borderless layouts, a VLM fails on long lists.

---

## 11. The economics

### The decision

Is a second extraction pass worth it? Run a second pass when:

$$\Delta d \times p_{\text{miss}} \times C_{\text{error}} > \Delta C_{\text{pass}}$$

where $\Delta d$ is the gain in detection rate, $p_{\text{miss}}$ is the probability a
table has a missing row, $C_{\text{error}}$ is the cost of shipping a wrong rebate, and
$\Delta C_{\text{pass}}$ is the added inference cost.

### Plug in plausible numbers

| Quantity | Value | Source |
|---|---|---|
| $\Delta d$ | 0.48 (0.40 → 0.88) | illustrative |
| $p_{\text{miss}}$ | 0.08 | replace with your recall curve |
| $C_{\text{error}}$ | $400 | replace with finance's number |
| $\Delta C_{\text{pass}}$ | $0.08 / page | ~8.1¢/page is a published reference price |

$$0.48 \times 0.08 \times \$400 = \$15.36 \quad \text{vs} \quad \$0.08$$

**192× return.** The second pass is not a close call.

### Breakeven

Solve for the error cost at which it stops being worth it:

$$C_{\text{error}}^{*} = \frac{\Delta C_{\text{pass}}}{\Delta d \times p_{\text{miss}}}
= \frac{0.08}{0.48 \times 0.08} = \$2.08$$

**If a missed rebate row costs more than about $2, run two passes.** It does.

### Honest note on slide 15

Slide 15 compares cost ratios and favours the selective approach. That is the right
picture when you're optimizing *inference spend in isolation*. Once you put a realistic
price on a wrong rebate, the maths above says always-two wins comfortably. Both framings
are defensible — the selective one if inference budget is the binding constraint, the
always-two one if error cost is. Know which constraint you're actually under before you
present it, and be ready for someone to do this arithmetic out loud.

---

## 12. Objections you will get

**"Can't we just tell the model not to truncate?"**
It isn't a compliance failure, it's degradation in long structured generation. Asking
nicely doesn't fix a capability limit. Bounded batches do.

**"Isn't two passes double the cost?"**
Double the *inference* cost, which is a rounding error against the cost of a wrong
rebate. See section 11.

**"How common is this really?"**
That's precisely what the synthetic recall curve answers, and we can have it in a day.
Bring the number, not the argument.

**"Aren't the structural checks brittle?"**
They're deterministic and auditable, which is the opposite of brittle. When a contiguity
check fires wrongly, you can read exactly why in one line of code. Compare that to
debugging why a model dropped a row.

**"Why not just use a better model?"**
Because the failure is silent. A better model has a lower miss rate and the same zero
detection rate. Detection is the missing capability, not accuracy.

**"We don't have time to build an eval set."**
The synthetic path needs no labelling. It's a renderer and a comparison function.

---

## 13. What we measure

Three numbers. Everything else is commentary.

1. **Row recall, bucketed by table length.** Not document accuracy. Not field accuracy.
   Bucketed, because the average hides the cliff.
2. **Flag rate from structural checks**, and what proportion of flags are real misses
   (precision of the detector).
3. **Estimated misses per table** from capture–recapture, reported at fleet level with a
   confidence interval.

---

## 14. Sources and further reading

- **ExtractBench** (LlamaIndex, Aug 2026) — schema-guided enterprise extraction benchmark,
  370 documents / 4,869 pages / 8 domains / 67 document types. Source of the long-list
  truncation finding, the synthetic-ground-truth methodology, and the grounding metrics.
  arXiv:2607.29677
- **OmniDocBench** — document parsing benchmark; reading-order and footnote error analysis.
  arXiv:2412.07626
- **Conformal Prediction for Risk-Controlled Medical Entity Extraction** (Mar 2026) —
  the calibration material referenced in problem 5; notable for finding that miscalibration
  direction reverses between structured and free-text documents. arXiv:2603.00924
- **Seber, G.A.F.** — *The Estimation of Animal Abundance*. The standard reference for
  capture–recapture estimators and their variance.
- **Chapman, D.G. (1951)** — the small-sample correction.

---

*Figures marked illustrative are placeholders pending our own measurement. Replace before
presenting externally.*
