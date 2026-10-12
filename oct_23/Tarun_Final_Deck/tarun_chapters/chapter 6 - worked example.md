# Chapter 6, Worked Example: One Query, One Document, Every Step

This file follows one real-looking search from start to finish. Every table has two columns. The **left column** explains the idea in plain words. The **right column** does the arithmetic with tiny numbers you can check by hand.

The real system uses vectors with thousands of numbers. Here every vector has only 2 or 3 numbers, but each step works exactly the same way.

---

## The cast

| Theory                                                                                                                                                                            | Math                                                                                                           |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **The query.** A user asks the LLM something. The LLM decides to search and writes a short search query.                                                                          | Query: **"cat food"**<br>Tokens: $\text{cat}$, $\text{food}$ (so $n = 2$)                                      |
| **The document.** Somewhere in the index there is a document we hope to find.                                                                                                     | Document: **"Healthy dry food for cats"**                                                                      |
| **Two other documents.** To talk about ranking, we need some competitors.                                                                                                         | **"Cat behavior guide"** and **"Pizza recipes"**                                                               |
| **The teacher.** A normal, already-trained embedding model $E$. It turns text into a vector. All documents in the index were turned into vectors by the teacher, ahead of time.   | Teacher vector for our query:<br>$\mathbf{y} = E(\text{"cat food"}) = [0.8,\ 0.6]$                             |
| **The student.** The small projection network $f$ we are building. It never reads text. It reads the LLM's hidden states and must produce a vector that works like the teacher's. | Student vector: $f(\mathbf{H})$, computed in Part 1                                                            |
| **Toy sizes.** In a real system these are large. We keep them tiny.                                                                                                               | LLM width $d_h = 3$<br>Internal width $d_m = 2$<br>Teacher width $d = 2$                                       |
| **Reading our 2D vectors.** To build intuition, pretend the first number means "about cats" and the second means "about food". Real dimensions have no such clean meaning.        | $[\text{cat-ness},\ \text{food-ness}]$<br>"cat food" teacher $= [0.8,\ 0.6]$: mostly cats, quite a bit of food |

The three documents, as the teacher stored them in the index:

| Theory | Math |
|---|---|
| **"Cat behavior guide"** is about cats and not at all about food. | $\mathbf{d}_1 = [1,\ 0]$ |
| **"Pizza recipes"** is about food and not at all about cats. | $\mathbf{d}_2 = [0,\ 1]$ |
| **"Healthy dry food for cats"** is about both, a little more about food. | $\mathbf{d}_3 = [0.6,\ 0.8]$ |

---

## Part 0: The math toolkit

Everything later uses only these few operations. If any row is unfamiliar, read it twice before moving on.

