# 17 · Results, Part 1: How Search Quality Is Measured

Before reading the results you need to know what the numbers mean. Each metric looks at the **top 10** documents returned for one retrieval trigger, then the paper averages over all test triggers.

## Step 1: Recall@10, "did we find it at all?"

For each trigger: 1 if a relevant document is anywhere in the top 10, else 0. Average over triggers.

> Baseline 0.637 means: for 63.7% of searches, the right document showed up somewhere in the top 10.

It doesn't care whether it is 1st or 10th.

## Step 2: MRR@10, "how high was it?"

**Reciprocal rank** = 1 / (position of the first relevant document), or 0 if none is in the top 10.

| First relevant document at position | Reciprocal rank |
|---|---|
| 1 | 1.0 |
| 2 | 0.5 |
| 3 | 0.333 |
| 10 | 0.1 |
| not in top 10 | 0 |

**Mean** reciprocal rank averages these. MRR rewards putting the right answer near the top, which matters because an agent usually reads only the first few results.

## Step 3: nDCG@10, "how good is the whole ordering?"

**DCG** adds up relevance scores with a discount for lower positions: a relevant document at position $r$ contributes $1/\log_2(r + 1)$. So position 1 is worth 1.0, position 3 is worth 0.5, position 10 about 0.29. **nDCG** divides by the best possible DCG, so a perfect ordering scores 1. It is useful when there are several relevant documents.

## Step 4: Toy example

Suppose the relevant document for "cat food" is "Healthy dry food for cats":

| System | Its position | Recall@10 | RR | DCG contribution |
|---|---|---|---|---|
| Teacher | 1 | 1 | 1.0 | 1.0 |
| Student ranks it 3rd | 3 | 1 | 0.333 | 0.5 |

Same recall, very different MRR. This is why the paper reports all three.

## Step 5: Is the difference real? (statistics)

Test sets are finite, so some difference between two systems can be luck.

| Tool | Question it answers | How |
|---|---|---|
| **McNemar's test** | On the same triggers, does one system succeed more often than the other beyond chance? | Look only at triggers where the systems *disagree*. Here the student won 140 and lost 206. $\chi^2 = (|140-206|-1)^2/(140+206) = 12.21$, which gives $p = 0.0005$. So the student is genuinely a little worse, not just unlucky. |
| **Bootstrap 95% CI** | What range of gaps is plausible? | Resample the test triggers 1,000 times with replacement, recompute the gap each time, and take the middle 95%. For Recall@10 the gap is −3.0 points with CI [−4.7, −1.4]. The whole range is below zero, which agrees with McNemar. |
| **Win / tie / loss** | Where exactly do they differ? | Per trigger: 140 student-only successes, 206 baseline-only, 1,843 the same (both succeed or both fail). Agreement = 1843 / 2189 = 84.2%. |

## Step 6: Latency p50

The **median** time per query (half of queries are faster, half slower). The median is used because a few unusually slow queries would distort an average.
