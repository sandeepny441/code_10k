# 02 · Step 1: Input Projection

## 1. Where we are

The LLM hands us one hidden state per token. They are too wide (4,096). We resize each one to the head's working width (1,024). Nothing is mixed between tokens yet.

```
H (n × d_h) ──► [ × W_in + b_in ] ──► X (n × d_m)
```

## 2. The formula, symbol by symbol

$$\mathbf{X} = \mathbf{H}\mathbf{W}_{\text{in}} + \mathbf{b}_{\text{in}}$$

| Symbol | Meaning | Learned? |
|---|---|---|
| $\mathbf{H}$ | Hidden states, one row per token | No, comes from the frozen LLM |
| $\mathbf{W}_{\text{in}}$ | Resize matrix, $d_h$ rows × $d_m$ columns | Yes |
| $\mathbf{b}_{\text{in}}$ | Bias, one number per output column, added to every token | Yes |
| $\mathbf{X}$ | Resized token vectors, one row per token | Output |

Row by row, for each token $i$: $\mathbf{x}_i = \mathbf{h}_i \mathbf{W}_{\text{in}} + \mathbf{b}_{\text{in}}$.

## 3. Shapes: toy vs. real

| | Toy | Paper |
|---|---|---|
| $\mathbf{H}$ | $2 \times 3$ | $n \times 4096$ |
| $\mathbf{W}_{\text{in}}$ | $3 \times 2$ | $4096 \times 1024$ |
| $\mathbf{b}_{\text{in}}$ | $2$ | $1024$ |
| $\mathbf{X}$ | $2 \times 2$ | $n \times 1024$ |
| Learned numbers | $3 \cdot 2 + 2 = 8$ | $4096 \cdot 1024 + 1024 = 4{,}195{,}328$ |

The input projection alone is about 4.2M parameters, a large share of the whole head.

## 4. The worked numbers

$\mathbf{W}_{\text{in}}$ columns: $[1,0,1]$ and $[0,1,1]$. $\mathbf{b}_{\text{in}} = [0, 0]$.

| Token | Column 1 | Column 2 | $\mathbf{x}_i$ |
|---|---|---|---|
| cat, $[1,0,2]$ | $1 + 0 + 2 = 3$ | $0 + 0 + 2 = 2$ | $[3, 2]$ |
| food, $[0,1,1]$ | $0 + 0 + 1 = 1$ | $0 + 1 + 1 = 2$ | $[1, 2]$ |

As a full matrix product:

$$
\underbrace{\begin{bmatrix} 1 & 0 & 2 \\ 0 & 1 & 1 \end{bmatrix}}_{\mathbf{H}}
\underbrace{\begin{bmatrix} 1 & 0 \\ 0 & 1 \\ 1 & 1 \end{bmatrix}}_{\mathbf{W}_{\text{in}}}
= \begin{bmatrix} 3 & 2 \\ 1 & 2 \end{bmatrix}
$$

## 5. Going deeper

### Each output number is a "recipe"

Column 1 of $\mathbf{W}_{\text{in}}$ is $[1, 0, 1]$: "take hidden dimension 1, ignore dimension 2, add dimension 3". Each column is a learned recipe for one new feature. With 1,024 columns, the head learns 1,024 recipes, each mixing all 4,096 LLM dimensions.

### It can only throw information away, never add it

Going from 3 numbers to 2 means some combination of the originals is lost. In the toy, the direction $[1, 1, -1]$ gives $[1+0-1, 0+1-1] = [0, 0]$. Any hidden state can be shifted along $[1,1,-1]$ and the head won't notice. With 4096 → 1024, there are at least 3,072 such "invisible" directions. Training has to choose which 1,024 combinations of the LLM's thoughts are worth keeping for search.

### The bias shifts every token equally

With $\mathbf{b}_{\text{in}} = [0.5, -1]$, "cat" becomes $[3.5, 1]$ and "food" becomes $[1.5, 1]$. Both move by the same amount.

## 6. Common mistakes

- Writing $\mathbf{W}\mathbf{H}$ instead of $\mathbf{H}\mathbf{W}$. With tokens as rows, the matrix goes on the right.
- Thinking this step mixes tokens. Row $i$ of $\mathbf{X}$ depends only on row $i$ of $\mathbf{H}$.
- Forgetting the bias is the same for every token.

## 7. Check yourself

1. Project $\mathbf{h} = [2, 1, 0]$ with the same $\mathbf{W}_{\text{in}}$ and zero bias.
2. Same, but with $\mathbf{b}_{\text{in}} = [0.5, -1]$.
3. If $d_h = 4096$ and $d_m = 512$, how many numbers are in $\mathbf{W}_{\text{in}}$?

---
**Answers.** 1. $[2+0+0,\; 0+1+0] = [2, 1]$. 2. $[2.5, 0]$. 3. $4096 \times 512 = 2{,}097{,}152$.