| Theory | Math |
|---|---|
| **Vector.** An ordered list of numbers. You can think of it as an arrow pointing somewhere. | $[0.6,\ 0.8]$ is an arrow 0.6 to the right and 0.8 up |
| **Dot product.** Multiply matching positions, then add. A big result means the two arrows point in similar directions. | $[0.6, 0.8] \cdot [0.8, 0.6]$<br>$= 0.6 \times 0.8 + 0.8 \times 0.6$<br>$= 0.48 + 0.48 = 0.96$ |
| **Length (L2 norm).** How long the arrow is. Square each number, add them, take the square root. | $\lVert [3, 4] \rVert_2 = \sqrt{3^2 + 4^2} = \sqrt{25} = 5$ |
| **Normalizing.** Divide a vector by its length. The direction stays the same, but the length becomes exactly 1. A length-1 vector is called a *unit vector*. | $[3, 4] / 5 = [0.6,\ 0.8]$<br>Check: $\sqrt{0.36 + 0.64} = 1$ ✓ |
| **Cosine similarity.** Measures only direction, ignoring length. 1 means same direction, 0 means unrelated (at a right angle), −1 means opposite. | $\cos(\mathbf{a}, \mathbf{b}) = \dfrac{\mathbf{a} \cdot \mathbf{b}}{\lVert \mathbf{a} \rVert \, \lVert \mathbf{b} \rVert}$ |
| **The key shortcut.** If both vectors already have length 1, the bottom of the cosine fraction is $1 \times 1$. So the dot product *is* the cosine. This is why we normalize. | For unit vectors:<br>$\cos(\mathbf{a}, \mathbf{b}) = \mathbf{a} \cdot \mathbf{b}$ |
| **Vector times matrix.** A matrix is a grid of numbers. Multiplying a vector by a matrix means taking one dot product per column. The number of columns decides the width of the answer, so this is how we change a vector's size. | $[1, 0, 2]$ times a matrix with columns $[1,0,1]$ and $[0,1,1]$:<br>first: $[1,0,2] \cdot [1,0,1] = 1 + 0 + 2 = 3$<br>second: $[1,0,2] \cdot [0,1,1] = 0 + 0 + 2 = 2$<br>result: $[3,\ 2]$ (3 numbers in, 2 out) |
| **Exponential, $e^x$.** Turns any number into a positive number. Bigger inputs grow very fast. $e \approx 2.718$. | $e^0 = 1$, $e^1 = 2.718$, $e^2 = 7.389$, $e^3 = 20.09$ |
| **Natural log, $\log$.** The reverse of $e^x$. The log of a probability is negative, so losses put a minus sign in front. | $-\log(1) = 0$<br>$-\log(0.5) = 0.693$<br>$-\log(0.1) = 2.303$<br>Confident and right → small loss. Unsure → big loss. |
| **Softmax.** Turns a list of scores into probabilities that are all positive and add up to 1. Apply $e^x$ to each score, then divide each by the total. | Scores $[2, 1, 0]$<br>$e^x$: $[7.389,\ 2.718,\ 1]$, total $= 11.107$<br>softmax $= [0.665,\ 0.245,\ 0.090]$ |
| **KL divergence.** Measures how different two probability lists are. It is 0 when they are identical and grows as they disagree. | $\mathrm{KL}(P \Vert Q) = \sum_k P_k \log \dfrac{P_k}{Q_k}$<br>$P = [0.5, 0.5]$, $Q = [0.5, 0.5]$ → $0$<br>$P = [0.5, 0.5]$, $Q = [0.9, 0.1]$ → $0.5\log\tfrac{0.5}{0.9} + 0.5\log\tfrac{0.5}{0.1} = -0.294 + 0.805 = 0.51$ |

---

## Part 1: Inference, from hidden states to a search vector

This is what happens every time the LLM searches, after training is finished.

### Step 1: Input projection

| Theory | Math |
|---|---|
| **Where we start.** While writing "cat food", the LLM produced one internal vector per token. These are its hidden states, stacked into the matrix $\mathbf{H}$. We don't compute these; the LLM hands them to us. | $\mathbf{h}_{\text{cat}} = [1,\ 0,\ 2]$<br>$\mathbf{h}_{\text{food}} = [0,\ 1,\ 1]$ |
| **The problem.** These vectors have the LLM's width ($d_h = 3$), which isn't the width our small network wants to work with ($d_m = 2$). | 3 numbers per token, but we want 2 |
| **The fix.** Multiply every token by the same learned matrix $\mathbf{W}_{\text{in}}$ and add a learned bias $\mathbf{b}_{\text{in}}$. This is just a resize, like converting units. | $\mathbf{X} = \mathbf{H}\mathbf{W}_{\text{in}} + \mathbf{b}_{\text{in}}$ |
| **Our learned numbers.** $\mathbf{W}_{\text{in}}$ has 3 rows (for 3 inputs) and 2 columns (for 2 outputs). We'll use a bias of zero to keep it simple. | Column 1 of $\mathbf{W}_{\text{in}}$: $[1, 0, 1]$<br>Column 2 of $\mathbf{W}_{\text{in}}$: $[0, 1, 1]$<br>$\mathbf{b}_{\text{in}} = [0,\ 0]$ |
| **Token "cat".** One dot product per column. | $[1,0,2] \cdot [1,0,1] = 3$<br>$[1,0,2] \cdot [0,1,1] = 2$<br>$\mathbf{x}_{\text{cat}} = [3,\ 2]$ |
| **Token "food".** Same matrix, same process. | $[0,1,1] \cdot [1,0,1] = 1$<br>$[0,1,1] \cdot [0,1,1] = 2$<br>$\mathbf{x}_{\text{food}} = [1,\ 2]$ |
| **Result.** Still one vector per token, just a new width. Nothing has been mixed between tokens yet. | $\mathbf{x}_{\text{cat}} = [3, 2]$, $\mathbf{x}_{\text{food}} = [1, 2]$ |

