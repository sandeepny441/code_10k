The goal of this whole block is simple: take the LLM’s private thoughts (hidden states) and turn them into a search vector that can look up documents the same way a normal embedding model would.

## What the projection head does

After the LLM writes a search query, it already has a list of internal vectors, one per token. Call that list H\mathbf{H}H. Those vectors are the wrong size and shape for your document index, so a small network fff remaps them.

**1. Input projection**

X=HWin+bin\mathbf{X} = \mathbf{H} \mathbf{W}_{\text{in}} + \mathbf{b}_{\text{in}}X=HWin​+bin​

Each token vector is multiplied by a learned matrix and shifted. That only changes the width of the vectors (from the LLM size dhd_hdh​ to an internal size dmd_mdm​). Think of it as a unit conversion so the next layers can work comfortably.

**2. Transformer encoder**

Position markers are added so the model knows token order. Then a few transformer layers let every token look at every other token. That mixes the sequence so later pooling is not just “average of isolated words,” but an average of tokens that already know about each other.

**3. Pooling**

p=1n∑i=1nxi\mathbf{p} = \frac{1}{n} \sum_{i=1}^{n} \mathbf{x}_ip=n1​i=1∑n​xi​

You now have many vectors and need one. Mean pooling takes the average of the valid (non-padding) token vectors. Result: one vector p\mathbf{p}p that stands for the whole query.

**4. Output projection and L2 normalize**

f(H)=pWout+bout∥pWout+bout∥2f(\mathbf{H}) = \frac{\mathbf{p} \mathbf{W}_{\text{out}} + \mathbf{b}_{\text{out}}}{\|\mathbf{p} \mathbf{W}_{\text{out}} + \mathbf{b}_{\text{out}}\|_2}f(H)=∥pWout​+bout​∥2​pWout​+bout​​

Another linear layer changes the width to the teacher embedding size ddd. Then you divide by the vector’s length so the result has length 1. After that, a dot product between two vectors equals cosine similarity, which is what the retrieval index expects.

So at inference: LLM hidden states → these four steps → one unit-length search vector. No separate embedding model.

## How it is trained (three losses)

You have a teacher embedding model EEE. For each training query, you already know the “correct” vector y=E(q)\mathbf{y} = E(q)y=E(q). The student outputs f(H)f(\mathbf{H})f(H). You push the student toward the teacher with three different pressures.

**Alignment loss**

Lalign=1−1B∑j=1Bcos⁡(f(H(j)),  y(j))\mathcal{L}_{\text{align}} = 1 - \frac{1}{B}\sum_{j=1}^{B}\cos\big(f(\mathbf{H}^{(j)}),\; \mathbf{y}^{(j)}\big)Lalign​=1−B1​j=1∑B​cos(f(H(j)),y(j))

Cosine similarity is 1 when two vectors point the same way. So 1−average cosine1 - \text{average cosine}1−average cosine is 0 when student and teacher match, and larger when they disagree. This is the direct “point at the same place as the teacher” signal.

**Contrastive loss (InfoNCE)**

Lcontra=−1B∑j=1Blog⁡exp⁡(f(H(j))⋅y(j)/τ)∑k=1Bexp⁡(f(H(j))⋅y(k)/τ)\mathcal{L}_{\text{contra}} = -\frac{1}{B}\sum_{j=1}^{B}\log \frac{\exp(f(\mathbf{H}^{(j)})\cdot\mathbf{y}^{(j)}/\tau)}{\sum_{k=1}^{B}\exp(f(\mathbf{H}^{(j)})\cdot\mathbf{y}^{(k)}/\tau)}Lcontra​=−B1​j=1∑B​log∑k=1B​exp(f(H(j))⋅y(k)/τ)exp(f(H(j))⋅y(j)/τ)​

Inside a batch, for student vector jjj, compare it to every teacher vector in the batch. The fraction is large when the match to its own teacher is much bigger than the match to other teachers. The log and the leading minus turn that into a loss you minimize. Temperature τ\tauτ controls how sharp that comparison is (smaller τ\tauτ = harsher).

In short: alignment says “match your teacher.” Contrastive says “match your teacher _more than_ the other teachers in the batch,” which keeps queries separable.

**Rank distillation loss**

For each query, take the teacher’s top-KKK documents and their teacher scores sk=y⋅dks_k = \mathbf{y}\cdot\mathbf{d}_ksk​=y⋅dk​. The student scores the same documents: s^k=f(H)⋅dk\hat{s}_k = f(\mathbf{H})\cdot\mathbf{d}_ks^k​=f(H)⋅dk​. Softmax turns each score list into a probability distribution over documents. KL divergence measures how different those two distributions are.

Lrank=KL(softmax(s/τr) ∥ softmax(s^/τr))\mathcal{L}_{\text{rank}} = \mathrm{KL}\big(\mathrm{softmax}(\mathbf{s}/\tau_r)\,\|\,\mathrm{softmax}(\hat{\mathbf{s}}/\tau_r)\big)Lrank​=KL(softmax(s/τr​)∥softmax(s^/τr​))

So this does not only say “look like the teacher vector.” It says “rank documents in the same order the teacher would.”

**Combined loss**

L=λaLalign+λcLcontra+λrLrank\mathcal{L} = \lambda_a\mathcal{L}_{\text{align}} + \lambda_c\mathcal{L}_{\text{contra}} + \lambda_r\mathcal{L}_{\text{rank}}L=λa​Lalign​+λc​Lcontra​+λr​Lrank​

The λ\lambdaλ values are just knobs for how much each pressure matters. AdamW + cosine LR is the optimizer schedule used to minimize L\mathcal{L}L.

## One-sentence map

Hidden states → shrink/mix/average/resize/normalize → search vector; train that map so the vector matches the teacher’s direction (align), stays distinct from other queries (contrastive), and ranks documents like the teacher (rank).

If you want, next I can walk one numerical toy example (2 tokens, tiny dimensions) through pooling and alignment only.