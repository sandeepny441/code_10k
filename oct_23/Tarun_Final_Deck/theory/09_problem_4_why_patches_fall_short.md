# 09 · Problem 4: Why the Known Patches Keep the Split

People have noticed problems 1–3 before. Each popular fix improves something, but each **keeps two separate "brains"**: one to talk, one to point at memory.

## Step 1: What happens

Look at each patch and ask two questions: *Does it still need a separate encoder at search time?* and *Does it add work?*

| Patch | What it does | Separate encoder still needed? | Extra work |
|---|---|---|---|
| **Query rewriting** | LLM writes a self-contained query using the dialogue history. | Yes | None beyond generation |
| **HyDE** (Gao et al., 2022) | LLM writes a *fake answer document*, and that is embedded instead of the query. Fake answers look more like real documents. | Yes | Much more text to generate |
| **Hybrid search** | Combine keyword search (e.g. BM25) with vector search. | Yes, plus a keyword index | A second index and a way to merge results |
| **Bigger embedders** | Use a stronger encoder. | Yes | More compute per query |
| **LLM2Vec / NV-Embed** | Turn an LLM *into* an embedding model (bidirectional attention, special pooling, contrastive training). | Yes. It is a second model, or a second forward pass in "embedding mode". | A full extra pass |

## Step 2: Why it hurts

Every patch treats the symptom (bad or thin query text) and leaves the structure (throw away the LLM's understanding, re-read the text) in place. Some make Problems 1 and 2 **worse**: HyDE generates more text, hybrid adds a second index.

## Step 3: A concrete example

With HyDE, the query "cat food" might become a 100-token fake paragraph: *"Choosing a food for your cat depends on age and health. Senior cats with kidney issues benefit from…"*. The fake paragraph is then embedded. Quality may improve, but you now pay for 100 generated tokens **and** the embedder pass.

## Step 4: The closest relatives

LLM2Vec and NV-Embed deserve special attention, because they also use an LLM's hidden states for embeddings. The difference is **when**:

| | LLM2Vec / NV-Embed | This paper |
|---|---|---|
| Whose hidden states? | A modified LLM running specially in embedding mode | The *same* agent LLM, during its normal generation |
| Extra forward pass? | Yes | No, the states are reused |
| Extra network | Pooling or a full model | ~25M-parameter head |
| Goal | A better embedding model | No embedding model at search time |

## Step 5: What a real fix would need

Stop re-reading. Use the representation that already exists at the moment the agent decides to search, and add as little new machinery as possible.

→ That is the core insight in `11`.
