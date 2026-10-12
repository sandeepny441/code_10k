# 14 · Solution Step 4: Learn From a Teacher

## 1. Goal of this step

Give the projection head something to aim at, so its vectors land in the **existing** embedding space and the existing document index keeps working.

## 2. What the paper does

It uses **knowledge distillation** (Hinton et al., 2015): a small *student* learns by imitating a trained *teacher*.

| Role | Model | During training | After training |
|---|---|---|---|
| Teacher $E$ | Qwen3-Embedding-8B | Encodes each training query text $q^{(j)}$ into $\mathbf{y}^{(j)} = E(q^{(j)})$. Also supplies document vectors $\mathbf{d}_k$ from the index. | **Removed** |
| Student $f$ | Projection head | Reads $\mathbf{H}^{(j)}$ and outputs $f(\mathbf{H}^{(j)})$, which should be close to $\mathbf{y}^{(j)}$. | Used for every search |
| LLM | Qwen3-8B | Produces $\mathbf{H}^{(j)}$ and the query text. Not trained. | Used as usual |

Each training example is a pair: *(hidden states from the LLM, the teacher's vector for the text the LLM wrote)*.

## 3. Why it is done this way

- **No relevance labels needed for the main signal.** The teacher's vector *is* the label, so any conversation the LLM can run through can become training data.
- **The index stays.** The documents were embedded by the teacher. If the student speaks the teacher's language, those stored vectors remain valid. No re-indexing of the collection.
- **Same-family pairing.** Qwen3-8B and Qwen3-Embedding-8B come from the same model family, so their internal representations may already be somewhat similar, which makes the translation easier. The paper names this as a limitation too: cross-family pairs are untested.

This is distillation with an unusual twist. Normally distillation **compresses** a big encoder into a small encoder. Here the goal is to **eliminate** the encoder: the student isn't a standalone model reading text; it is a head bolted onto a different model.

## 4. Which problem it answers

**Problem 1:** after training, one model (plus a tiny head) does the job, and the index, the most expensive thing to rebuild, is untouched.

## 5. What could go wrong

- **The teacher is still needed for training**, and again whenever the LLM changes.
- **The ceiling is the teacher.** A student trained to copy the teacher is rewarded for matching it, not for beating it. Even if hidden states "know more" than the query text, the training target doesn't reward using that extra knowledge. (Discussed in `08` and `19`.)
- **Distribution shift.** The student learns from the teacher's behavior on training queries. New kinds of queries, or new documents, may be handled less well. The paper lists this as untested.

→ **Math:** the training batch, teacher vectors and student vectors are laid out in `math/07_training_batch.md`.
