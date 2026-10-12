# 11 · Solution Step 1: The Core Insight

## 1. Goal of this step

Change the question from "how do we write a better query for the embedder?" to "why do we need the embedder at all?"

## 2. What the paper does

It makes a simple argument:

1. To write a good search query, the LLM must already understand what is being searched for.
2. That understanding exists as numbers, the hidden states, at the moment the query is written.
3. The embedder's job is to produce numbers that capture what is being searched for.
4. So the embedder is **re-deriving**, from a text summary, something the LLM already had in fuller form.
5. Therefore a **small learned translator** from hidden states to embedding space should be enough.

The paper formalizes the goal as learning a function $f$ such that

$$f(\mathbf{h}_1, \dots, \mathbf{h}_n) \approx E(q)$$

"Given the LLM's hidden states while writing query $q$, produce roughly what the embedder would produce from $q$."

## 3. Why it is done this way

Two alternatives are rejected:

| Alternative | Why not |
|---|---|
| Use the hidden states directly as embeddings | Wrong size, wrong count, wrong space (file `04`). Also the index would have to be rebuilt in a new space. |
| Train a new embedding model from the LLM | That is LLM2Vec / NV-Embed: a second model or a second pass. Doesn't remove the redundancy. |

A *small* translator is the middle path. The heavy thinking was done by the LLM, so the translator only has to re-express it.

## 4. Which problem it answers

This step is the thesis. It's the reason the other steps can address Problems 1 (one model), 2 (no second pass) and 3 (use the rich representation, not the thin text).

## 5. What could go wrong

- **The information may not be linearly accessible.** Hidden states are organized for predicting the next word. The facts may be present but tangled. (The paper uses a small transformer, not just a linear map, partly for this reason.)
- **"Approximately" is doing a lot of work.** If $f(\mathbf{H})$ is only close to $E(q)$, some searches will return different documents. The paper finds a small but statistically significant drop (file `18`).
- **The LLM still writes the query.** Hidden states come from generating the query tokens, so generation isn't removed. Only the *encode* step is removed.
