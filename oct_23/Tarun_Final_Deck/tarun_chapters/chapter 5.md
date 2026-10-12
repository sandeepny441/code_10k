I can’t paste the full paper verbatim. Here’s a **faithful Markdown digest** with the actual equations, plus the source so you can read the original.

**Source:** Bo Jiang, *One Model Is Enough: Native Retrieval Embeddings from LLM Agent Hidden States*, arXiv:2603.08429, 9 Mar 2026. [arxiv.org/abs/2603.08429](https://arxiv.org/abs/2603.08429) · HTML: [arxiv.org/html/2603.08429v1](https://arxiv.org/html/2603.08429v1) · CC BY 4.0.

---

# One Model Is Enough (technical digest)

## Claim

Standard agent RAG is **generate query text → separate embedder \(E\)**. Hidden states from generation already encode the dialogue. Learn a small \(f\) so \(f(\mathbf{H})\approx E(q)\) and drop \(E\) at inference.

## Problem

\[
\mathbf{v}=E(q),\qquad q=(t_1,\ldots,t_n).
\]

Generation already produces last-layer states \(\mathbf{h}_i\in\mathbb{R}^{d_h}\). Those are discarded; \(E\) re-encodes a lossy string.

## Method

### Extract

Keep non-special last-layer states:

\[
\mathbf{H}=[\mathbf{h}_1;\ldots;\mathbf{h}_n]\in\mathbb{R}^{n\times d_h}.
\]

### Head \(f\)

1. Input map: \(\mathbf{X}=\mathbf{H}\mathbf{W}_{\mathrm{in}}+\mathbf{b}_{\mathrm{in}}\)
2. \(L=2\) transformer encoder layers (internal size \(d_m\))
3. Mean pool: \(\displaystyle\mathbf{p}=\frac1n\sum_{i=1}^n\mathbf{x}_i\)
4. Output + L2:

\[
f(\mathbf{H})=\frac{\mathbf{p}\mathbf{W}_{\mathrm{out}}+\mathbf{b}_{\mathrm{out}}}{\|\mathbf{p}\mathbf{W}_{\mathrm{out}}+\mathbf{b}_{\mathrm{out}}\|_2}
\]

~25M params. Target dim \(d=1024\), LLM hidden \(d_h=4096\).

### Losses (distill teacher \(\mathbf{y}=E(q)\))

**Alignment**

\[
\mathcal{L}_{\mathrm{align}}=1-\frac1B\sum_{j=1}^B\cos\bigl(f(\mathbf{H}^{(j)}),\mathbf{y}^{(j)}\bigr)
\]

**Contrastive (InfoNCE)**

\[
\mathcal{L}_{\mathrm{contra}}=-\frac1B\sum_{j=1}^B\log\frac{\exp\bigl(f(\mathbf{H}^{(j)})\cdot\mathbf{y}^{(j)}/\tau\bigr)}{\sum_{k=1}^B\exp\bigl(f(\mathbf{H}^{(j)})\cdot\mathbf{y}^{(k)}/\tau\bigr)}
\]

**Rank distill** on teacher top-\(K\) docs \(\mathbf{d}_k\):

\[
s_k=\mathbf{y}\cdot\mathbf{d}_k,\quad
\hat s_k=f(\mathbf{H})\cdot\mathbf{d}_k
\]

\[
\mathcal{L}_{\mathrm{rank}}=\mathrm{KL}\bigl(\mathrm{softmax}(\mathbf{s}/\tau_r)\,\|\,\mathrm{softmax}(\hat{\mathbf{s}}/\tau_r)\bigr)
\]

**Total**

\[
\mathcal{L}=\lambda_a\mathcal{L}_{\mathrm{align}}+\lambda_c\mathcal{L}_{\mathrm{contra}}+\lambda_r\mathcal{L}_{\mathrm{rank}}
\]

Best: \(\lambda_a=\lambda_c=\lambda_r=0.5\), \(\tau=\tau_r=0.05\), \(K=128\), 80 epochs, lr \(2\times10^{-4}\). LLM frozen; only \(f\) trained. Traces cached (~2 h), head train ~15–20 min.

## Setup

- Data: QReCC, 346 convos / 2189 triggers, split by conversation  
- Models: Qwen3-8B agent + Qwen3-Embedding-8B teacher (same family)  
- Baseline: greedy rewrite (≤32 toks) → \(E\) → cosine index  

## Results (test)

| | R@10 | MRR@10 | nDCG@10 | p50 encode |
|--|--|--|--|--|
| Baseline | 0.637 | 0.329 | 0.402 | 43.5 ms |
| Ours | 0.607 | 0.293 | 0.367 | 2.0 ms |
| Δ | −3.0% | −3.6% | −3.5% | 21.8× faster |

McNemar \(p=0.0005\); win/tie/loss 140 / 1843 / 206 (~84% agree).

Ablation: align strongest alone; rank-only collapses (~0); all three best; long slow train helps most. High lr (\(5\times10^{-4}\)) collapses.

## Limits

One dataset; same-family only; small but real quality gap; teacher still needed **to train** \(f\); OOD docs untested.

---

For wording, tables, and related-work citations, use the HTML/PDF above. I can turn *this digest* into a study sheet or flashcards next if you want.