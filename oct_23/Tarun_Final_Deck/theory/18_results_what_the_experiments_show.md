# 18 · Results, Part 2: What the Experiments Show

## Step 1: The main result

| | Recall@10 | MRR@10 | nDCG@10 | Latency (p50) |
|---|---|---|---|---|
| Baseline (LLM → text → embedder) | 0.637 | 0.329 | 0.402 | 43.5 ms |
| Projection head | 0.607 | 0.293 | 0.367 | 2.0 ms |
| Difference | −3.0 pts | −3.6 pts | −3.5 pts | 21.8× faster |

**Reading it:** the head is a little worse at search and much faster at the encode step. The gap is small but statistically real ($p = 0.0005$).

A note on "97%": the −3.0 is in **percentage points**. As a ratio, the head keeps 0.607 / 0.637 = **95.3%** of the baseline's Recall@10, 89% of its MRR and 91% of its nDCG. The paper's "97%" and "95–97%" figures read like 100 − 3 rather than a ratio. See `19`.

## Step 2: The loss ablation (which losses matter)

All at 30 epochs, lr $3 \times 10^{-4}$:

| Losses used | R@10 | Lesson |
|---|---|---|
| Rank only | 0.001 | Collapses: no anchor in space |
| Contrastive only | 0.498 | Works, but weak alone |
| Align only | 0.567 | The strongest single signal |
| Align + Rank | 0.579 | Rank helps once alignment anchors things |
| Align + Contrastive | 0.582 | Separation helps |
| All three | 0.595 | Best combination |
| All three + long/slow recipe | **0.607** | Best overall |

## Step 3: The training recipe (how to train)

- Learning rate $5 \times 10^{-4}$ collapses; $2 \times 10^{-4}$ with 80 epochs is best.
- 50 epochs at $3 \times 10^{-4}$ is **worse** than 30 epochs at the same rate, a sign of overshooting or overfitting when the rate isn't lowered.
- Going from the standard to the extended recipe (+0.012) gave the paper's largest single gain, larger than adding any one loss on top of the others.

## Step 4: Loss-weight sensitivity

With no contrastive loss ($\lambda_c = 0$):

| Setting | R@10 |
|---|---|
| More alignment ($\lambda_a = 1.0$, $\lambda_r = 0.5$) | 0.591 |
| More rank ($\lambda_a = 0.5$, $\lambda_r = 1.0$) | 0.516 |
| Top-256 instead of top-128 docs | 0.584 |

Leaning on alignment is safe; leaning on rank hurts. Doubling $K$ doesn't help, so the ranking signal saturates at a moderate number of candidates.

## Step 5: Where it fails

- Per-conversation agreement with the baseline averages 84.5%, but failures **cluster**: 48 conversations (with at least 3 triggers each) have recall well below the baseline.
- The paper **hypothesizes** (it doesn't test) that failures involve rare terms, long coreference chains, or domain vocabulary, the "long tail" where the head saw few training examples.
- It also points to the **causal vs. bidirectional** mismatch (file `04`): the head must translate from states that only look backward into a space built by a model that looks both ways.

## Step 6: The takeaway

| Claim | Supported? |
|---|---|
| A small head can stand in for the embedder at search time | Yes: 95% of recall, same index |
| It is much faster at the encode step | Yes: 43.5 → 2.0 ms |
| All three losses contribute | Yes, in this setting |
| Careful optimization matters a lot | Yes |
| Hidden states make search *better* than text (Problem 3) | Not shown: the head is slightly worse than the text pipeline |
