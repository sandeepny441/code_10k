# 11 · Combining the Losses

## 1. Where we are

Training needs **one** number to minimize. We add the three losses with a weight on each.

## 2. The formula, symbol by symbol

$$\mathcal{L} = \lambda_a\,\mathcal{L}_{\text{align}} + \lambda_c\,\mathcal{L}_{\text{contra}} + \lambda_r\,\mathcal{L}_{\text{rank}}$$

| Symbol | Meaning | Paper's best |
|---|---|---|
| $\lambda_a$ | How much a wrong direction matters | 0.5 |
| $\lambda_c$ | How much confusion between queries matters | 0.5 |
| $\lambda_r$ | How much wrong document order matters | 0.5 |

## 3. Shapes: toy vs. real

Always a single number, whatever the batch or vector size.

## 4. The worked numbers

| Weights | Calculation | $\mathcal{L}$ |
|---|---|---|
| All 1 | $0.04 + 0.304 + 0.181$ | 0.525 |
| $\lambda_c = 2$, others 1 | $0.04 + 2(0.304) + 0.181$ | 0.829 |
| Paper: all 0.5 | $0.5 \times 0.525$ | 0.2625 |

## 5. Going deeper

### 5a. The size of a loss is not its importance

Alignment is 0.04 and contrastive is 0.304, but that doesn't mean contrastive "matters" 7× more. What drives learning is the **gradient**, not the value. The gradients add up just like the losses:

$$\nabla\mathcal{L} = \lambda_a\nabla\mathcal{L}_{\text{align}} + \lambda_c\nabla\mathcal{L}_{\text{contra}} + \lambda_r\nabla\mathcal{L}_{\text{rank}}$$

Each loss's gradient has its own natural size. Contrastive and rank divide by small temperatures ($\tau = 0.05$), which tends to make their gradients large; alignment's are gentle. The $\lambda$s balance these pushes.

### 5b. Only the ratios really matter (with AdamW)

Setting all three weights to 0.5 instead of 1 halves every gradient. With plain gradient descent that would be the same as halving the learning rate. **Adam**, however, divides each update by a running estimate of the gradient's size (file 12), so scaling the whole loss by a constant barely changes the updates. What matters is the **ratio** $\lambda_a : \lambda_c : \lambda_r$. The paper's 0.5 / 0.5 / 0.5 is effectively "equal weights". (Weight decay is the one part that doesn't rescale, so it isn't *exactly* the same.)

### 5c. What the paper learned by turning the knobs

| $\lambda_a / \lambda_c / \lambda_r$ | R@10 | Lesson |
|---|---|---|
| 1 / 0 / 0 | 0.567 | Alignment alone is solid |
| 0 / 1 / 0 | 0.498 | Contrastive alone is weaker |
| 0 / 0 / 1 | 0.001 | Rank alone collapses (file 10) |
| 0.5 / 0.5 / 0 | 0.582 | |
| 0.5 / 0 / 0.5 | 0.579 | |
| 1 / 0 / 0.5 | 0.591 | Leaning on alignment is safe |
| 0.5 / 0 / 1 | 0.516 | Leaning on rank hurts |
| 0.5 / 0.5 / 0.5 | 0.595 | All three is best |

(All at 30 epochs, learning rate $3 \times 10^{-4}$.)

### 5d. Each term catches a different mistake

| Loss | Toy verdict | Catches |
|---|---|---|
| Alignment | 0.04, "fine" | Wrong direction |
| Contrastive | 0.304, "student 2 is confused" | Queries that blur together |
| Rank | 0.181, "pizza is ranked too high" | Wrong document order |

## 6. Common mistakes

- Comparing loss values across different weight settings. A higher total loss with bigger $\lambda$s doesn't mean a worse model.
- Tuning $\lambda$s and learning rate separately as if independent. They interact.

## 7. Check yourself

1. Compute $\mathcal{L}$ with $\lambda_a = 1$, $\lambda_c = 0$, $\lambda_r = 0.5$ for the toy.
2. Why is 0.5/0.5/0.5 with Adam almost the same as 1/1/1?

---
**Answers.** 1. $0.04 + 0 + 0.0905 = 0.1305$. 2. Adam normalizes each update by the gradient's recent size, so multiplying the whole loss by 0.5 cancels out; only the ratios between the three stay meaningful.
