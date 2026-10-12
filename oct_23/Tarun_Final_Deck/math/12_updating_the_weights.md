# 12 · Updating the Weights

## 1. Where we are

We have one loss number. Now we change the head's numbers so that the loss goes down, and repeat many times.

**What changes:** $\mathbf{W}_{\text{in}}, \mathbf{b}_{\text{in}}$, the positional vectors, the encoder's weights, $\mathbf{W}_{\text{out}}, \mathbf{b}_{\text{out}}$.
**What stays frozen:** the LLM and the teacher.

## 2. The formulas, symbol by symbol

**Gradient descent:**
$$w \leftarrow w - \eta\,g$$
where $g = \partial\mathcal{L}/\partial w$ is the gradient and $\eta$ the learning rate.

**AdamW** (what the paper uses), per weight:

| Line | Formula | Meaning |
|---|---|---|
| Momentum | $m \leftarrow \beta_1 m + (1-\beta_1)\,g$ | Running average of gradients |
| Size | $v \leftarrow \beta_2 v + (1-\beta_2)\,g^2$ | Running average of squared gradients |
| Bias fix | $\hat{m} = m/(1-\beta_1^t)$, $\hat{v} = v/(1-\beta_2^t)$ | Corrects the early averages, which start at 0 |
| Update | $w \leftarrow w - \eta\left(\dfrac{\hat{m}}{\sqrt{\hat{v}} + \epsilon} + \lambda_{\text{wd}}\,w\right)$ | Step against the gradient, scaled per weight, plus weight decay |

**Cosine schedule:**
$$\eta_t = \eta_{\min} + \tfrac{1}{2}(\eta_{\max} - \eta_{\min})\big(1 + \cos(\pi t/T)\big)$$

**Gradient clipping:** if $\lVert\mathbf{g}\rVert > c$, replace $\mathbf{g}$ with $\mathbf{g}\cdot c/\lVert\mathbf{g}\rVert$.

## 3. Shapes: toy vs. real

| | Toy | Paper |
|---|---|---|
| Learned numbers | $\mathbf{b}_{\text{out}}$ only, in the demo | ~25–30M |
| $\beta_1, \beta_2$ | 0.9, 0.999 | 0.9, 0.999 |
| Weight decay $\lambda_{\text{wd}}$ | — | $10^{-4}$ |
| $\eta_{\max} \to \eta_{\min}$ | 0.001 → 0 | $2\times10^{-4} \to 10^{-5}$ |
| Schedule length | 1,000 steps | 80 epochs |
| Clip norm $c$ | — | 1.0 |

## 4. The worked numbers

The worked example jumped straight to the "ideal" bias $[2, 1]$: $[2,2] + [2,1] = [4, 3] \to [0.8, 0.6]$, exactly the teacher. Alignment and rank loss for query 1 both become 0. Here is how gradient descent actually **gets** there.

## 5. Going deeper

### 5a. Gradient descent on $\mathbf{b}_{\text{out}}$, step by step

Use only the alignment loss for query 1, and let only $\mathbf{b}_{\text{out}}$ change ($\mathbf{p} = [2,2]$ fixed). The gradient formula is from file 08, 5b. Learning rate $\eta = 5$ (huge, so the toy moves visibly).

| Step | $\mathbf{b}_{\text{out}}$ | $\mathbf{z}$ | $f(\mathbf{H})$ | $\mathcal{L}_{\text{align}}$ | Gradient |
|---|---|---|---|---|---|
| 0 | $[1.000, 2.000]$ | $[3.000, 4.000]$ | $[0.600, 0.800]$ | 0.0400 | $[-0.0448, 0.0336]$ |
| 1 | $[1.224, 1.832]$ | $[3.224, 3.832]$ | $[0.644, 0.765]$ | 0.0259 | $[-0.0345, 0.0290]$ |
| 2 | $[1.397, 1.687]$ | $[3.397, 3.687]$ | $[0.678, 0.736]$ | 0.0167 | $[-0.0267, 0.0246]$ |
| 3 | $[1.530, 1.564]$ | $[3.530, 3.564]$ | $[0.704, 0.711]$ | 0.0107 | $[-0.0207, 0.0205]$ |
| 4 | $[1.634, 1.461]$ | $[3.634, 3.461]$ | $[0.724, 0.690]$ | 0.0069 | $[-0.0161, 0.0169]$ |
| 5 | $[1.714, 1.377]$ | $[3.714, 3.377]$ | $[0.740, 0.673]$ | 0.0045 | $[-0.0126, 0.0139]$ |

