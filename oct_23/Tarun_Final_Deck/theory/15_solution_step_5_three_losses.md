# 15 · Solution Step 5: Three Losses, Three Kinds of Mistake

## 1. Goal of this step

Define "the student is doing well" precisely enough to train on. One number, the **loss**, must go down when the student gets better.

## 2. What the paper does

It combines three losses, each measuring a different mistake:

| Loss | Question it asks | Plain-words version | Math file |
|---|---|---|---|
| **Alignment** $\mathcal{L}_{\text{align}}$ | Does the student point where its teacher points? | "Copy your teacher." | `math/08` |
| **Contrastive** $\mathcal{L}_{\text{contra}}$ (InfoNCE) | Is the student closer to *its own* teacher than to the other teachers in the batch? | "Don't be confusable with other queries." | `math/09` |
| **Rank distillation** $\mathcal{L}_{\text{rank}}$ | Does the student put the teacher's top documents in the teacher's order? | "Rank documents like your teacher." | `math/10` |

$$\mathcal{L} = \lambda_a \mathcal{L}_{\text{align}} + \lambda_c \mathcal{L}_{\text{contra}} + \lambda_r \mathcal{L}_{\text{rank}}$$

The best setting uses $\lambda_a = \lambda_c = \lambda_r = 0.5$, temperatures $\tau = \tau_r = 0.05$, and the teacher's top $K = 128$ documents for ranking. (`math/11` combines them.)

## 3. Why three and not one

The worked example shows the reason perfectly. For the query "cat food":

- **Alignment says 0.04**, nearly perfect. The student's cosine with its teacher is 0.96.
- **Contrastive says** the "cat toys" student is almost as close to the "cat food" teacher (0.936) as to its own (0.96). The two queries are nearly confusable.
- **Rank says** the student ranks *Pizza recipes* above *Cat behavior guide*, the teacher's second choice. A cosine of 0.96 is not enough to get the order right.

A vector can be *close* to the teacher and still be *wrong in the ways that matter for search*. Each loss catches a different way of being wrong.

| Loss | Kind of signal | Strength | Weakness |
|---|---|---|---|
| Alignment | Absolute: "go to this point" | Strong, stable, always has a clear target | Doesn't care about neighbors or order |
| Contrastive | Relative to other *queries* | Keeps queries separable | Depends on what else is in the batch (only 16 queries) |
| Rank | Relative among *documents* | Directly targets search order | Has no anchor: collapses alone (see below) |

## 4. What the experiments say about them

From the ablation (all at 30 epochs, lr $3 \times 10^{-4}$), Recall@10:

| Setting | R@10 |
|---|---|
| Align only | 0.567 |
| Contrastive only | 0.498 |
| Rank only | **0.001** (collapsed) |
| Align + Contrastive | 0.582 |
| Align + Rank | 0.579 |
| All three | 0.595 |

- Alignment is the backbone.
- Each extra loss helps a bit on top of it; all three together are best.
- Rank distillation alone fails completely. It only compares scores *among* a few documents, so it never tells the vector *where in the space* to be. It can match the teacher's order among those 128 documents while pointing somewhere that retrieves junk from the rest of the index. `math/10` shows this happening with numbers.
- Too much rank weight also hurts ($\lambda_r = 1.0$: 0.516).

## 5. What could go wrong

- **Weights are hand-tuned.** The best $\lambda$s were found by trial on this dataset.
- **Temperature matters.** Too low and training is harsh and unstable; too high and near-ties are ignored (`math/09`).
- **Batch size limits contrastive learning.** With 16 queries per batch, each student only sees 15 "wrong" teachers.
