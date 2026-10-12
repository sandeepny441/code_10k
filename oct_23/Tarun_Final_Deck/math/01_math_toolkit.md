# 01 · The Math Toolkit

## 1. Where we are

Every step later uses only the operations on this page. If one row feels unfamiliar, do its exercise before moving on.

## 2. The operations, symbol by symbol

| Operation | Formula | Toy example | Why this paper needs it |
|---|---|---|---|
| **Vector** | $\mathbf{a} = [a_1, \dots, a_d]$ | $[0.6, 0.8]$ | Everything is a vector: hidden states, queries, documents |
| **Dot product** | $\mathbf{a} \cdot \mathbf{b} = \sum_i a_i b_i$ | $[0.6, 0.8] \cdot [0.8, 0.6] = 0.96$ | Scoring documents, attention, all three losses |
| **Length (L2 norm)** | $\lVert \mathbf{a} \rVert_2 = \sqrt{\sum_i a_i^2}$ | $\lVert [3,4] \rVert = 5$ | Normalizing the output (step 4) |
| **Normalize** | $\mathbf{a} / \lVert \mathbf{a} \rVert$ | $[3,4]/5 = [0.6, 0.8]$ | Makes every search vector length 1 |
| **Cosine similarity** | $\cos(\mathbf{a}, \mathbf{b}) = \dfrac{\mathbf{a}\cdot\mathbf{b}}{\lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert}$ | $\cos([2,0],[1,1]) = \tfrac{2}{2 \times 1.414} = 0.707$ | Alignment loss; how the index compares vectors |
| **Vector × matrix** | $(\mathbf{a}\mathbf{W})_j = \mathbf{a} \cdot (\text{column } j \text{ of } \mathbf{W})$ | $[1,0,2]$ with columns $[1,0,1], [0,1,1]$ → $[3, 2]$ | Input and output projections |
| **Exponential** | $e^x$, with $e \approx 2.718$ | $e^0 = 1$, $e^1 = 2.718$, $e^2 = 7.389$, $e^3 = 20.09$ | Inside softmax |
| **Natural log** | $\log$ undoes $e^x$ | $-\log 1 = 0$, $-\log 0.5 = 0.693$, $-\log 0.1 = 2.303$ | Turning probabilities into losses |
| **Softmax** | $\mathrm{softmax}(\mathbf{s})_k = \dfrac{e^{s_k}}{\sum_m e^{s_m}}$ | $[2, 1, 0]$ → $[0.665, 0.245, 0.090]$ | Attention weights, contrastive and rank losses |
| **KL divergence** | $\mathrm{KL}(P \Vert Q) = \sum_k P_k \log \dfrac{P_k}{Q_k}$ | $P = [0.5,0.5]$, $Q = [0.9,0.1]$ → $0.51$ | Rank distillation |

## 3. Shapes: toy vs. real

A dot product of two 2-number vectors takes 2 multiplications. Of two 1,024-number vectors, 1,024. Nothing else changes, which is why tiny examples teach the real thing.

## 4. The key shortcut, worked out

If $\lVert\mathbf{a}\rVert = \lVert\mathbf{b}\rVert = 1$, the cosine formula's denominator is $1 \times 1$:

$$\cos(\mathbf{a}, \mathbf{b}) = \mathbf{a} \cdot \mathbf{b}$$

Check with the teacher and student: both have length 1, their dot product is $0.96$, and their cosine is $0.96 / (1 \times 1) = 0.96$. Same number. This is the whole reason the student normalizes its output.

## 5. Going deeper

### Distance and cosine are the same thing for unit vectors

For unit vectors, $\lVert \mathbf{a} - \mathbf{b} \rVert^2 = \lVert\mathbf{a}\rVert^2 + \lVert\mathbf{b}\rVert^2 - 2\,\mathbf{a}\cdot\mathbf{b} = 2 - 2\cos(\mathbf{a},\mathbf{b})$.

Student vs teacher: $\lVert[0.6,0.8]-[0.8,0.6]\rVert^2 = 0.04 + 0.04 = 0.08$, and $2 - 2(0.96) = 0.08$ ✓.
So "closest" and "most similar direction" give the same ranking once everything is normalized.

### Softmax only cares about differences

Adding the same number to every score doesn't change softmax: $[2,1,0]$ and $[12,11,10]$ give the same probabilities, because $e^{s+c} = e^c e^s$ and the $e^c$ cancels top and bottom. This fact explains why rank distillation can't work alone (file 10).

### Two-item softmax shortcut

With two scores, correct $a$ and wrong $b$: $\dfrac{e^a}{e^a + e^b} = \dfrac{1}{1 + e^{\,b-a}}$. Used in file 09.

### KL is not symmetric

$\mathrm{KL}(P\Vert Q) \neq \mathrm{KL}(Q \Vert P)$ in general. With $P = [0.5,0.5]$, $Q = [0.9, 0.1]$: $\mathrm{KL}(P\Vert Q) = 0.51$ but $\mathrm{KL}(Q\Vert P) = 0.9\log 1.8 + 0.1 \log 0.2 = 0.529 - 0.161 = 0.368$. The order matters; the paper puts the **teacher first** (file 10).

## 6. Common mistakes

- Using $\log_{10}$ instead of the natural log. All logs here are natural ($\ln$).
- Forgetting softmax needs *every* score in the denominator, including the one on top.
- Thinking a matrix multiply mixes tokens. $\mathbf{H}\mathbf{W}$ processes **each row (token) separately**. Mixing tokens is the encoder's job.

## 7. Check yourself

1. $[1, 2] \cdot [3, -1] = \;?$
2. Normalize $[1, 1]$.
3. Softmax of $[1, 1, 1]$?
4. Softmax of $[0, \log 3]$? (Hint: $e^{\log 3} = 3$.)

---
**Answers.** 1. $3 - 2 = 1$. 2. $[0.707, 0.707]$. 3. $[1/3, 1/3, 1/3]$. 4. $[1/4, 3/4] = [0.25, 0.75]$. This is how an attention weight of exactly 75% arises: the two scores must differ by $\log 3 \approx 1.099$.
