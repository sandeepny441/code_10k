# 06 · Step 5: Searching the Index

## 1. Where we are

The student has produced a unit vector. The index holds the teacher's unit document vectors. Search is one dot product per document, then sort.

## 2. The formula, symbol by symbol

$$\hat{s}_k = f(\mathbf{H}) \cdot \mathbf{d}_k \qquad \text{(student score for document } k\text{)}$$
$$s_k = \mathbf{y} \cdot \mathbf{d}_k \qquad \text{(teacher score, for comparison)}$$

Because all vectors have length 1, each score is a cosine similarity between $-1$ and $1$. Return the documents with the highest scores.

## 3. Shapes: toy vs. real

| | Toy | Paper |
|---|---|---|
| Documents | 3 | a pre-built QReCC index |
| Numbers per document | 2 | 1,024 |
| Multiplications per document | 2 | 1,024 |
| Results kept | top 3 | top 10 for evaluation, top 128 for rank distillation |

For a million documents, that is about a billion multiply-adds per search, so real systems usually use approximate nearest-neighbor indexes. This step is **identical** in the baseline and the new method; only where the query vector comes from differs.

## 4. The worked numbers

| Document | Student $[0.6, 0.8]$ | Teacher $[0.8, 0.6]$ |
|---|---|---|
| $\mathbf{d}_1$ Cat behavior $[1,0]$ | $0.6$ | $0.8$ |
| $\mathbf{d}_2$ Pizza $[0,1]$ | $0.8$ | $0.6$ |
| $\mathbf{d}_3$ Dry cat food $[0.6,0.8]$ | $0.36 + 0.64 = 1.0$ | $0.48 + 0.48 = 0.96$ |

| Rank | Student | Teacher |
|---|---|---|
| 1 | Dry cat food (1.0) | Dry cat food (0.96) |
| 2 | **Pizza (0.8)** | Cat behavior (0.8) |
| 3 | Cat behavior (0.6) | Pizza (0.6) |

Right winner, wrong runner-up.

## 5. Going deeper

### Why unnormalized vectors break search

Use the raw $\mathbf{z} = [3, 4]$ instead: scores $3$, $4$, $5$. The order is the same here, but the numbers are 5× larger. Now imagine two queries in a system, one with $\lVert\mathbf{z}\rVert = 5$ and one with $\lVert\mathbf{z}\rVert = 0.5$. A fixed "relevance threshold" (say 0.7) would accept everything for the first and nothing for the second. Normalization makes scores comparable across queries and matches the teacher's scale, which the losses rely on.

### Measuring this search (see theory file 17)

Say the relevant document is $\mathbf{d}_3$.

| Metric | Student | Teacher |
|---|---|---|
| Recall@3 | 1 | 1 |
| Reciprocal rank | $1/1 = 1$ | $1/1 = 1$ |

Both perfect. Now suppose the user actually wanted behavior advice, so the relevant document is $\mathbf{d}_1$:

| Metric | Student (rank 3) | Teacher (rank 2) |
|---|---|---|
| Recall@3 | 1 | 1 |
| Reciprocal rank | $1/3 = 0.333$ | $1/2 = 0.5$ |
| DCG | $1/\log_2 4 = 0.5$ | $1/\log_2 3 = 0.631$ |

The student's food lean costs it on MRR and nDCG, even though recall is the same. This is the kind of loss the paper measures: −3.6 MRR points.

### Where the student and teacher disagree

The student's scores are the teacher's with pizza and cat-behavior swapped, because the student's vector is the teacher's with its coordinates swapped. In high dimensions, small direction errors like this shuffle documents with similar scores, which is why the paper's student agrees with the baseline on 84% of searches but not all.

## 6. Common mistakes

- Comparing a student vector with documents embedded by a **different** model. Scores would be meaningless.
- Thinking the highest score must be 1. It is 1 only when the query vector exactly equals a document vector, as happens by coincidence in the toy.

## 7. Check yourself

1. Score a student vector $[0.8, 0.6]$ against all three documents. What order?
2. A document $[0.707, 0.707]$ is added. Where does the original student rank it?
3. What is the reciprocal rank if the relevant document is 4th and we only look at the top 3?

---
**Answers.** 1. $0.8$, $0.6$, $0.96$: same as the teacher. 2. $0.6(0.707) + 0.8(0.707) = 0.990$, so 2nd, just below dry cat food. 3. 0.
