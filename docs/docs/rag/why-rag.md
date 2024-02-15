---
sidebar_position: 2
---

# Why RAG?

What challenges does the retrieval augmented generation approach solve?

## Problem 1: LLM models do not know your data

Traditional LLMs are trained on massive datasets but lack access to your specific data, leading to:

- **Out-of-date responses**: They might rely on outdated information from their training data, not reflecting real-time changes in your domain.
- **Inaccurate answers**: When faced with questions outside their training, they might fabricate information or provide irrelevant responses.
- **Limited context**: They struggle to fully understand the specific context of your application, resulting in generic answers that lack nuance.

## Problem 2: AI applications must leverage custom data to be effective

Integrating custom data into traditional LLMs is often a complex and resource-intensive process:

- **Retraining**: You might need to retrain the entire LLM on your data, which can be expensive and time-consuming.
- **Limited applicability**: The LLM might not be able to effectively process and utilize your specific data formats or domain knowledge.

## AI Model Guidance Comparison: Methods vs. Applications

| Method                                   | Definition                                                | Primary Use Case                        | Data Requirements                                           | Advantages                                     | Considerations                                    |
| ---------------------------------------- | --------------------------------------------------------- | --------------------------------------- | ----------------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------- |
| **Prompt Engineering**                   | Crafting specialized prompts to guide LLM behavior        | Quick, on-the-fly model guidance        | None                                                        | Fast, cost-effective, no training required     | Less control than fine-tuning                     |
| **Retrieval Augmented Generation (RAG)** | Combining an LLM with external knowledge retrieval        | Dynamic datasets and external knowledge | External knowledge base or database (e.g., vector database) | Dynamically updated context, enhanced accuracy | Increases prompt length and inference computation |
| **Fine-tuning**                          | Adapting a pretrained LLM to specific datasets or domains | Domain or task specialization           | Thousands of domain-specific or instruction examples        | Granular control, high specialization          | Requires labeled data, computational cost         |
| **Pretraining**                          | Training an LLM from scratch                              | Unique tasks or domain-specific corpora | Large datasets (billions to trillions of tokens)            | Maximum control, tailored for specific needs   | Extremely resource-intensive                      |