### Step 2: Transformer encoder

| Theory | Math |
|---|---|
| **Position markers.** A transformer by itself doesn't know which token came first. So we add a small "position vector" to each token. In real models these are patterns of small numbers. In our toy they are zero so the arithmetic stays clean. | $\text{pos}_1 = [0, 0]$, $\text{pos}_2 = [0, 0]$<br>$\mathbf{x}_{\text{cat}} = [3,2] + [0,0] = [3, 2]$<br>$\mathbf{x}_{\text{food}} = [1,2] + [0,0] = [1, 2]$ |
| **Why mix tokens at all.** On its own, "cat" could mean the animal, and "food" could mean any food. Together they mean something specific. Each token should carry some meaning from its neighbors before we combine them. | Goal: "cat" learns it is next to "food", and "food" learns it is next to "cat" |
| **Attention, in one sentence.** Each token decides how much to borrow from every token (including itself) and takes a weighted average. The weights come from learned similarity scores passed through softmax, so they add up to 1. | Suppose attention produced these weights:<br>"cat": 75% from itself, 25% from "food"<br>"food": 25% from "cat", 75% from itself |
| **New "cat" vector.** | $0.75 \times [3, 2] + 0.25 \times [1, 2]$<br>$= [2.25, 1.5] + [0.25, 0.5]$<br>$= [2.5,\ 2]$ |
| **New "food" vector.** | $0.25 \times [3, 2] + 0.75 \times [1, 2]$<br>$= [0.75, 0.5] + [0.75, 1.5]$<br>$= [1.5,\ 2]$ |
| **Real encoders do more.** Each layer also has a small feed-forward network, and several layers are stacked. We skip those here because the idea is the same: tokens leave the encoder knowing about each other. | $\mathbf{x}_{\text{cat}} = [2.5, 2]$<br>$\mathbf{x}_{\text{food}} = [1.5, 2]$ |

### Step 3: Mean pooling

| Theory | Math |
|---|---|
| **The problem.** We have one vector per token, but a search needs exactly one vector for the whole query. | Two vectors in, one vector out |
| **The fix.** Take the average. Add the token vectors and divide by how many there are. | $\mathbf{p} = \dfrac{1}{n}\displaystyle\sum_{i=1}^{n} \mathbf{x}_i$ |
| **Our query.** | $\mathbf{p} = \dfrac{[2.5, 2] + [1.5, 2]}{2} = \dfrac{[4, 4]}{2} = [2,\ 2]$ |
| **About padding.** Queries are processed in batches, and short queries are filled out with empty `[PAD]` tokens so they all have the same length. Those pad positions still come out of the encoder with *some* numbers. We must skip them, so we average only the real tokens. | Say our query was padded to 3 tokens, and the pad came out as $[4, -1]$. |
| **Right way:** use a mask that marks real tokens with 1 and pads with 0. | Mask $= [1, 1, 0]$<br>$\mathbf{p} = ([2.5,2] + [1.5,2]) / 2 = [2,\ 2]$ ✓ |
| **Wrong way:** include the pad. The garbage pad values pull the average in a meaningless direction. | $([2.5,2] + [1.5,2] + [4,-1]) / 3 = [2.67,\ 1]$ ✗ |

### Step 4: Output projection and L2 normalization

