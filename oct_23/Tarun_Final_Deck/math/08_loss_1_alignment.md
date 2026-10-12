# 08 · Loss 1: Alignment ("point where your teacher points")

## 1. Where we are

The simplest possible training signal: for each query, how far is the student's direction from the teacher's? It only looks at the **diagonal** of the batch grid.

## 2. The formula, symbol by symbol

$$\mathcal{L}_{\text{align}} = 1 - \frac{1}{B}\sum_{j=1}^{B}\cos\!\big(f(\mathbf{H}^{(j)}),\ \mathbf{y}^{(j)}\big)$$

| Piece | Meaning |
|---|---|
| $\cos(\cdot,\cdot)$ | Direction match for one query, from −1 to 1 |
| $\frac{1}{B}\sum_j$ | Average over the batch |
| $1 - \ldots$ | Flip it so that perfect = 0 and worse = bigger |

Range: 0 (perfect) to 2 (every student points exactly opposite its teacher).

## 3. Shapes: toy vs. real

| | Toy | Paper |
|---|---|---|
| Cosines computed | 2 | 16 per batch |
| Numbers per cosine | 2 | 1,024 |
| Weight in the total loss | 1 (file 11) | $\lambda_a = 0.5$ |

## 4. The worked numbers

| Query | Cosine (both unit, so just the dot product) |
|---|---|
| 1 | $[0.6, 0.8]\cdot[0.8, 0.6] = 0.96$ |
| 2 | $[0.96, 0.28]\cdot[1, 0] = 0.96$ |

$$\mathcal{L}_{\text{align}} = 1 - \frac{0.96 + 0.96}{2} = 0.04$$

## 5. Going deeper

### 5a. It is secretly a squared distance

For unit vectors, $\lVert\mathbf{u} - \mathbf{y}\rVert^2 = 2 - 2\cos(\mathbf{u},\mathbf{y})$ (file 01). So

$$\mathcal{L}_{\text{align}} = \frac{1}{B}\sum_j \tfrac{1}{2}\lVert f(\mathbf{H}^{(j)}) - \mathbf{y}^{(j)}\rVert^2$$

Check for query 1: $\tfrac12 \lVert[-0.2, 0.2]\rVert^2 = \tfrac12(0.08) = 0.04$ ✓. So alignment is "mean squared error on the unit sphere".

### 5b. The gradient: which way to push

For one query, write $\mathbf{z}$ for the raw output (before normalizing) and $\mathbf{u} = \mathbf{z}/\lVert\mathbf{z}\rVert$. The gradient of $1 - \mathbf{u}\cdot\mathbf{y}$ with respect to $\mathbf{z}$ is

$$\frac{\partial \mathcal{L}}{\partial \mathbf{z}} = -\frac{\mathbf{y} - (\mathbf{u}\cdot\mathbf{y})\,\mathbf{u}}{\lVert\mathbf{z}\rVert}$$

In words: take the teacher's direction, remove the part that already agrees with the student, and push along what is left. Divide by the length (long vectors are harder to turn).

Query 1: $\mathbf{z} = [3, 4]$, $\mathbf{u} = [0.6, 0.8]$, $\mathbf{u}\cdot\mathbf{y} = 0.96$.

| Piece | Value |
|---|---|
| $(\mathbf{u}\cdot\mathbf{y})\,\mathbf{u}$ | $0.96 \times [0.6, 0.8] = [0.576, 0.768]$ |
| $\mathbf{y} - $ that | $[0.8 - 0.576,\ 0.6 - 0.768] = [0.224, -0.168]$ |
| $\div \lVert\mathbf{z}\rVert = 5$, with minus sign | $[-0.0448,\ 0.0336]$ |

Gradient descent moves **against** the gradient: increase the first coordinate (more cat), decrease the second (less food). Exactly the fix we wanted. Since $\mathbf{z} = \mathbf{p} + \mathbf{b}_{\text{out}}$, this is also the gradient for $\mathbf{b}_{\text{out}}$. File 12 takes steps with it.

### 5c. Its blind spot

Alignment treats each query alone. It cannot see that student 2 ($[0.96, 0.28]$) is nearly as close to teacher 1 as to teacher 2, or that student 1 ranks pizza above the cat guide. Both students have the same "grade" (0.96) even though their problems are different. That is why two more losses exist.

### 5d. Why it is the backbone

It gives every query a fixed, absolute target, so it always has a useful gradient, even at the start of training when everything is random. In the paper it is the strongest single loss (Recall@10 0.567 alone), and rank distillation collapses without it (file 10).

## 6. Common mistakes

- Averaging distances instead of cosines, then subtracting from 1. The formula averages **cosines**.
- Expecting the loss to reach exactly 0 on real data. The student can't reproduce the teacher perfectly for every query.

## 7. Check yourself

1. Student $[1, 0]$, teacher $[0.6, 0.8]$, $B = 1$. Loss?
2. What loss do you get if every student points exactly opposite its teacher?
3. Using 5b, compute the gradient for $\mathbf{z} = [4, 3]$, $\mathbf{y} = [0.8, 0.6]$.

---
**Answers.** 1. $1 - 0.6 = 0.4$. 2. $1 - (-1) = 2$. 3. $\mathbf{u} = \mathbf{y}$, so $\mathbf{y} - 1\cdot\mathbf{u} = [0, 0]$ and the gradient is zero: nothing to fix.
