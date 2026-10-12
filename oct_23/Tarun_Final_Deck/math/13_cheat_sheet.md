# 13 · Cheat Sheet

## Inference

| Step | Formula | Toy numbers | Paper sizes | File |
|---|---|---|---|---|
| Hidden states | $\mathbf{H} = [\mathbf{h}_1;\dots;\mathbf{h}_n]$ | $[1,0,2]$, $[0,1,1]$ | $n \times 4096$ | 00 |
| 1. Input projection | $\mathbf{X} = \mathbf{H}\mathbf{W}_{\text{in}} + \mathbf{b}_{\text{in}}$ | $[3,2]$, $[1,2]$ | $4096 \to 1024$ | 02 |
| 2. Encoder | positions + attention (+FFN) | $[2.5,2]$, $[1.5,2]$ | 2 layers, 8 heads | 03 |
| 3. Mean pooling | $\mathbf{p} = \frac{1}{n}\sum \mathbf{x}_i$ (mask pads) | $[2,2]$ | 1,024 | 04 |
| 4. Output + normalize | $f = \mathbf{z}/\lVert\mathbf{z}\rVert$, $\mathbf{z} = \mathbf{p}\mathbf{W}_{\text{out}} + \mathbf{b}_{\text{out}}$ | $[3,4] \to [0.6,0.8]$ | $1024 \to 1024$ | 05 |
| 5. Search | $\hat{s}_k = f(\mathbf{H})\cdot\mathbf{d}_k$ | 1.0, 0.8, 0.6 | top 10 | 06 |

## Training

| Loss | Formula | Toy | Paper setting | Catches | File |
|---|---|---|---|---|---|
| Alignment | $1 - \frac{1}{B}\sum_j\cos(f^{(j)}, \mathbf{y}^{(j)})$ | 0.04 | $\lambda_a = 0.5$ | wrong direction | 08 |
| Contrastive | $-\frac{1}{B}\sum_j \log\mathrm{softmax}_k(f^{(j)}\cdot\mathbf{y}^{(k)}/\tau)_j$ | 0.304 ($\tau$=0.1) | $\lambda_c = 0.5$, $\tau = 0.05$ | confusable queries | 09 |
| Rank | $\mathrm{KL}(\mathrm{softmax}(\mathbf{s}/\tau_r)\Vert\mathrm{softmax}(\hat{\mathbf{s}}/\tau_r))$ | 0.181 ($\tau_r$=0.2) | $\lambda_r = 0.5$, $\tau_r = 0.05$, $K = 128$ | wrong order | 10 |
| Total | $\lambda_a\mathcal{L}_a + \lambda_c\mathcal{L}_c + \lambda_r\mathcal{L}_r$ | 0.525 (all $\lambda$ = 1) | — | — | 11 |

## Gradients worth remembering

| Where | Gradient | Meaning |
|---|---|---|
| Alignment, w.r.t. raw output $\mathbf{z}$ | $-(\mathbf{y} - (\mathbf{u}\cdot\mathbf{y})\mathbf{u})/\lVert\mathbf{z}\rVert$ | Turn toward the teacher; never stretch |
| Contrastive, w.r.t. grid entry $jk$ | $(P_{jk} - [k=j])/\tau$ | Prediction minus truth, sharpened |
| Rank, w.r.t. student score $\hat{s}_k$ | $(Q_k - P_k)/\tau_r$ | Raise under-scored docs, lower over-scored ones |

## Optimization (paper)

AdamW ($\beta = 0.9, 0.999$; weight decay $10^{-4}$), cosine LR $2\times10^{-4} \to 10^{-5}$ over 80 epochs, batch 16, clip norm 1.0.

## Five facts that explain most of the paper

1. Unit vectors → dot product = cosine = (up to a constant) distance.
2. Normalization means training can only **turn** the output, never stretch it.
3. Small temperatures focus learning on near-ties.
4. Softmax ignores shifts, so rank loss has no anchor and collapses alone.
5. Adam cares about the ratio of the $\lambda$s, not their size.