| Theory | Math |
|---|---|
| **Resize again.** $\mathbf{p}$ has the internal width $d_m$. The index expects the teacher's width $d$. Another learned matrix and bias fix that. Here both widths are 2, so the matrix can be the "do nothing" identity matrix, and the bias does the work. | $\mathbf{W}_{\text{out}}$ = identity (columns $[1,0]$ and $[0,1]$)<br>$\mathbf{b}_{\text{out}} = [1,\ 2]$ |
| **Apply it.** | $\mathbf{p}\mathbf{W}_{\text{out}} = [2, 2]$<br>$[2, 2] + [1, 2] = [3,\ 4]$ |
| **Measure the length.** | $\lVert [3, 4] \rVert_2 = \sqrt{9 + 16} = 5$ |
| **Normalize.** Divide by the length so the vector has length 1. | $f(\mathbf{H}) = [3, 4] / 5 = [0.6,\ 0.8]$ |
| **The full formula** for this step, now that you've seen each piece. | $f(\mathbf{H}) = \dfrac{\mathbf{p}\mathbf{W}_{\text{out}} + \mathbf{b}_{\text{out}}}{\lVert \mathbf{p}\mathbf{W}_{\text{out}} + \mathbf{b}_{\text{out}} \rVert_2}$ |
| **Done.** This is the student's search vector for "cat food". No separate embedding model was run. | $f(\mathbf{H}) = [0.6,\ 0.8]$ |

### Step 5: Searching the index

| Theory | Math |
|---|---|
| **Scoring a document.** The index compares the search vector with each stored document vector using a dot product. Since everything has length 1, each score is a cosine similarity. | score $= f(\mathbf{H}) \cdot \mathbf{d}_k$ |
| **Our target document**, "Healthy dry food for cats". | $[0.6, 0.8] \cdot [0.6, 0.8] = 0.36 + 0.64 = 1.0$ |
| **The competitors.** | "Cat behavior guide": $[0.6, 0.8] \cdot [1, 0] = 0.6$<br>"Pizza recipes": $[0.6, 0.8] \cdot [0, 1] = 0.8$ |
| **Why normalizing mattered.** Without it, the raw vector $[3, 4]$ produces scores 5 times bigger. Scores would depend on the vector's length, not only its direction, so they couldn't be compared fairly with cosine scores. | $[3, 4] \cdot [0.6, 0.8] = 1.8 + 3.2 = 5.0$ |
| **The student's ranking.** The right document wins. But look at second place: the student thinks "Pizza recipes" is more relevant to "cat food" than "Cat behavior guide". Its vector leans too much toward food. | 1. Dry food for cats (1.0)<br>2. Pizza recipes (0.8)<br>3. Cat behavior guide (0.6) |
| **The teacher's ranking**, for comparison, using $\mathbf{y} = [0.8, 0.6]$. The teacher puts cats first. Training exists to fix disagreements like this one. | 1. Dry food for cats ($0.48 + 0.48 = 0.96$)<br>2. Cat behavior guide ($0.8$)<br>3. Pizza recipes ($0.6$) |

---

## Part 2: Training, teaching the student to act like the teacher

During training, we run Part 1 on many queries and compare the student's vectors with the teacher's. Three losses measure three different kinds of mistakes. A loss is a single number, and **smaller means better**.

### The training batch

| Theory | Math |
|---|---|
| **A batch** is a small group of queries processed together. We use two. The second query is chosen to be similar to the first, because similar queries are where students get confused. | $B = 2$<br>Query 1: "cat food"<br>Query 2: "cat toys" |
| **Teacher vectors** (the "correct answers"). "cat toys" is all about cats and not about food. | $\mathbf{y}^{(1)} = [0.8,\ 0.6]$<br>$\mathbf{y}^{(2)} = [1,\ 0]$ |
| **Student vectors.** Query 1 is what we computed in Part 1. Query 2 went through the same five steps; we just show the result. | $f(\mathbf{H}^{(1)}) = [0.6,\ 0.8]$<br>$f(\mathbf{H}^{(2)}) = [0.96,\ 0.28]$<br>Check: $\sqrt{0.9216 + 0.0784} = 1$ ✓ |

### Loss 1: Alignment ("point where your teacher points")

