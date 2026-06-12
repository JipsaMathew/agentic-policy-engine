## Architecture

Orchestration: LangGraph (providing stateful, multi-step reasoning loops).

RAG Pipeline: LangChain-based ingestion with localized vector retrieval.

Core Logic: Deterministic policy lookup via RAG to mitigate hallucinations.

Tech Stack: Python, Streamlit, LangChain, LangGraph, Groq (LLM Inference).

Key Technical Features
Agentic Workflow: Implements a Human-in-the-Loop (HIL) pattern to ensure high-stakes financial policy queries are verified for accuracy.

Deterministic Guardrails: The agent is configured with strict system prompts and retrieval constraints to ensure it stays within the context of the GM Financial lease documentation.

Performance Optimization: Uses efficient vector indexing to reduce latency in policy lookups.

Resilient Infrastructure: Developed with a modular backend to allow for future integration with enterprise-grade vector databases and LLM providers.

Getting Started
Prerequisites
Python 3.11+

Groq API Key

### Installation

> **1. Clone the repository:**
> ```bash
> git clone [https://github.com/yourusername/agentic-policy-engine.git](https://github.com/yourusername/agentic-policy-engine.git)
> cd agentic-policy-engine
> ```
>
> **2. Install dependencies:**
> ```bash
> pip install -r requirements.txt
> ```
>
> **3. Set your environment variables:**
> ```bash
> export GROQ_API_KEY='your-api-key-here'
> ```
>
> **4. Run the application:**
> ```bash
> streamlit run main.py
> ```
