## The five problems, one sentence each

1. **If the scanner garbles the page, the AI reads garbage** — no amount of clever instructions fixes that.
2. **Tables fall apart** — the AI can't always tell which number belongs to which row.
3. **We never agreed what we're asking for** — say "the date" and the AI picks one of four dates.
4. **Rows go missing quietly** — six rebate tiers in the document, five in our data, and nothing warns us.
5. **A wrong answer looks exactly like a right one** — the AI never says "I'm not sure," it just answers.

## Why we picked #4

The other four eventually get caught. Someone in finance spots a wrong number, a customer complains, a report doesn't add up.

A missing row is never caught, because **there's nothing on the screen to look at.** The data looks complete. Everyone trusts it. That makes it the most dangerous of the five, and the one nobody is currently watching.

## How we solve it

Three steps, easiest first.

**Step 1 — Ask the data to check itself.**  
Rebate tiers have to connect end to end. If tier 3 stops at 5,000 units and the next one starts at 8,000, something is missing from the middle. That's a rule anyone can write, it runs instantly, and it catches most cases. No AI involved.

**Step 2 — Build our own test papers.**  
We make fake rebate documents where _we_ chose the answers in advance. Run them through our system and count what came back. Now we know exactly how often rows go missing, and whether it gets worse on longer tables. No manual labelling needed, because we wrote the answer key first.

**Step 3 — Read it twice and compare.**  
Run the document through two different methods and compare. If method A found 18 rows and method B found 17 and they agree on 15, they're both missing things — so something is probably missing from both. There's a standard formula (borrowed from the way biologists count fish in a lake) that estimates how much.

**What changes:** instead of hoping nothing is missing, we get a number telling us how much is — and an alert when a specific document looks incomplete.


No — the problem itself is one of the clearest of the five. "Six tiers in the document, five in our data" is something anyone can picture in one sentence. Problems 1 and 5 are much harder to explain to a non-technical listener.

But there are two real weak spots, and they're worth fixing before you present.

**The bigger one: we don't know it happens to _you_.** Everything so far says rows _can_ go missing and that benchmarks show it happening elsewhere. The recall chart is illustrative. If someone in the room asks "has this actually happened in our pipeline?", right now the honest answer is "we don't know." That turns a sharp point into a hypothetical — and that's where the vagueness would come from, not the concept itself.

The fix is cheap: before presenting, find **one real rebate document** where your pipeline dropped a row. Look at your longest tier tables, or ones that cross a page break — that's where it'll be if it exists. One real example on screen is worth more than every chart in the deck. And if you look and genuinely can't find any, that's important to know too — it might mean a different problem deserves the spotlight.

**The smaller one: step 3 is the hard part.** Steps 1 and 2 are intuitive. The fish-counting method is clever but takes real effort to follow, and as the doc notes, it can't prove anything about a single document — only across hundreds. For a general audience, I'd present steps 1 and 2 as _the_ solution and step 3 as "and there's a statistical way to go further," rather than giving it equal weight.

One more thing to own: I recommended #4, partly because it's the most demonstrable. If your team's actual pain is something else — say, the date ambiguity in #3 keeps causing arguments with finance — then that's the better choice regardless of what's more elegant to present. You know which one hurts.