| Theory | Math |
|---|---|
| **Idea.** For each query, check how well the student points in the teacher's direction, using cosine similarity. | Cosine for each query in the batch |
| **Query 1.** | $[0.6, 0.8] \cdot [0.8, 0.6] = 0.96$ |
| **Query 2.** | $[0.96, 0.28] \cdot [1, 0] = 0.96$ |
| **Turn it into a loss.** Average the cosines, then subtract from 1. A perfect student has average cosine 1 and loss 0. | $\mathcal{L}_{\text{align}} = 1 - \dfrac{1}{B}\displaystyle\sum_{j=1}^{B} \cos\big(f(\mathbf{H}^{(j)}),\ \mathbf{y}^{(j)}\big)$ |
| **Our batch.** | $1 - \dfrac{0.96 + 0.96}{2} = 1 - 0.96 = 0.04$ |
| **What this tells us.** Only 0.04 — the students look nearly perfect. The next two losses will show that this is misleading. | $\mathcal{L}_{\text{align}} = 0.04$ |

### Loss 2: Contrastive, InfoNCE ("be closer to your teacher than to anyone else's")

| Theory | Math |
|---|---|
| **Idea.** It isn't enough to be close to your own teacher. You must be clearly closer to your own teacher than to the *other* teachers in the batch. Otherwise the index can't tell the queries apart. | Compare every student with every teacher |
| **All four dot products.** The diagonal (student 1 vs teacher 1, student 2 vs teacher 2) holds the correct matches. The other two are the wrong matches. | Student 1 vs $\mathbf{y}^{(1)}$: $0.96$ ✓<br>Student 1 vs $\mathbf{y}^{(2)}$: $0.6 \times 1 + 0.8 \times 0 = 0.6$<br>Student 2 vs $\mathbf{y}^{(2)}$: $0.96$ ✓<br>Student 2 vs $\mathbf{y}^{(1)}$: $0.768 + 0.168 = 0.936$ |
| **Spot the problem.** Student 2 ("cat toys") scores 0.96 with its own teacher but 0.936 with the "cat food" teacher. That's almost a tie. A search for cat toys would pull up cat food results nearly as often. | $0.96$ vs $0.936$: barely different |
| **Temperature $\tau$.** Before softmax, divide the scores by a small number. This stretches small differences into big ones, making the comparison stricter. We use $\tau = 0.1$. | Student 1: $0.96/0.1 = 9.6$ and $0.6/0.1 = 6.0$<br>Student 2: $0.96/0.1 = 9.6$ and $0.936/0.1 = 9.36$ |
| **Softmax for student 1.** What probability does student 1 give its own teacher? With two scores $a$ (correct) and $b$ (wrong), softmax simplifies to $\dfrac{1}{1 + e^{\,b - a}}$. | $\dfrac{1}{1 + e^{6.0 - 9.6}} = \dfrac{1}{1 + e^{-3.6}} = \dfrac{1}{1.027} = 0.973$ |
| **Loss for student 1.** Take $-\log$ of that probability. The probability is high, so the loss is tiny. | $-\log(0.973) = 0.027$ |
| **Softmax for student 2.** | $\dfrac{1}{1 + e^{9.36 - 9.6}} = \dfrac{1}{1 + e^{-0.24}} = \dfrac{1}{1.787} = 0.560$ |
| **Loss for student 2.** Barely better than a coin flip, so the loss is much larger. | $-\log(0.560) = 0.580$ |
| **The full formula.** The fraction is exactly the softmax probability we just computed. Average the $-\log$ values over the batch. | $\mathcal{L}_{\text{contra}} = -\dfrac{1}{B}\displaystyle\sum_{j=1}^{B} \log \dfrac{\exp\big(f(\mathbf{H}^{(j)}) \cdot \mathbf{y}^{(j)} / \tau\big)}{\sum_{k=1}^{B} \exp\big(f(\mathbf{H}^{(j)}) \cdot \mathbf{y}^{(k)} / \tau\big)}$ |
| **Our batch.** | $\mathcal{L}_{\text{contra}} = \dfrac{0.027 + 0.580}{2} = 0.304$ |
| **What temperature did.** With $\tau = 1$ instead, student 2's probability would be only 0.506, and the loss would treat the problem as smaller. A small $\tau$ makes the loss react strongly to near-ties. | $\tau = 1$: $\dfrac{1}{1 + e^{0.936 - 0.96}} = \dfrac{1}{1 + e^{-0.024}} = 0.506$ |
| **What this tells us.** Alignment said "almost perfect". Contrastive says "student 2 is dangerously confused with query 1". | $\mathcal{L}_{\text{contra}} = 0.304$ |

