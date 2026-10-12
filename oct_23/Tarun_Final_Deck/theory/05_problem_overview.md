# 05 · The Problems at a Glance

The paper's main complaint is a single word: **redundancy**. The LLM understands the situation, writes a summary of that understanding as text, and then a second model re-reads the summary to rebuild an understanding the first model already had.

That redundancy shows up as four problems.

| # | Problem | One-line description | Kind of cost |
|---|---|---|---|
| 1 | **Two models** | You must deploy, pay for, and keep in sync two large networks. | Money, engineering |
| 2 | **Latency** | The second model adds a full forward pass to every search. | Time |
| 3 | **Information bottleneck** | The embedder only sees the short query text, not the conversation. | Search quality |
| 4 | **Patches don't remove the split** | Known fixes improve quality but keep, or even add to, the two-model setup. | All of the above |

## How they connect

```
            The LLM already understands the conversation
                              │
                 but hands over only a short string
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
  a 2nd model is needed   that model takes    the string loses
  to read the string      extra time          context
   (Problem 1)            (Problem 2)          (Problem 3)
         └────────────────────┼────────────────────┘
                              ▼
          people patch 3, but the patches keep 1 and 2
                         (Problem 4)
```

Problems 1 and 2 are about **cost**. Problem 3 is about **quality**. Problem 4 explains why the field hasn't simply fixed this already.

## A fair warning before you read on

The paper argues all four, but its experiments measure them unevenly:

- Problem 2 (latency) is **measured** directly: 43.5 ms vs 2.0 ms.
- Problem 1 (two models) is removed **at inference time only**; the teacher is still needed for training.
- Problem 3 (bottleneck) is the **motivation**, but the experiments don't show the new method beating the baseline on quality. It comes out slightly worse. File `19` discusses this.

Keep asking "was this measured?" as you read.
