# 01 · Context: Why Agents Look Things Up

## The short version

A language model only knows what was in its training data, frozen at some date. When it needs a fact it doesn't have (a company's internal policy, yesterday's news, the contents of a specific manual), it has to **retrieve** that fact from somewhere outside itself and read it before answering.

## Step 1: The model's knowledge is fixed

An LLM learns by reading a huge amount of text once. After that, its knowledge sits inside its weights and does not change. Three kinds of gaps follow:

| Gap | Example |
|---|---|
| **Too new** | "What did the board decide last Tuesday?" |
| **Too private** | "What is our refund policy for enterprise customers?" |
| **Too specific** | "What torque does page 214 of this repair manual give for bolt C?" |

When it doesn't know, a model may still produce a confident-sounding answer. This is called *hallucination*.

## Step 2: The fix is to hand it the right text

**Retrieval-Augmented Generation (RAG)** is the standard fix (Lewis et al., 2020). Before answering, the system:

1. Searches a collection of documents for passages that look relevant.
2. Pastes the best few passages into the model's input.
3. Lets the model answer while reading them.

The model is no longer answering from memory alone. It is answering from evidence.

## Step 3: From chatbots to agents

In a simple RAG chatbot, a search happens on every user message. In an **agent**, the model itself decides *when* to search, sometimes several times in one conversation. The paper calls each of these moments a **retrieval trigger**. The dataset used in the paper has 2,189 of them.

This matters because agents search in the *middle* of long conversations, where the meaning of a question often depends on what was said earlier.

## Step 4: Conversations make search harder

Look at this exchange:

> **User:** Tell me about the Eiffel Tower.
> **Agent:** *(answers)*
> **User:** How tall is it?

"How tall is it?" is a terrible search query on its own. "It" only makes sense because of the first message. Resolving words like "it", "that one" or "the second option" using earlier turns is called **coreference resolution**, and it is exactly where conversational search goes wrong. The QReCC dataset, which the paper uses, was built to test this.

## Step 5: The question the rest of this guide answers

Retrieval is necessary. The question is **how the search is carried out**, and whether the usual way is wasteful. To answer that, you first need to understand how search by meaning works (next file).

---
**Key terms:** retrieval, RAG, hallucination, agent, retrieval trigger, coreference, QReCC.
