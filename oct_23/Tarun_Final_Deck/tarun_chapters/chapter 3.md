**5 bullets (the problem, before the fix)**

- **What broke:** Agents look things up by writing a search sentence, then a *second* embedding model turns that sentence into a vector. The chat model already understood the whole conversation internally, but that understanding is thrown away and rebuilt from a short string.

- **Why that’s a problem:** Extra model, extra hop, extra delay and ops cost. The embedder never sees the raw dialogue — only a lossy rewrite — so follow-ups, “that,” and earlier constraints get flattened.

- **What people tried:** Better query rewriting (make the sentence self-contained). HyDE (write a fake answer document, then embed it). Hybrid keyword + vector search. Bigger / LLM-based embedders (LLM2Vec, NV-Embed) in a separate embedding pass.

- **Why those still fail the core issue:** They improve the *text you hand to the second model*, or they *are* a second model. You still run another forward pass, still maintain two stacks, still discard the hidden states the agent already paid to compute.

- **What was missing:** A way to turn the agent’s existing thoughts into an index-compatible vector *during the same generation*, so retrieval doesn’t need a specialist embedder at serve time. That’s the gap the projection-head paper targets.


**Situation**  
Agents that look up documents used a two-model habit: the chat model writes a search sentence, a separate embedder turns that sentence into a vector, then a vector index returns nearby docs. The chat model already held the full conversation in its hidden states, but those states were discarded. Teams tried query rewriting, HyDE, hybrid search, and LLM-as-embedder models. Those helped the *text* or added a better second encoder. They did not remove the extra hop, the extra model, or the lost context.

**Task**  
Keep retrieval quality close to generate-then-encode, on multi-turn search (QReCC), without calling a standalone embedder at inference. Use the hidden states the agent already computes while writing the query. Land those states in the *same* vector space as the existing document index.

**Action**  
Freeze the chat LLM. While it generates the query, cache last-layer hidden states for real tokens. Run a small projection head (~25M params): linear squeeze → two transformer layers → mean pool → map to teacher dimension → L2-normalize. Distill from a same-family teacher embedder with three losses: alignment (match the teacher vector), contrastive (keep queries distinct), rank distillation (copy document order). Train only the head on cached traces; leave documents indexed as before.

**Result**  
On QReCC, Recall@10 / MRR / nDCG stay about 95–97% of the two-model baseline. Encode-side latency drops from ~44 ms to ~2 ms because the second big model is gone at serve time. Most queries agree with the old pipeline; misses cluster on messy or rare dialogues. The teacher is still needed to *train* the head, not to *serve* each search.




**STAR** is just a four-box story:  
**Situation** — what was going on.  
**Task** — what you had to get done.  
**Action** — what you actually did.  
**Result** — what changed.

That’s it. Interviewers use it so answers don’t wander.

---

**This paper, in those four boxes (plain English)**

**Situation**  
Chatbots that look up documents used two brains. Brain 1 talks and writes a short search sentence. Brain 2 (the embedder) turns that sentence into numbers so a library can find similar pages. Brain 1 had already “understood” the whole chat inside itself, then threw that away. Extra cost, extra wait, and the second brain only saw a skinny sentence.

**Task**  
Keep finding the right pages almost as well as before, but stop calling Brain 2 every time someone searches. Use the understanding Brain 1 already built.

**Action**  
While Brain 1 writes the search sentence, save its internal snapshots. Train a tiny add-on to turn those snapshots into the same kind of numbers the library already uses. Teach the add-on by copying a good embedder: “point the same way, keep different questions apart, rank the same articles in the same order.” After class, Brain 2 can go home at search time.

**Result**  
Hits stay close to the old two-brain setup (a few points worse). Making the search numbers gets much faster. The library of documents does not change. You still need Brain 2 to *train* the add-on, not to *answer* each lookup.