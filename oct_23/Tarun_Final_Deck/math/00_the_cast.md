# 00 · The Cast

## 1. Where we are

Before any math, we fix the characters. Every later file uses exactly these numbers.

## 2. The characters

| Character | Symbol | Toy value | In the paper |
|---|---|---|---|
| The query the LLM writes | $q$ | "cat food", tokens *cat*, *food*, so $n = 2$ | Up to 32 generated tokens |
| Hidden states for the query | $\mathbf{H}$ | $\mathbf{h}_{\text{cat}} = [1, 0, 2]$, $\mathbf{h}_{\text{food}} = [0, 1, 1]$ | $n \times 4096$ |
| Teacher (embedding model) | $E$ | a function we don't open up | Qwen3-Embedding-8B |
| Teacher's query vector | $\mathbf{y} = E(q)$ | $[0.8, 0.6]$ | 1,024 numbers, length 1 |
| Student (projection head) | $f$ | the network we compute by hand | ~25M parameters |
| Student's query vector | $f(\mathbf{H})$ | $[0.6, 0.8]$ (computed in files 02–05) | 1,024 numbers, length 1 |

## 3. Shapes: toy vs. real

| Size | Symbol | Toy | Paper |
|---|---|---|---|
| LLM hidden width | $d_h$ | 3 | 4,096 |
| Head's internal width | $d_m$ | 2 | 1,024 |
| Embedding width | $d$ | 2 | 1,024 |
| Tokens in the query | $n$ | 2 | ≤ 32 |
| Queries per batch | $B$ | 2 | 16 |
| Documents used for ranking | $K$ | 3 | 128 |

## 4. The documents (stored in the index by the teacher)

Pretend dimension 1 is "cat-ness" and dimension 2 is "food-ness".

| | Document | Vector | Length |
|---|---|---|---|
| $\mathbf{d}_1$ | Cat behavior guide | $[1, 0]$ | 1 |
| $\mathbf{d}_2$ | Pizza recipes | $[0, 1]$ | 1 |
| $\mathbf{d}_3$ | Healthy dry food for cats | $[0.6, 0.8]$ | $\sqrt{0.36 + 0.64} = 1$ |

All document vectors have length 1, because the teacher normalizes its outputs.

## 5. Going deeper: why these particular numbers

The toy is built so that the student is **almost right in a misleading way**:

- The student's vector $[0.6, 0.8]$ is the teacher's $[0.8, 0.6]$ with its two numbers **swapped**. Both have length 1, and their cosine is $0.48 + 0.48 = 0.96$, which looks excellent.
- But the student leans toward *food* where the teacher leans toward *cats*. That lean is exactly what makes the student rank *Pizza recipes* above *Cat behavior guide* in file 06.
- The student's vector also happens to equal $\mathbf{d}_3$ exactly, so it finds the right document with a perfect score of 1.0, which hides the problem even more.

This one setup lets the three losses (files 08–10) each tell a different story.

## 6. Common mistakes

- Thinking the student reads the text "cat food". It **never** does; it only sees $\mathbf{H}$.
- Thinking the documents are embedded by the student. They were embedded by the **teacher**, once, before anything else. The student has to learn to speak the teacher's language.

## 7. Check yourself

1. Is $\mathbf{y} = [0.8, 0.6]$ a unit vector?
2. Which document would the teacher rank first? (Compute $\mathbf{y} \cdot \mathbf{d}_k$ for each.)
3. In the paper, how many numbers does $\mathbf{H}$ contain for a 10-token query?

---
**Answers.** 1. Yes: $0.64 + 0.36 = 1$. 2. $0.8$, $0.6$, $0.96$, so $\mathbf{d}_3$ first, then $\mathbf{d}_1$, then $\mathbf{d}_2$. 3. $10 \times 4096 = 40{,}960$.
