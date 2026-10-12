# 04 · Step 3: Mean Pooling

## 1. Where we are

The encoder gives one vector per token. A search needs **one** vector per query. Mean pooling averages the real tokens.

```
X' (n × d_m) ──► [ average over real tokens ] ──► p (d_m)
```

## 2. The formula, symbol by symbol

The paper's version:

$$\mathbf{p} = \frac{1}{n}\sum_{i=1}^{n} \mathbf{x}_i$$

where $n$ counts **only** valid (non-padding) positions. In code it is written with a **mask** $m_i$ (1 for real tokens, 0 for padding):

$$\mathbf{p} = \frac{\sum_i m_i\,\mathbf{x}_i}{\sum_i m_i}$$

## 3. Shapes: toy vs. real

| | Toy | Paper |
|---|---|---|
| Input | $2 \times 2$ (or $3 \times 2$ with a pad) | $n \times 1024$, padded to the longest query in the batch |
| Output $\mathbf{p}$ | 2 numbers | 1,024 numbers |
| Learned parameters | 0 | 0 |

Pooling has no weights. It is a fixed operation.

## 4. The worked numbers

$$\mathbf{p} = \frac{[2.5, 2] + [1.5, 2]}{2} = \frac{[4, 4]}{2} = [2, 2]$$

With a pad token that came out of the encoder as $[4, -1]$:

| | Mask | Calculation | Result |
|---|---|---|---|
| Right | $[1, 1, 0]$ | $([2.5,2] + [1.5,2]) / 2$ | $[2, 2]$ ✓ |
| Wrong | ignored | $([2.5,2] + [1.5,2] + [4,-1]) / 3$ | $[2.67, 1]$ ✗ |

## 5. Going deeper

### Why padding exists at all

Training processes 16 queries at once as one grid of numbers. Grids need equal row lengths, so short queries are filled with pad tokens. A 3-token query in a batch whose longest query has 9 tokens gets 6 pads. Without masking, that short query's vector would be two-thirds garbage.

### Why pads aren't zero after the encoder

Even if a pad starts as zeros, it gets a position vector, passes through attention (it can attend to real tokens), and through the feed-forward layer and its biases. It comes out as *something*. (Real implementations also stop real tokens from attending *to* pads.)

### Mean pooling and a causal LLM

Because the LLM is causal, the hidden state of the **last** query token has seen the most. Mean pooling gives the first token, which saw the least, the same weight. The encoder partly fixes this by letting early tokens read later ones. Alternatives:

| Pooling | Formula | Used by |
|---|---|---|
| Mean | average of real tokens | This paper |
| Last token | $\mathbf{p} = \mathbf{x}_n$ | Many LLM-based embedders |
| Attention pooling | learned weights over tokens | NV-Embed |

The paper only tests mean pooling.

### Average vs. sum

Using the sum instead of the mean would make longer queries produce longer vectors. The final normalization (step 4) would remove the length anyway, but the bias added before it would then matter more for short queries than for long ones. The mean keeps the scale steady.

## 6. Common mistakes

- Dividing by the padded length instead of the real length.
- Forgetting to mask pads, which may still "work" but quietly hurts short queries most.
- Thinking pooling is learned. It isn't.

## 7. Check yourself

1. Tokens $[1, 0]$, $[3, 2]$, $[2, 4]$ with mask $[1, 1, 0]$. Correct $\mathbf{p}$?
2. Same, if you forget the mask?
3. A batch has queries of 4, 7 and 12 tokens. How many pads does each get?

---
**Answers.** 1. $([1,0] + [3,2])/2 = [2, 1]$. 2. $[6, 6]/3 = [2, 2]$. 3. 8, 5 and 0.