### Loss 3: Rank distillation ("order the documents the way your teacher does")

| Theory | Math |
|---|---|
| **Idea.** What finally matters in search is the *order* of results. So take the teacher's top-$K$ documents for a query and make the student rank them the same way. We show query 1 ("cat food") with $K = 3$. In training this is averaged over every query in the batch. | Documents: $\mathbf{d}_1$ cat behavior, $\mathbf{d}_2$ pizza, $\mathbf{d}_3$ dry cat food |
| **Teacher scores** $s_k = \mathbf{y} \cdot \mathbf{d}_k$. | $s_1 = 0.8$, $s_2 = 0.6$, $s_3 = 0.96$<br>Order: dry cat food, cat behavior, pizza |
| **Student scores** $\hat{s}_k = f(\mathbf{H}) \cdot \mathbf{d}_k$ (from Part 1, Step 5). | $\hat{s}_1 = 0.6$, $\hat{s}_2 = 0.8$, $\hat{s}_3 = 1.0$<br>Order: dry cat food, **pizza, cat behavior** ✗ |
| **Temperature $\tau_r$.** Same trick as before: divide scores to sharpen differences. We use $\tau_r = 0.2$. | Teacher: $[0.8, 0.6, 0.96] / 0.2 = [4,\ 3,\ 4.8]$<br>Student: $[0.6, 0.8, 1.0] / 0.2 = [3,\ 4,\ 5]$ |
| **Teacher softmax $P$.** "How much attention the teacher gives each document." | $e^4 = 54.60$, $e^3 = 20.09$, $e^{4.8} = 121.51$<br>total $= 196.20$<br>$P = [0.278,\ 0.102,\ 0.619]$ |
| **Student softmax $Q$.** | $e^3 = 20.09$, $e^4 = 54.60$, $e^5 = 148.41$<br>total $= 223.10$<br>$Q = [0.090,\ 0.245,\ 0.665]$ |
| **KL divergence, one document at a time.** Each term compares the teacher's probability with the student's. Where the student gives too little attention (cat behavior), the term is large and positive. | Cat behavior: $0.278 \log\tfrac{0.278}{0.090} = 0.278 \times 1.129 = 0.314$<br>Pizza: $0.102 \log\tfrac{0.102}{0.245} = 0.102 \times (-0.871) = -0.089$<br>Dry cat food: $0.619 \log\tfrac{0.619}{0.665} = 0.619 \times (-0.072) = -0.044$ |
| **Add them up.** (Individual terms can be negative, but the total KL is never negative.) | $0.314 - 0.089 - 0.044 = 0.181$ |
| **The full formula.** | $\mathcal{L}_{\text{rank}} = \mathrm{KL}\big(\mathrm{softmax}(\mathbf{s}/\tau_r) \,\Vert\, \mathrm{softmax}(\hat{\mathbf{s}}/\tau_r)\big)$ |
| **What this tells us.** Student 1 had cosine 0.96 with its teacher, yet it ranks pizza above a cat guide for the query "cat food". Only this loss catches that. | $\mathcal{L}_{\text{rank}} = 0.181$ |

### Combining the three losses

| Theory | Math |
|---|---|
| **One number to minimize.** Add the three losses. Each gets a weight $\lambda$, a knob that says how much that kind of mistake matters. | $\mathcal{L} = \lambda_a \mathcal{L}_{\text{align}} + \lambda_c \mathcal{L}_{\text{contra}} + \lambda_r \mathcal{L}_{\text{rank}}$ |
| **Equal weights.** | $\lambda_a = \lambda_c = \lambda_r = 1$<br>$\mathcal{L} = 0.04 + 0.304 + 0.181 = 0.525$ |
| **Turning a knob.** If confusion between queries worries you most, raise $\lambda_c$. Now that loss dominates, and training will push hardest on separating queries. | $\lambda_c = 2$:<br>$\mathcal{L} = 0.04 + 2(0.304) + 0.181 = 0.829$ |
| **Each loss catches a different mistake.** | Alignment: "wrong direction"<br>Contrastive: "confused with other queries"<br>Rank: "wrong result order" |

