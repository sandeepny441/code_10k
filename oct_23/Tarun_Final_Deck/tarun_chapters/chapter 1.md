When an AI agent needs facts it doesn’t already have, it looks things up. For years that lookup used **embeddings**: turn text into a list of numbers so “similar meaning” becomes “nearby points.” Documents get stored as those points. A question gets turned into a point too. Closest neighbors come back as the answer sources.

The usual recipe was two machines. The chat model wrote a short search sentence. A *second* model — the embedder — turned that sentence into numbers. Then a database found nearby documents. That pattern came from search engines and RAG chatbots, then got copied into agents.

It was awkward. You had to run and pay for two models. The extra step added delay. Worse, the embedder only saw the short sentence, not the whole conversation the chat model already understood — so follow-ups and “what we meant earlier” often got flattened.

People patched it with better query writing, HyDE-style fake documents, hybrid keyword+vector search, and bigger embedders. The split stayed: one brain to talk, another to point at memory.

The “one model is enough” idea is: the chat model already built a rich internal picture of the conversation. Attach a small adapter that turns that picture into the same kind of number-list the document index uses. Train the adapter to copy a good embedder. At search time you skip the second model and search with the agent’s own thoughts. Same index, less plumbing, and the search vector can carry the full chat context instead of a squeezed-down sentence.