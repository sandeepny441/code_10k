# 12 · Solution Step 2: Keep the Hidden States

## 1. Goal of this step

Collect the right hidden states at the right moment, without adding extra computation.

## 2. What the paper does

While the LLM generates the search query token by token (greedy decoding, up to 32 tokens, using the KV cache), it keeps the **last-layer** hidden state of every generated token:

$$\mathbf{H} = [\mathbf{h}_1; \dots; \mathbf{h}_n] \in \mathbb{R}^{n \times 4096}$$

Details from the paper:

| Choice | Value |
|---|---|
| Which layer | Last layer only |
| Which tokens | Only the generated query tokens; special tokens (BOS, EOS, padding) are removed |
| Precision stored | float32 |
| Max length | 32 generated tokens (positions supported by the head: up to 128) |

## 3. Why it is done this way

- **Last layer:** it has seen the most processing and sits right before word prediction, so it is the most "digested" view. (Other layers might work better, but the paper doesn't test this.)
- **Generated tokens only:** these are the tokens the LLM wrote *because* it wanted to search, so their states are focused on the search intent. Because the LLM is causal, each of them also looks back at the whole conversation.
- **Drop special tokens:** BOS/EOS/PAD states carry formatting information rather than meaning, and would pollute the average later (see `math/04_step_3_mean_pooling.md`).
- **Reuse during generation:** the model computes these vectors anyway. Keeping them costs memory but no extra forward pass.

## 4. Which problem it answers

**Problem 2 (latency):** no second model has to read anything. **Problem 3 (bottleneck):** the states carry context that the text dropped.

## 5. What could go wrong

- **The first query token's state is "early":** it was computed before the rest of the query existed. The head's transformer layers (next file) are there to let later tokens inform earlier ones.
- **Storage during training:** 32 tokens × 4,096 numbers × 4 bytes ≈ 0.5 MB per trace. The paper caches 11,017 traces, which is manageable on disk but not free.
- **Tied to one LLM:** swap Qwen3-8B for another model (or even a fine-tuned Qwen3-8B) and the hidden states change, so the head must be retrained.

→ **Math:** the matrix $\mathbf{H}$ and its toy version are introduced in `math/02_step_1_input_projection.md`.