### Updating the weights

| Theory | Math |
|---|---|
| **What can change.** Only the projection head's own numbers are learned: $\mathbf{W}_{\text{in}}$, $\mathbf{b}_{\text{in}}$, the encoder's weights, $\mathbf{W}_{\text{out}}$, and $\mathbf{b}_{\text{out}}$. The LLM and the teacher stay frozen. | Learned: everything inside $f$ |
| **Gradient descent, the core idea.** For each number, calculate whether nudging it up would raise or lower the loss (the *gradient*). Then move it a small step in the direction that lowers the loss. The step size is the *learning rate* $\eta$. | $w_{\text{new}} = w - \eta \times \text{gradient}$<br>Example: $w = 2$, gradient $= 0.5$, $\eta = 0.1$<br>$w_{\text{new}} = 2 - 0.05 = 1.95$ |
| **AdamW** is a smarter version of this. It adjusts the step size separately for each weight based on its recent gradients, and it gently shrinks weights toward zero ("weight decay") to prevent overfitting. | Same idea: step against the gradient, with adaptive step sizes |
| **Cosine learning-rate schedule.** Big steps early, when the student is far from good. Small steps late, for fine-tuning. The step size follows half of a cosine wave from $\eta_{\max}$ down to $\eta_{\min}$ over $T$ steps. | $\eta_t = \eta_{\min} + \tfrac{1}{2}(\eta_{\max} - \eta_{\min})\big(1 + \cos(\pi t / T)\big)$<br>With $\eta_{\max} = 0.001$, $\eta_{\min} = 0$, $T = 1000$:<br>$t = 0$: $0.001$<br>$t = 500$: $0.0005$<br>$t = 1000$: $0$ |
| **What a good update looks like.** Suppose training changes $\mathbf{b}_{\text{out}}$ from $[1, 2]$ to $[2, 1]$. Redo Step 4 for "cat food". | $[2, 2] + [2, 1] = [4, 3]$<br>$\lVert [4, 3] \rVert_2 = 5$<br>$f(\mathbf{H}) = [0.8,\ 0.6]$, exactly the teacher's vector |
| **Check the losses for query 1.** Alignment is now perfect, and the student's scores equal the teacher's, so the rankings match and KL is 0. Pizza drops back to last place. | Cosine: $[0.8, 0.6] \cdot [0.8, 0.6] = 1$ → align term $0$<br>Scores: $0.8,\ 0.6,\ 0.96$ = teacher's → $\mathcal{L}_{\text{rank}} = 0$ |
| **Why training is still hard.** One bias change fixed one query. Real training must find a single set of weights that works for millions of queries at once, which is why it takes many small steps. | Same weights, every query |

---

## Cheat sheet

| Theory | Math (our numbers) |
|---|---|
| **1. Input projection:** resize each token from the LLM's width to the head's width. | $[1,0,2] \to [3,2]$, $[0,1,1] \to [1,2]$ |
| **2. Transformer encoder:** add positions, let tokens share meaning. | $[3,2] \to [2.5,2]$, $[1,2] \to [1.5,2]$ |
| **3. Mean pooling:** average the real tokens into one vector. | $\mathbf{p} = [2,\ 2]$ |
| **4. Output projection + normalize:** resize to the teacher's width, make length 1. | $[3,4] \to [0.6,\ 0.8]$ |
| **5. Search:** dot product with each document. | Dry cat food $1.0$, pizza $0.8$, cat guide $0.6$ |
| **Alignment loss:** is the student pointing where the teacher points? | $0.04$ |
| **Contrastive loss:** is each student clearly closest to its own teacher? | $0.304$ |
| **Rank loss:** does the student order documents like the teacher? | $0.181$ |
| **Combined loss:** weighted sum, minimized with AdamW and a cosine schedule. | $0.525$ |

**The whole chapter in one sentence:** the LLM's hidden states are resized, mixed, averaged, resized again, and normalized into a search vector, and training adjusts that process until the vector points where the teacher's does, stays distinct from other queries, and ranks documents the way the teacher would.
