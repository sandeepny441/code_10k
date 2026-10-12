# 03 · Step 2: Transformer Encoder

## 1. Where we are

Each token vector now has the right width, but each one still only "knows" about itself (at least as far as the head is concerned). The encoder adds position information and lets every token borrow information from every other token, so that the average taken in step 3 is an average of tokens that already know their context.

```
X (n × d_m) ──► [ + positions ] ──► [ attention + feed-forward ] × L ──► X' (n × d_m)
```

## 2. The formulas, symbol by symbol

**Positions.** $\mathbf{x}_i \leftarrow \mathbf{x}_i + \mathbf{pos}_i$, with one learned vector per position.

**Self-attention (one head).** For every token compute three vectors with learned matrices:

$$\mathbf{q}_i = \mathbf{x}_i\mathbf{W}_Q, \qquad \mathbf{k}_i = \mathbf{x}_i\mathbf{W}_K, \qquad \mathbf{v}_i = \mathbf{x}_i\mathbf{W}_V$$

| Vector | Role, in words |
|---|---|
| query $\mathbf{q}_i$ | "What am I looking for?" (unrelated to the *search* query) |
| key $\mathbf{k}_j$ | "What do I contain?" |
| value $\mathbf{v}_j$ | "What will I hand over if you pick me?" |

Score, weight, and output for token $i$:

$$\text{score}_{ij} = \frac{\mathbf{q}_i \cdot \mathbf{k}_j}{\sqrt{d_k}}, \qquad a_{ij} = \mathrm{softmax}_j(\text{score}_{ij}), \qquad \mathbf{x}'_i = \sum_j a_{ij}\,\mathbf{v}_j$$

Each row of weights $a_{i\cdot}$ adds up to 1, so each output is a weighted average of the values.

## 3. Shapes: toy vs. real

| | Toy | Paper |
|---|---|---|
| Width $d_m$ | 2 | 1,024 |
| Heads | 1 | 8 (each works in $1024/8 = 128$ dimensions, results are joined) |
| Layers $L$ | 1 | 2 |
| Positions | zero | learned, **initialized to zero**, up to 128 |
| Feed-forward | skipped | $1024 \to 4096 \to 1024$ per token |
| Normalization | skipped | pre-norm LayerNorm |
| Parameters per layer | — | about 12.6M |

## 4. The worked numbers

The worked example skipped computing attention and simply **assumed** these weights:

| | from cat | from food |
|---|---|---|
| cat borrows | 0.75 | 0.25 |
| food borrows | 0.25 | 0.75 |

With values equal to the inputs ($\mathbf{v} = \mathbf{x}$):

- $\mathbf{x}'_{\text{cat}} = 0.75[3,2] + 0.25[1,2] = [2.25, 1.5] + [0.25, 0.5] = [2.5, 2]$
- $\mathbf{x}'_{\text{food}} = 0.25[3,2] + 0.75[1,2] = [0.75, 0.5] + [0.75, 1.5] = [1.5, 2]$

## 5. Going deeper

### 5a. Computing the attention weights for real

Take $\mathbf{W}_Q = \mathbf{W}_K = 0.5\,\mathbf{I}$ and $\mathbf{W}_V = \mathbf{I}$, with $d_k = 2$, so $\sqrt{d_k} = 1.414$.

| Token | $\mathbf{q} = \mathbf{k} = 0.5\,\mathbf{x}$ | $\mathbf{v}$ |
|---|---|---|
| cat | $[1.5, 1]$ | $[3, 2]$ |
| food | $[0.5, 1]$ | $[1, 2]$ |

Scores:

| | key cat | key food |
|---|---|---|
| query cat | $(2.25 + 1)/1.414 = 2.298$ | $(0.75 + 1)/1.414 = 1.237$ |
| query food | $(0.75 + 1)/1.414 = 1.237$ | $(0.25 + 1)/1.414 = 0.884$ |

Softmax each row (two-item shortcut $1/(1+e^{b-a})$):

| | from cat | from food |
|---|---|---|
| cat | $1/(1 + e^{-1.061}) = 0.743$ | $0.257$ |
| food | $1/(1 + e^{-0.353}) = 0.587$ | $0.413$ |

Outputs:

- $\mathbf{x}'_{\text{cat}} = 0.743[3,2] + 0.257[1,2] = [2.486, 2]$
- $\mathbf{x}'_{\text{food}} = 0.587[3,2] + 0.413[1,2] = [2.175, 2]$

Two things to notice:

1. The "cat" row came out close to the assumed 75/25. It needs a score gap of $\log 3 = 1.099$ to be exactly 75/25; we got 1.061.
2. **"food" borrows more from "cat" than from itself.** Attention is not symmetric. The "cat" key $[1.5, 1]$ is longer than the "food" key, so it produces bigger dot products with *every* query. Long vectors tend to attract attention.

### 5b. A surprise: symmetric attention doesn't change the average

Pool the worked example's outputs: $([2.5,2] + [1.5,2])/2 = [2, 2]$. Pool the inputs *without* the encoder: $([3,2] + [1,2])/2 = [2, 2]$. **The same.**

Why: the pooled vector equals $\frac{1}{n}\sum_j (\text{column sum}_j) \cdot \mathbf{v}_j$. In the worked example each column sums to $0.75 + 0.25 = 1$, so every token keeps an equal share. In 5a the columns sum to $1.330$ and $0.670$, so "cat" gets more weight: pooled $= [2.330, 2]$, a genuinely different vector.

Lesson: attention matters for the final vector because it can **re-weight** tokens (and because real layers add the non-linear feed-forward part), not merely because it "mixes" them.

### 5c. What the real layer adds

A real pre-norm layer computes $\mathbf{x} + \mathrm{Attn}(\mathrm{LN}(\mathbf{x}))$, then $\mathbf{x} + \mathrm{FFN}(\mathrm{LN}(\mathbf{x}))$. The "$\mathbf{x} +$" (a **residual connection**) keeps the original vector and adds the borrowed information on top. Without LayerNorm, the 5a residual would be $[3,2] + [2.486, 2] = [5.486, 4]$ for "cat". The residual path is also why training can start gently: early on, the layer can act almost like "do nothing".

### 5d. Why positions matter

Attention treats its inputs as a set: swap "cat" and "food" and each output stays the same, just in swapped order, so the mean-pooled result doesn't change at all. Position vectors are the only way the head can tell "cat food" from "food cat". The paper starts them at zero and lets training decide how much order matters.

## 6. Common mistakes

- Confusing the attention "query" with the search query.
- Forgetting $\sqrt{d_k}$. Without it, scores in 128-dimensional heads get huge and softmax puts almost 100% on one token.
- Assuming attention weights are symmetric.

## 7. Check yourself

1. If both tokens attend 50/50 to each other, what are the outputs (with $\mathbf{v} = \mathbf{x}$)?
2. For 5a, what does "food" get if its weights were 0.9 from cat and 0.1 from itself?
3. Why does the worked example's pooled vector not change with the encoder?

---
**Answers.** 1. Both become $[2, 2]$. 2. $0.9[3,2] + 0.1[1,2] = [2.8, 2]$. 3. Each column of its attention weights sums to 1, so every token keeps an equal total share in the average.
