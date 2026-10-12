**10 simple bullets (how it’s solved)**

- Agent already thinks through the chat and starts writing a search sentence.
- While it writes, keep the internal number-snapshots (hidden states) instead of throwing them away.
- Don’t send that sentence to a second embedding model at search time.
- Feed the snapshots into a tiny extra network (the projection head).
- That head squashes a whole sequence of snapshots into one vector.
- Train the head to copy a teacher embedder’s vectors and rankings.
- Three training pressures: match the teacher’s vector, keep queries distinct, copy document order.
- After training, documents stay in the old index; only the query vector is new.
- Search is ordinary nearest-neighbor in that same space.
- Result: almost the same hits, no second big model on every lookup.

**10-step internals (each step feeds the next)**

**1.** A user and an agent are mid-conversation. The agent decides it needs a document. In the old world it would type a standalone search sentence and hand that sentence to another model. Here the same writing process is the raw material: as the agent generates those search tokens, every layer of the LLM has already mixed the full chat history into its last-layer hidden state at each new token. Those states are the “thoughts,” not the printed words.

**2.** At each generation step the model already computes that last-layer vector to pick the next word. The paper’s first trick is bookkeeping: save those vectors for real tokens and drop BOS/EOS/padding. You get a short film strip — one frame per generated word — instead of a single sentence sitting in a text box. No extra forward pass; you just don’t delete the byproduct.

**3.** A film strip is the wrong shape for a search index. Indexes want one fixed-length vector per query. So the strip goes into a small projection head: first a linear layer that changes the LLM’s fat hidden size (here 4096) into a slimmer internal size (1024). Same story, fewer columns, ready for a tiny transformer.

**4.** That slimmer sequence plus learned position tags is run through two transformer encoder layers. Self-attention lets later words look at earlier ones inside the *generated query*, so the head can weigh “it” against “the paper from turn two” even though the LLM’s own attention was causal when it wrote. This is the moment scattered thoughts become one coordinated sketch.

**5.** After those layers, mean-pool the valid positions: average the frames into one vector. Then a last linear map sends that vector into the teacher embedder’s dimension (here 1024) and L2-normalize it. Normalization is the handshake with the index: dot product now means “same direction,” same rule the document vectors already follow.

**6.** At this point you have a student vector that *could* be used for search, but it starts as random scribble. Training pairs each cached hidden-state strip with the teacher’s embedding of the *same* generated query. Alignment loss pulls student and teacher toward the same angle. That plants the student in the right neighborhood of the existing document space instead of inventing a private map.

**7.** Alignment alone can make every query a bland lookalike of its teacher. Contrastive (InfoNCE) adds peer pressure inside a batch: student-A must prefer teacher-A over teacher-B, C, D. Queries stay spread out so retrieval can tell them apart, not just copy one point at a time.

**8.** Search cares about *order of documents*, not only looking like the teacher. Rank distillation takes the teacher’s top-K docs and their scores, turns those scores into a soft ranking, and asks the student to produce a similar ranking when it dots its vector with the same docs. Ranking without alignment collapses — you can’t order books if you don’t know which room the library is in — so this loss rides on top of the first two.

**9.** Combined loss is a weighted mix of those three. The LLM stays frozen; only the ~25M-parameter head learns. They cache hidden-state traces once, then train the head quickly. Too-greedy learning rates wipe the map; slower, longer training lets the geometry settle. After this, the teacher embedder can leave the serving path.

**10.** At inference the loop is: agent generates (and we keep hidden states) → head → one vector → cosine search on the unchanged document index → documents back into the agent. Quality on QReCC is a few points under generate-then-encode; latency of the encode step drops because the second giant model is gone. Failures bunch on weird dialogues, which is what you’d expect from a small translator sitting between two different ways of “meaning.”