Each step: $\mathbf{b}_{\text{new}} = \mathbf{b} - 5 \times \text{gradient}$. For step 0→1: $[1 + 0.224,\ 2 - 0.168]$.

Watch three things:
- The bias slides toward $[2, 1]$ and the output toward $[0.8, 0.6]$.
- The loss shrinks every step.
- The gradient **shrinks** as we get closer, so steps get smaller on their own. Convergence slows down near the target.

Between steps 3 and 4 the student's cat-score passes its pizza-score (0.724 > 0.690): pizza has dropped back below the cat guide.

### 5b. One AdamW step

At step $t = 1$, starting from $m = v = 0$, with $\mathbf{g} = [-0.0448, 0.0336]$:

- $m = 0.1\,g$, $v = 0.001\,g^2$
- $\hat{m} = 0.1g / 0.1 = g$, $\hat{v} = 0.001g^2/0.001 = g^2$
- $\hat{m}/\sqrt{\hat{v}} = g/|g| = $ **sign of $g$** $= [-1, +1]$

So Adam's first step moves every weight by (almost) exactly $\eta$, regardless of how big its gradient is. With the paper's $\eta = 2 \times 10^{-4}$:

$$\mathbf{b}_{\text{out}} = [1, 2] - 2\times10^{-4}\,[-1, 1] = [1.0002,\ 1.9998]$$

Weight decay adds $\eta\lambda_{\text{wd}}w = 2\times10^{-4}\cdot10^{-4}\cdot w$, about $10^{-8}$ here: a very gentle pull toward zero that matters only over thousands of steps.

This is why Adam doesn't care much about the overall scale of the loss (file 11): the update depends on $g$ divided by its own size.

### 5c. Gradient clipping

If one unlucky batch produces a gradient $[3, 4]$ (length 5) and the clip norm is 1, it becomes $[3,4] \times 1/5 = [0.6, 0.8]$. Same direction, capped size. In the paper the norm is taken over **all** parameters together. Clipping protects against the large gradients that small temperatures can produce (file 09).

### 5d. The cosine schedule with the paper's numbers

| Epoch $t$ | $\cos(\pi t/80)$ | $\eta_t$ |
|---|---|---|
| 0 | 1 | $2.0 \times 10^{-4}$ |
| 20 | 0.707 | $1.72 \times 10^{-4}$ |
| 40 | 0 | $1.05 \times 10^{-4}$ |
| 60 | −0.707 | $0.38 \times 10^{-4}$ |
| 80 | −1 | $0.10 \times 10^{-4}$ |

Large steps early to get into the right region; tiny steps late to settle into the "subtle geometry" without bouncing out. The paper's recipe results fit this story: $5\times10^{-4}$ collapses, $3\times10^{-4}$ for 50 epochs overshoots, $2\times10^{-4}$ for 80 epochs is best.

### 5e. Why real training is harder than the toy

Our toy fixed one query with one bias change. The real head must find **one** set of ~25–30M numbers that works for every query at once. A change that helps "cat food" might hurt "cat toys". That tug of war, averaged over batches, is why it takes 80 epochs of small steps.

## 6. Common mistakes

- Moving **with** the gradient instead of against it.
- Training the LLM or teacher by accident. Only the head's parameters should be in the optimizer.
- Confusing weight decay with L2 loss. AdamW applies decay directly to the weights, separately from the gradient ("decoupled").

## 7. Check yourself

1. $w = 2$, $g = 0.5$, $\eta = 0.1$. New $w$ with plain gradient descent?
2. What is Adam's first-step update for a weight with $g = 0.0001$ and $\eta = 0.01$?
3. Clip $\mathbf{g} = [0.3, 0.4]$ at norm 1.
4. Using the table in 5a, what is $\mathbf{b}_{\text{out}}$ after step 6? (Step 5's gradient is $[-0.0126, 0.0139]$.)

---
**Answers.** 1. $1.95$. 2. About $-0.01$ (a step of size $\eta$ against the sign of $g$). 3. Unchanged: its length is 0.5, below 1. 4. $[1.714 + 0.063,\ 1.377 - 0.070] = [1.777, 1.307]$.
