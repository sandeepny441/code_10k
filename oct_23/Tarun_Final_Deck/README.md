# Study Guide: "One Model Is Enough"

A companion folder for understanding the paper *One Model Is Enough: Native Retrieval Embeddings from LLM Agent Hidden States* (Bo Jiang, 2026).

The guide is split in two:

| Folder | What it is for | How to read it |
|---|---|---|
| [`theory/`](theory/00_reading_map.md) | The *story*: the background you need, the problems with the old way, and the solution built up one step at a time. Very few formulas. | In order, from `00` to `19`. |
| [`math/`](math/README.md) | The *numbers*: one file per step of the Chapter 6 worked example, going deeper than the worked example could. Every calculation can be checked by hand. | In order, or jump to the step you are stuck on. |

## Suggested path

1. Read `theory/01` to `theory/04` (context).
2. Read `theory/05` to `theory/09` (the problems).
3. Read `theory/10` to `theory/16` (the solution). Each solution file points to the math file that goes with it. Open that math file the first time you see it mentioned.
4. Read `theory/17` to `theory/19` (results, what they mean, and a critical look at the paper).

## The running example

Both folders reuse the same toy search from the worked example so nothing has to be learned twice:

- Query: **"cat food"** (and a second query, **"cat toys"**, for training)
- Documents: **"Cat behavior guide"** $[1, 0]$, **"Pizza recipes"** $[0, 1]$, **"Healthy dry food for cats"** $[0.6, 0.8]$
- Teacher vector for "cat food": $[0.8, 0.6]$

All toy numbers in the math folder were re-checked with code.
