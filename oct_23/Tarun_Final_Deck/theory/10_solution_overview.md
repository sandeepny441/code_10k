# 10 · The Solution at a Glance

## One sentence

Attach a small network, the **projection head**, to the LLM. It turns the hidden states the LLM produced while writing the query into a vector that lives in the **same space** as the existing embedding model's vectors, so the existing document index can be searched without running the embedder.

## Before and after

```
BEFORE (two models at search time)
conversation ─► [ LLM ] ─ text ─► [ Embedder E, 8B ] ─ vector ─► [ Index ] ─► docs

AFTER (one model at search time)
conversation ─► [ LLM ] ─ hidden states H ─► [ Projection head f, ~25M ] ─ vector ─► [ same Index ] ─► docs
```

The index doesn't change. Only the thing that produces the query vector changes.

## The six solution steps

| Step | File | Idea | Fixes |
|---|---|---|---|
| 1 | `11` | **Core insight:** the LLM already holds what the search needs. | Frames all four problems |
| 2 | `12` | **Extract hidden states** during normal generation, at no extra compute. | Problem 2 |
| 3 | `13` | **Projection head:** resize → mix → average → resize → normalize. | Problems 1, 2, 3 |
| 4 | `14` | **Learn from a teacher:** train the head to copy the existing embedder, so the old index still works. | Problem 1 (keeps the index) |
| 5 | `15` | **Three losses:** alignment, contrastive, rank distillation, each catching a different mistake. | Makes the copy good enough to use |
| 6 | `16` | **Training recipe and deployment:** cache traces, train slowly, then drop the teacher. | Problems 1, 2 at inference |

## The names to remember

| Name | Symbol | Role |
|---|---|---|
| LLM (agent) | — | Qwen3-8B. Writes queries, produces hidden states. **Frozen**, never trained here. |
| Teacher | $E$ | Qwen3-Embedding-8B. Built the index. Gives the "correct" query vectors during training. **Frozen.** Not needed after training. |
| Student | $f$ | The projection head. The **only** part that is trained. |
| Hidden states | $\mathbf{H}$ | Input to the student. |
| Teacher vector | $\mathbf{y} = E(q)$ | The target the student is trained to match. |

## The math, in one place

The worked example follows this whole pipeline with tiny numbers. Start with `math/00_the_cast.md` and `math/01_math_toolkit.md` if you haven't already.
