# 00 · Reading Map

This folder tells the story of the paper in three acts. Each act is broken into small steps so you can stop after any file and still know where you are.

## Act 1: Context (what you need to know first)

| File | Question it answers |
|---|---|
| `01_context_what_agents_retrieve.md` | Why does an AI agent need to look things up at all? |
| `02_context_embeddings.md` | What is an embedding, and how does "similar meaning = nearby point" work? |
| `03_context_the_standard_pipeline.md` | What exactly happens, step by step, in the usual "generate then encode" search? |
| `04_context_hidden_states.md` | What are an LLM's hidden states, and why do they matter here? |

## Act 2: The problems (why the usual way is awkward)

Every problem file follows the same five steps:

1. **What happens** — the behavior in plain words
2. **Why it hurts** — the cost
3. **A concrete example**
4. **How people patched it**
5. **What a real fix would need**

| File | Problem |
|---|---|
| `05_problem_overview.md` | The four problems at a glance and how they connect |
| `06_problem_1_two_models.md` | Running and maintaining two models |
| `07_problem_2_latency.md` | The extra step adds delay |
| `08_problem_3_information_bottleneck.md` | The embedder only sees a short sentence, not the conversation |
| `09_problem_4_why_patches_fall_short.md` | Why query rewriting, HyDE, hybrid search, and LLM-as-embedder don't remove the split |

## Act 3: The solution (built one step at a time)

Every solution step file follows the same five steps:

1. **Goal of this step**
2. **What the paper does**
3. **Why it is done this way**
4. **Which problem it answers**
5. **What could go wrong**

| File | Solution step | Math file(s) that go with it |
|---|---|---|
| `10_solution_overview.md` | The whole idea in one picture | `math/00`, `math/01` |
| `11_solution_step_1_the_core_insight.md` | Reuse what the LLM already computed | — |
| `12_solution_step_2_extract_hidden_states.md` | Keep the hidden states instead of throwing them away | `math/02` |
| `13_solution_step_3_the_projection_head.md` | Turn many LLM vectors into one search vector | `math/02` → `math/06` |
| `14_solution_step_4_learn_from_a_teacher.md` | Copy an existing embedder so the old index still works | `math/07` |
| `15_solution_step_5_three_losses.md` | Why one loss isn't enough | `math/08` → `math/11` |
| `16_solution_step_6_training_and_deployment.md` | How it is trained and how it runs afterwards | `math/12` |

## Act 4: Did it work?

| File | Question |
|---|---|
| `17_results_how_it_is_measured.md` | What do Recall@10, MRR, nDCG, McNemar and confidence intervals mean? |
| `18_results_what_the_experiments_show.md` | Main result, ablations, training recipe, failures |
| `19_critical_reading_and_limitations.md` | What the paper does *not* show, and a few numbers worth double-checking |
