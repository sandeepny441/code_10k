# 05 · Step 4: Output Projection and L2 Normalization

## 1. Where we are

We have one pooled vector $\mathbf{p}$ at the head's width. The index expects the teacher's width, and vectors of length 1. One more learned resize, then divide by the length. The result is the student's search vector.

```
p (d_m) ──► [ × W_out + b_out ] ──► z (d) ──► [ ÷ ‖z‖ ] ──► f(H) (d, length 1)
```

## 2. The formula, symbol by symbol

$$f(\mathbf{H}) = \frac{\mathbf{p}\mathbf{W}_{\text{out}} + \mathbf{b}_{\text{out}}}{\left\lVert \mathbf{p}\mathbf{W}_{\text{out}} + \mathbf{b}_{\text{out}} \right\rVert_2}$$

It helps to name the top part: $\mathbf{z} = \mathbf{p}\mathbf{W}_{\text{out}} + \mathbf{b}_{\text{out}}$, the **raw** output. Then $f(\mathbf{H}) = \mathbf{z}/\lVert\mathbf{z}\rVert$.

| Symbol | Meaning | Learned? |
|---|---|---|
| $\mathbf{W}_{\text{out}}$ | $d_m \times d$ resize matrix | Yes |
| $\mathbf{b}_{\text{out}}$ | $d$-number bias | Yes |
| $\mathbf{z}$ | Raw output, any length | — |
| $\lVert\mathbf{z}\rVert_2$ | Its length | — |

## 3. Shapes: toy vs. real

| | Toy | Paper |
|---|---|---|
| $\mathbf{W}_{\text{out}}$ | $2 \times 2$ (identity) | $1024 \times 1024$ |
| $\mathbf{b}_{\text{out}}$ | $[1, 2]$ | 1,024 numbers |
| Learned numbers | 6 | $1024 \cdot 1024 + 1024 = 1{,}049{,}600$ |

In both toy and paper $d_m = d$, so this layer doesn't change the width. It still matters: it is a learned **rotation, stretch and shift** into the teacher's space.

## 4. The worked numbers

| Step | Calculation | Result |
|---|---|---|
| Multiply | $[2, 2] \times \mathbf{I}$ | $[2, 2]$ |
| Add bias | $[2, 2] + [1, 2]$ | $\mathbf{z} = [3, 4]$ |
| Length | $\sqrt{9 + 16}$ | $5$ |
| Normalize | $[3, 4] / 5$ | $f(\mathbf{H}) = [0.6, 0.8]$ |

## 5. Going deeper

### Normalization throws away length on purpose

$[3, 4]$, $[6, 8]$ and $[0.3, 0.4]$ all normalize to $[0.6, 0.8]$. After this step only **direction** carries meaning. That matches the teacher, whose vectors all have length 1, and the index, which compares by cosine.

### Why the bias matters so much here

In the toy, $\mathbf{p} = [2, 2]$ points exactly "half cat, half food". The bias $[1, 2]$ tips it toward food. In file 12, training changes the bias to $[2, 1]$, which tips it toward cats: $[2,2] + [2,1] = [4, 3]$, normalized to $[0.8, 0.6]$, exactly the teacher. One learned shift can rotate the final direction.

Notice that the bias has **more** influence when $\mathbf{p}$ is short. With $\mathbf{p} = [20, 20]$, adding $[1,2]$ gives $[21, 22]$, direction $\approx [0.69, 0.72]$, barely changed from $[0.707, 0.707]$. This is one reason the mean (not the sum) is used in pooling: it keeps $\mathbf{p}$'s scale stable across query lengths.

### What normalization does to gradients (preview of file 12)

Because $f = \mathbf{z}/\lVert\mathbf{z}\rVert$, making $\mathbf{z}$ longer changes nothing. So the gradient reaching $\mathbf{z}$ is always **perpendicular** to $\mathbf{z}$: training can only turn the vector, not stretch it. In numbers, the alignment gradient at $\mathbf{z} = [3,4]$ is $[-0.0448, 0.0336]$, and indeed $[-0.0448, 0.0336]\cdot[3,4] = -0.134 + 0.134 = 0$.

### Edge case

If $\mathbf{z}$ were exactly $[0, 0]$ the division would fail. Code adds a tiny number to the length ($\lVert\mathbf{z}\rVert + \epsilon$) to be safe.

## 6. Common mistakes

- Normalizing **before** adding the bias. The order is: multiply, add bias, then normalize.
- Forgetting to normalize, so scores depend on length (see file 06).
- Thinking a square $\mathbf{W}_{\text{out}}$ is pointless. It still reshapes the space.

## 7. Check yourself

1. $\mathbf{p} = [1, 3]$, $\mathbf{W}_{\text{out}} = \mathbf{I}$, $\mathbf{b}_{\text{out}} = [2, 1]$. What is $f(\mathbf{H})$?
2. What bias would make $\mathbf{p} = [2, 2]$ come out as exactly $[1, 0]$ after normalizing? Give one.
3. Is $[0.6, 0.8]$ still the output if $\mathbf{z}$ were $[30, 40]$?

---
**Answers.** 1. $\mathbf{z} = [3, 4]$, so $[0.6, 0.8]$. 2. Any bias giving $[c, 0]$ with $c > 0$, e.g. $[0, -2]$ gives $[2, 0] \to [1, 0]$. 3. Yes.
