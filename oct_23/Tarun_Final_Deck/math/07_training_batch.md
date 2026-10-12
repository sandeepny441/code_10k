# 07 · The Training Batch

## 1. Where we are

Part 1 ran the head on one query. Training runs it on many queries at once, a **batch**, and compares with the teacher. This file sets up the batch that files 08–11 use.

## 2. What one training example contains

| Item | Symbol | Comes from | Needed by |
|---|---|---|---|
| Hidden states | $\mathbf{H}^{(j)}$ | LLM trace (cached) | Student input |
| Teacher query vector | $\mathbf{y}^{(j)} = E(q^{(j)})$ | Teacher reading the query text | Alignment, contrastive, rank |
| Teacher's top-$K$ documents | $\mathbf{d}_1, \dots, \mathbf{d}_K$ | Searching the index with $\mathbf{y}^{(j)}$ | Rank |
| Teacher scores | $s_k = \mathbf{y}^{(j)} \cdot \mathbf{d}_k$ | Dot products | Rank |

The superscript $(j)$ means "the $j$-th query in the batch".

## 3. Shapes: toy vs. real

| | Toy | Paper |
|---|---|---|
| Batch size $B$ | 2 | 16 |
| $\mathbf{H}^{(j)}$ | $2 \times 3$ | $n_j \times 4096$, padded to the longest in the batch |
| $\mathbf{y}^{(j)}$ | 2 | 1,024 |
| Top-$K$ docs per query | 3 | 128 |
| Student–teacher dot products for contrastive | $2 \times 2 = 4$ | $16 \times 16 = 256$ |

## 4. The worked numbers

| $j$ | Query | Teacher $\mathbf{y}^{(j)}$ | Student $f(\mathbf{H}^{(j)})$ | Student length |
|---|---|---|---|---|
| 1 | "cat food" | $[0.8, 0.6]$ | $[0.6, 0.8]$ (files 02–05) | 1 |
| 2 | "cat toys" | $[1, 0]$ | $[0.96, 0.28]$ | $\sqrt{0.9216 + 0.0784} = 1$ |

The second query was chosen to be **similar** to the first. Similar queries are where a student is most likely to blur things together, so they make the contrastive loss interesting.

## 5. Going deeper

### Student–teacher similarity matrix

All four dot products, arranged as a grid (rows: students, columns: teachers):

| | $\mathbf{y}^{(1)}$ cat food | $\mathbf{y}^{(2)}$ cat toys |
|---|---|---|
| student 1 | **0.96** | 0.60 |
| student 2 | 0.936 | **0.96** |

The **diagonal** holds the correct pairs. File 08 (alignment) only reads the diagonal. File 09 (contrastive) reads whole rows. File 10 (rank) ignores this grid and looks at documents instead.

### How the training data is produced

1. Run the LLM on training conversations (~2 hours for all of them).
2. At every retrieval trigger, store $\mathbf{H}$ and the query text.
3. Encode the text with the teacher to get $\mathbf{y}$, search to get the top-128 documents.
4. Save everything to disk (11,017 traces).

After that, each training run reads from disk and never loads the 8B models.

### Why conversation-level splits

Queries from the same conversation look alike. If turn 3 were in training and turn 4 in testing, the test would be too easy. The paper assigns whole conversations to train, validation or test.

## 6. Common mistakes

- Thinking the teacher sees hidden states. It only ever sees **text**.
- Forgetting that other queries' teacher vectors are used as "wrong answers" in contrastive loss, so batch composition matters.

## 7. Check yourself

1. How many "wrong" teacher vectors does each student see in a batch of 16?
2. Which entries of the grid does the alignment loss use?
3. Which is the most dangerous off-diagonal entry in the toy grid, and why?

---
**Answers.** 1. 15. 2. Only the diagonal. 3. Student 2 vs teacher 1 (0.936), because it is almost as large as student 2's correct score (0.96).
