# 19 · Reading the Paper Critically

A good way to understand a paper is to ask what it *didn't* show. This file collects the paper's own stated limitations and a few extra points that are worth checking yourself.

## Step 1: Limitations the paper states

| Limitation | Why it matters |
|---|---|
| **One dataset** (QReCC) | Other domains, languages or document types may behave differently. |
| **Same-family models** (Qwen3-8B → Qwen3-Embedding-8B) | Siblings may share internal structure. Mapping into an unrelated embedder is probably harder. |
| **Still worse than baseline**, significantly | It's a trade: speed and simplicity for a few points of quality. |
| **Teacher needed for training** | Only deployment is simplified. |
| **Unknown generalization to new documents** | Not tested whether the head holds up when the collection changes. |

## Step 2: The motivation vs. the evidence

The strongest argument in the introduction is Problem 3: hidden states are *richer* than query text. But:

- The student is trained to **match the teacher**, and the teacher only sees query text. So training rewards reproducing the text-based vector, not going beyond it.
- No experiment tests whether the hidden states actually carry extra, useful context (for example, a variant trained on relevance labels, or one that also reads hidden states from the conversation itself).
- The result, slightly *below* the teacher, is what you would expect from good imitation, not from exploiting extra information.

So the paper shows **"nearly as good, much cheaper"**. It doesn't yet show **"better because of richer context"**. That is an open and interesting next step.

## Step 3: Numbers worth double-checking

These are not necessarily errors; they are places where the text is ambiguous, and a careful reader should notice them.

| Item | What the paper says | What to notice |
|---|---|---|
| **"Retains 97%"** | Headline claim; "95–97%" in Section 5.1. | The gaps (−3.0, −3.6, −3.5) are in points. Relative retention is 95.3% (Recall), 89.1% (MRR), 91.3% (nDCG). |
| **Test set size** | 2,189 retrieval triggers in the whole split, divided into train/val/test by conversation. | The test win/tie/loss counts add up to 140 + 1843 + 206 = **2,189**, the full number, and the per-conversation analysis covers all **346** conversations. Either the test set is the full set, or the counts are over everything. It isn't clear which. |
| **Latency** | 43.5 ms vs 2.0 ms, 21.8×. | Compares only the encode step. Both pipelines still generate the query with the 8B LLM, which usually takes much longer than 43.5 ms. End-to-end speedup is far smaller than 21.8×. |
| **"Avoid text generation for retrieval altogether"** | Said when contrasting with HyDE. | The method still generates the query text; its hidden states come from exactly that generation. It avoids *extra* generation (compared to HyDE) and *re-encoding*, not generation. |
| **~25M parameters** | Section 4.4. | Counting the listed layers (4096→1024 input, 2 layers with FFN 4096, 1024→1024 output, 128 positions) gives about 30.6M. Close enough to be "tiny", but not 25M. |
| **Randomness** | Bootstrap CIs over test triggers. | These capture test-set noise, not training noise. There is no mention of multiple training seeds, which matters because training is sensitive (lr 5e-4 collapses). |

## Step 4: Questions to think about

1. Would a cross-family pair (say, a Llama LLM and a different embedder) still reach 95%?
2. Could training on real relevance labels, in addition to the teacher, let the student *beat* the teacher?
3. Which hidden layer is best? Only the last one was tried.
4. Would attention pooling or last-token pooling beat mean pooling?
5. Could the query text be skipped entirely by projecting from the hidden state at the moment the model *decides* to search?

## Step 5: The fair summary

The paper identifies a real redundancy, proposes a simple and cheap fix, and shows with careful ablations and proper statistics that a ~25–30M head can stand in for an 8B embedder at a small quality cost, with a large saving in the encode step. The bigger promise, that searching with the LLM's own thoughts could beat searching with its words, is still to be demonstrated.
