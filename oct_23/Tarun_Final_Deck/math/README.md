# Math Folder: One File per Step

Each file takes **one step** of the Chapter 6 worked example and goes deeper than the worked example had room for. Every file has the same layout:

1. **Where we are**: the step in one paragraph and where it sits in the pipeline
2. **The formula, symbol by symbol**
3. **Shapes: toy vs. real**: the sizes in the example next to the sizes in the paper
4. **The worked numbers**: the calculation from the worked example, redone
5. **Going deeper**: something the worked example skipped
6. **Common mistakes**
7. **Check yourself**: small exercises, with answers at the bottom

| File | Step | Theory file |
|---|---|---|
| `00_the_cast.md` | The query, documents, teacher, student, toy sizes | `theory/10` |
| `01_math_toolkit.md` | Vectors, dot product, norm, cosine, matrices, $e^x$, log, softmax, KL | `theory/02` |
| **Part 1: Inference** | | |
| `02_step_1_input_projection.md` | $\mathbf{X} = \mathbf{H}\mathbf{W}_{\text{in}} + \mathbf{b}_{\text{in}}$ | `theory/12`, `13` |
| `03_step_2_transformer_encoder.md` | Positions + self-attention | `theory/13` |
| `04_step_3_mean_pooling.md` | $\mathbf{p} = \frac{1}{n}\sum \mathbf{x}_i$, with masking | `theory/13` |
| `05_step_4_output_projection_and_normalization.md` | Resize to $d$, divide by length | `theory/13` |
| `06_step_5_searching_the_index.md` | Dot products with documents, ranking, metrics | `theory/13`, `17` |
| **Part 2: Training** | | |
| `07_training_batch.md` | Teacher and student vectors for a batch | `theory/14` |
| `08_loss_1_alignment.md` | $1 - \text{mean cosine}$ | `theory/15` |
| `09_loss_2_contrastive_infonce.md` | InfoNCE with temperature | `theory/15` |
| `10_loss_3_rank_distillation.md` | KL between ranking distributions | `theory/15` |
| `11_combining_the_losses.md` | Weighted sum | `theory/15` |
| `12_updating_the_weights.md` | Gradients, AdamW, clipping, cosine schedule | `theory/16` |
| `13_cheat_sheet.md` | Everything on one page, toy and real | — |

Every new number in these files (numbers not in the original worked example) was checked with a short script.
