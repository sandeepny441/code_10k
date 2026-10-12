**The 30,000-foot view**

Most enterprise data is unstructured—PDFs, scans, forms, tables, charts. For decades the only reliable way to read it was **OCR**: convert pixels to text, then hope a general LLM could make sense of the flattened mess. It failed on layout, reading order, merged cells, handwriting, and visual context. Agents and RAG pipelines inherited the garbage.

**Problem 1:** Text extraction loses meaning.  
**Solution 1:** Treat the page as an image. Use vision models to reason about structure.  
**Why it was incomplete:** Generic vision-language models still hallucinated on messy real-world documents and were slow and expensive at scale.

**Problem 2:** Agents need reliable, structured, grounded input—not just text.  
**Solution 2 (Feb 2025):** Andrew Ng publicly launched **Agentic Document Extraction**. Break the document into components, iterate, and extract meaning the way a human does.  
**Why the next step was needed:** Early versions were still too slow and brittle on complex tables and multi-page files.

**Problem 3:** Production workloads demanded speed and fidelity.  
**Solution 3 (May 2025):** Major speed-up—median processing dropped from roughly two minutes to eight seconds—plus layout-aware parsing and visual grounding.  
**Why still not enough:** Complex tables without gridlines, signatures, checkboxes, and odd scans remained unreliable.

**Problem 4:** Need a specialized model, not a stretched general one.  
**Solution 4 (Sept 2025):** **DPT-2**—Document Pre-trained Transformer. Ng himself posted it as the way to unlock “dark data” in PDFs. Cell-level grounding appeared.  
**Why the remainder of the problem persisted:** Output was still not fully agent-native. Agents received chunks without stable IDs, precise provenance, or clean hierarchical structure. Cost and auditability lagged for regulated work.

**The exact thing Ng is excited about right now (Sept 2026)**

**ADE Gen 2**, announced the ninth of this month. It is a fundamental rebuild, not a patch. The new **DPT-3** models deliver **atomic grounding**: every extracted value points to the exact page, block, line, and word. Parse returns clean, hierarchical Markdown with stable IDs designed for agents. Pricing was overhauled for 25–80 % cost cuts on mixed workloads. An Intelligent Router is coming later this year.

Ng’s long-standing claim is that PDFs are the single most valuable pool of unstructured data. Gen 2 turns that pool into something agents can actually trust—traceable, auditable, and cheap enough to run at volume. That is the pitch: provenance-grade extraction for finance, healthcare, and compliance, where “the model said so” is no longer acceptable.