# 10 · Loss 3: Rank Distillation ("order the documents the way your teacher does")

## 1. Where we are

Search quality is about the **order** of returned documents. This loss ignores the batch grid and looks at documents: take the teacher's top-$K$ for a query, and make the student's preferences among them match the teacher's.

## 2. The formula, symbol by symbol

$$\mathcal{L}_{\text{rank}} = \mathrm{KL}\big(\mathrm{softmax}(\mathbf{s}/\tau_r)\ \Vert\ \mathrm{softmax}(\hat{\mathbf{s}}/\tau_r)\big)$$

| Piece | Meaning |
|---|---|
| $s_k = \mathbf{y}\cdot\mathbf{d}_k$ | Teacher score for document $k$ |
| $\hat{s}_k = f(\mathbf{H})\cdot\mathbf{d}_k$ | Student score for the same document |
| $/\tau_r$, softmax | Turn each score list into "how much attention each document gets" |
| $P$ (teacher), $Q$ (student) | The two distributions |
| $\mathrm{KL}(P\Vert Q) = \sum_k P_k \log(P_k/Q_k)$ | How much $Q$ differs from $P$, weighted by where the teacher cares |

Averaged over all queries in the batch.

## 3. Shapes: toy vs. real

| | Toy | Paper |
|---|---|---|
| Documents per query $K$ | 3 | 128 (256 tested, no gain) |
| $\tau_r$ | 0.2 | 0.05 |
| Weight | 1 | $\lambda_r = 0.5$ |

## 4. The worked numbers (query 1, "cat food")

| | Cat behavior $\mathbf{d}_1$ | Pizza $\mathbf{d}_2$ | Dry cat food $\mathbf{d}_3$ |
|---|---|---|---|
| Teacher $s$ | 0.8 | 0.6 | 0.96 |
| Student $\hat{s}$ | 0.6 | 0.8 | 1.0 |
| $s/0.2$ | 4 | 3 | 4.8 |
| $\hat{s}/0.2$ | 3 | 4 | 5 |
| $P$ | 0.278 | 0.102 | 0.619 |
| $Q$ | 0.090 | 0.245 | 0.665 |
| $P\log(P/Q)$ | $+0.314$ | $-0.089$ | $-0.044$ |

$$\mathcal{L}_{\text{rank}} = 0.314 - 0.089 - 0.044 = 0.181$$

## 5. Going deeper

### 5a. The gradient tells each document score where to go

For KL with softmax, the gradient with respect to the student's scores is

$$\frac{\partial \mathcal{L}_{\text{rank}}}{\partial \hat{s}_k} = \frac{Q_k - P_k}{\tau_r}$$

| Document | $Q - P$ | $\div 0.2$ | Descent will… |
|---|---|---|---|
| Cat behavior | $-0.188$ | $-0.94$ | **raise** its score strongly |
| Pizza | $+0.142$ | $+0.71$ | **lower** its score |
| Dry cat food | $+0.046$ | $+0.23$ | lower it slightly (student over-confident) |

These pushes then flow back through $\hat{s}_k = f(\mathbf{H})\cdot\mathbf{d}_k$ into the student vector. The combined push is $-0.94\,\mathbf{d}_1 + 0.71\,\mathbf{d}_2 + 0.23\,\mathbf{d}_3 = [-0.94 + 0.14,\ 0.71 + 0.18] = [-0.80, 0.89]$. Descent moves against it: more cat, less food. Same direction alignment wanted, but for a different reason.

### 5b. Why KL(teacher ‖ student) and not the other way

$P$ is the weight on each term. Documents the **teacher** cares about (high $P_k$) dominate the loss; documents the teacher thinks are irrelevant barely count. The student is punished most for ignoring what the teacher considers important. That is the right priority for search.

### 5c. Why rank distillation alone collapses (a demonstration)

Rank loss only sees scores **among the $K$ chosen documents**. Two facts make that dangerous:

1. Softmax ignores shifts: adding a constant to every score changes nothing (file 01).
2. With $K$ documents in $d$ dimensions, directions the $K$ documents don't "see" are unconstrained. With $K = 128$ in $d = 1024$, that is at least ~900 free directions per query.

Toy demonstration in 3D. Add a third dimension, "fish-ness". The three documents keep their old coordinates with 0 fish. Add a fourth document **not** in the teacher's top-3: "Aquarium fish food", $[0, 0.6, 0.8]$. The teacher is $\mathbf{y} = [0.8, 0.6, 0]$.

Consider a weird student: $\mathbf{u} = [0.48, 0.36, 0.8]$ (length 1). It is 60% the teacher plus a big fish component.

| | Teacher $\mathbf{y}$ | Original student $[0.6, 0.8, 0]$ | Weird student $\mathbf{u}$ |
|---|---|---|---|
| Cat behavior | 0.8 | 0.6 | 0.48 |
| Pizza | 0.6 | 0.8 | 0.36 |
| Dry cat food | 0.96 | 1.0 | 0.576 |
| Order among top-3 | food, cat, pizza | food, **pizza, cat** ✗ | food, cat, pizza ✓ |
| $\mathcal{L}_{\text{rank}}$ | — | 0.181 | **0.030** (much "better") |
| Cosine with teacher | 1 | 0.96 | 0.60 |
| Aquarium fish food (outside top-3) | 0.36 | 0.48 | **0.856, ranked #1** ✗ |

The weird student gets the teacher's order right and a far lower rank loss, yet in the full index it returns a fish-tank document first. Rank loss never saw that document, so it never objected. Alignment would: its loss for this student is $1 - 0.60 = 0.40$, ten times the original student's.

This is the paper's explanation in numbers: rank distillation has **no anchor** in the space. It refines local order *after* alignment has put the vector in the right place. Alone: Recall@10 = 0.001.

### 5d. Why top-256 didn't help

Beyond the first hundred or so, the teacher's scores for extra documents are low, so their $P_k$ are tiny and they add almost nothing to the loss. The ranking signal saturates.

## 6. Common mistakes

- Using the student's top-$K$ instead of the teacher's. The paper uses the **teacher's** candidates.
- Forgetting that individual KL terms can be negative; only the total is guaranteed $\geq 0$.
- Giving it too much weight: $\lambda_r = 1.0$ dropped Recall@10 to 0.516.

## 7. Check yourself

1. If the student's scores were $[0.8, 0.6, 0.96]$, what would the rank loss be?
2. If the student's scores were the teacher's plus 0.1 on every document, what would the rank loss be?
3. Why doesn't answer 2 mean the student is perfect?

---
**Answers.** 1. 0: identical distributions. 2. Also 0: softmax ignores a constant shift. 3. The scores on documents *outside* the top-$K$ might be completely wrong, as in 5c.
