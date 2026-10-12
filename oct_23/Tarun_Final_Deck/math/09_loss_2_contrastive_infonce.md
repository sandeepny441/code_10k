# 09 · Loss 2: Contrastive, InfoNCE ("be closer to your teacher than to anyone else's")

## 1. Where we are

Alignment reads only the diagonal of the batch grid. Contrastive loss reads **whole rows**: each student must beat every other teacher in the batch, not just be near its own.

## 2. The formula, symbol by symbol

$$\mathcal{L}_{\text{contra}} = -\frac{1}{B}\sum_{j=1}^{B}\log\frac{\exp\!\big(f(\mathbf{H}^{(j)})\cdot\mathbf{y}^{(j)}/\tau\big)}{\sum_{k=1}^{B}\exp\!\big(f(\mathbf{H}^{(j)})\cdot\mathbf{y}^{(k)}/\tau\big)}$$

| Piece | Meaning |
|---|---|
| $f(\mathbf{H}^{(j)})\cdot\mathbf{y}^{(k)}$ | Grid entry: student $j$ vs teacher $k$ |
| $/\tau$ | Temperature: divide by a small number to exaggerate differences |
| The fraction | Softmax over row $j$, read at the correct column: "probability student $j$ picks its own teacher" |
| $-\log$ | Small when that probability is near 1, big when it is low |
| $\frac{1}{B}\sum_j$ | Average over students |

This is ordinary **cross-entropy** where the "classes" are the teachers in the batch and the correct class is the diagonal.

## 3. Shapes: toy vs. real

| | Toy | Paper |
|---|---|---|
| Grid | $2 \times 2$ | $16 \times 16$ |
| Wrong teachers per student | 1 | 15 |
| $\tau$ | 0.1 | 0.05 |
| Weight | 1 | $\lambda_c = 0.5$ |

## 4. The worked numbers ($\tau = 0.1$)

| | vs $\mathbf{y}^{(1)}$ | vs $\mathbf{y}^{(2)}$ | Prob. of own teacher | $-\log$ |
|---|---|---|---|---|
| student 1 | **9.6** | 6.0 | $1/(1 + e^{-3.6}) = 0.973$ | 0.027 |
| student 2 | 9.36 | **9.6** | $1/(1 + e^{-0.24}) = 0.560$ | 0.580 |

$$\mathcal{L}_{\text{contra}} = \frac{0.027 + 0.580}{2} = 0.304$$

Student 2 is nearly a coin flip between "cat toys" and "cat food". Alignment gave it the same grade as student 1.

## 5. Going deeper

### 5a. The gradient is "prediction minus truth"

For cross-entropy on softmax, the gradient with respect to each grid entry in row $j$ is

$$\frac{\partial \mathcal{L}_j}{\partial (\text{entry}_{jk})} = \frac{P_{jk} - [k = j]}{\tau}$$

where $[k=j]$ is 1 on the diagonal and 0 elsewhere.

| | Push on correct entry | Push on wrong entry |
|---|---|---|
| student 1 | $(0.973 - 1)/0.1 = -0.27$ | $(0.027 - 0)/0.1 = +0.27$ |
| student 2 | $(0.560 - 1)/0.1 = -4.40$ | $(0.440 - 0)/0.1 = +4.40$ |

(Negative gradient = descent will **raise** that score; positive = descent will **lower** it.)

Student 2 gets about **16× the push** of student 1. Contrastive loss automatically spends its effort on the confused queries.

### 5b. What temperature really does (a correction)

The worked example says that with $\tau = 1$ "the loss would treat the problem as smaller". The **value** of the loss actually goes up. What goes down is how much it *singles out* the hard case:

| $\tau$ | P(own) student 1 | P(own) student 2 | Loss 1 | Loss 2 | Batch loss | Push ratio (2 vs 1) |
|---|---|---|---|---|---|---|
| 1 | 0.589 | 0.506 | 0.529 | 0.681 | 0.605 | ~1.2× |
| 0.1 | 0.973 | 0.560 | 0.027 | 0.580 | 0.304 | ~16× |
| 0.05 (paper) | 0.9993 | 0.618 | 0.0007 | 0.482 | 0.241 | ~550× |

With $\tau = 1$, both students look "somewhat unsure", so both get similar pushes. With a small $\tau$, the easy query is treated as solved and nearly all the learning goes to the near-tie. Small $\tau$ = strict teacher who ignores what you already know and drills your mistakes.

The risk: very small $\tau$ makes gradients large and training jumpy. That sensitivity fits the paper's finding that too high a learning rate collapses training.

### 5c. Why this keeps queries apart in the index

If two different queries get almost the same vector, they will retrieve almost the same documents. Contrastive loss explicitly punishes that. In the paper, it adds about 1.5 points of Recall@10 on top of alignment (0.567 → 0.582).

### 5d. One direction only

The paper's formula lets each **student** pick among **teachers** (rows). Some methods also add the reverse (each teacher picks among students, columns). The paper uses only the row version.

## 6. Common mistakes

- Forgetting to include the correct pair in the denominator.
- Reading "smaller $\tau$ → bigger loss". Not always; smaller $\tau$ → sharper focus on near-ties.
- Assuming a batch of 16 covers all the confusions. A student is only compared with the 15 queries that happen to share its batch.

## 7. Check yourself

1. With $\tau = 0.1$, what would student 2's probability be if its wrong score dropped from 0.936 to 0.5?
2. Why does student 1 barely learn anything from this loss at $\tau = 0.05$?
3. In a batch of 16, how many exponentials are computed in total?

---
**Answers.** 1. $1/(1 + e^{5 - 9.6}) = 1/(1 + e^{-4.6}) = 0.990$. 2. Its probability of picking its own teacher is already 0.9993, so $P - 1 \approx 0$. 3. $16 \times 16 = 256$.
