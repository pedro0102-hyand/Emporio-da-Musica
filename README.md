# 🎸 Empório da Música

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/LLM-Groq-green.svg)](https://groq.com/)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple.svg)](https://www.trychroma.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)

This project was developed as a solution for the technical challenge for the AI Engineer role at Artefact.

The goal of the challenge was to create an intelligent virtual assistant for the Empório da Música store, capable of answering questions about the catalog, orders, internal policies, and providing a natural, contextualized customer experience using AI, RAG, and tool calling.

---

## Overview

Empório da Música is a conversational customer support agent built with LangGraph, SQLite, and ChromaDB, using language models from Groq for fast and efficient execution.

The agent is able to:

- query the product catalog with filters by name, price, and category;
- check the status of orders based on ID or tracking code;
- search purchase history by email or phone number;
- answer questions about store policies using semantic search over policy documents;
- maintain contextual memory per session;
- reject out-of-scope questions and avoid hallucinations.

---

## System architecture

The project combines three main layers:

1. Agent orchestration with LangGraph
2. Structured data queries in SQLite
3. Semantic retrieval of knowledge in ChromaDB

General flow:

```text
User
  ↓
CLI / Streamlit
  ↓
LangGraph Agent
  ├─ SQLite lookup
  ├─ semantic search in documents
  └─ contextual response via Groq
```

---

## Tech stack

- Python 3.12
- LangGraph
- LangChain
- Groq API
- SQLite
- ChromaDB
- Hugging Face embeddings
- Streamlit
- Pandas

---

## Business rules and guardrails

The agent was designed to follow explicit customer service policies:

- respond only about products and services from Empório da Música;
- never invent stock, prices, or delivery statuses;
- use tools to query real database data before answering;
- answer return and cancellation questions based on the store’s policy documents;
- refuse out-of-scope requests politely and safely;
- maintain conversation context per session.

---

## 🛠️ Technical decisions and architectural rationale

### 1. Choice of LLM provider: **Groq API (`llama-3.3-70b-versatile` / `llama3-8b-8192`)**
* **Decision:** We chose the **Groq** infrastructure using the **Llama 3.3 70B** model (or Llama 3 8B as a fallback) instead of stricter quota-limited APIs such as Gemini.
* **FinOps and performance rationale:**
  - **Free and without rigid rate-limit restrictions:** Groq offers a generous free tier with significantly higher requests-per-minute (RPM) and tokens-per-minute (TPM) for development work.
  - **Near-zero latency:** Groq’s LPU acceleration delivers responses in milliseconds, eliminating the bottleneck in the LangGraph tool-calling cycle.
  - **Native function-calling support:** The Llama 3.3 model adapted for Groq has high accuracy when structuring JSON arguments to trigger tools.

### 2. Free local embeddings: **`sentence-transformers/all-MiniLM-L6-v2`**
* **Decision:** Use an open-source model via `langchain-huggingface` to vectorize PDF chunks.
* **Rationale:**
  - **Zero cost and privacy:** Runs locally on the machine’s processor without relying on paid external API calls.
  - **Efficiency:** A compact model (80 MB) with strong semantic fidelity for Portuguese text, generating 384-dimensional vectors optimized for cosine similarity search in ChromaDB.

### 3. Relational database (SQLite) and optimized preprocessing
* **Decision:** Load the 6 CSV tables into a relational database `emporio.db` with prior creation of relational indexes.
* **Rationale:**
  - **Queries in under 5 ms:** Indexes on `product_id`, `category_id`, `tracking_code`, `email`, and `phone` guarantee near-instant retrieval.
  - **Data integrity:** Validation of the JSON format in the `specs` field for products and support for case-insensitive searches in customer contact data.

### 4. State orchestration: **LangGraph**
* **Decision:** Structure the agent as a state graph (*StateGraph*) with a conditional ReAct loop (`call_model` ↔ `tools`).
* **Rationale:**
  - **Determinism and control:** Unlike legacy single-chain agents (`AgentExecutor`), LangGraph allows explicit termination routes (`END`) and exception handling.
  - **Transactional memory:** Using `MemorySaver` with `thread_id` preserves the full conversation context across multiple turns.

---

## 🛡️ Guardrails and business rules

The assistant was implemented through a robust system prompt (`src/prompt.py`) to operate under three core principles:

1. **Restriction of product scope (accessories):**
   * *Rule:* Empório da Música sells **only musical instruments**.
   * *Behavior:* If the user asks for cables, picks, strings, or cases, the agent politely refuses the sale and directs the customer to local partners.
2. **Out-of-scope questions:**
   * *Rule:* Questions unrelated to the store or instruments (e.g., programming, news, general advice).
   * *Behavior:* The agent redirects the conversation politely toward the store’s scope without hallucinating.
3. **Anti-financial and stock hallucination:**
   * *Rule:* The model never invents prices or delivery statuses. Any factual information must come from the result of a tool call (`search_products`, `get_order_status`, `consult_store_policies`).

---

## Repository structure

```text
Emporio-da-Musica/
├── app.py                     # interactive web interface in Streamlit
├── main.py                    # interactive command-line interface
├── requirements.txt           # project dependencies
├── .env                       # local environment variables (not versioned)
├── README.md                 # project documentation (Portuguese)
├── README.en.md              # project documentation (English translation)
├── data/
│   ├── desafio_tecnico_ai_eng - categories.csv
│   ├── desafio_tecnico_ai_eng - customers.csv
│   ├── desafio_tecnico_ai_eng - order_items.csv
│   ├── desafio_tecnico_ai_eng - orders.csv
│   ├── desafio_tecnico_ai_eng - products.csv
│   ├── desafio_tecnico_ai_eng - promotions.csv
│   ├── emporio.db             # generated SQLite database
│   └── políticas_da_loja.pdf
├── vector_store/              # ChromaDB vector index
├── src/
│   ├── agent.py               # agent orchestration
│   ├── db_tools.py            # structured queries in SQLite
│   ├── prompt.py              # system instructions and guardrails
│   └── rag_tools.py           # semantic search for store policies
├── scripts/
│   ├── preprocess_db.py       # creation of the SQLite database
│   ├── ingest_polices.py      # ingestion of the PDF into ChromaDB
│   ├── eda.py                 # exploratory analysis
│   └── tests/
│       ├── test_agent.py      # agent integration tests
│       └── test_tools.py      # tool tests
├── conversations/
│   ├── scenario_1_catalogo_e_preco.md
│   ├── scneario_2_informacoes_gerais.md
│   ├── scneario_3_politica_devolucao.md
│   ├── scenario_4_status_pedido.md
│   └── scenario_5_guardrail_acessorios.md
└── .gitignore
```

---

## Prerequisites

- Python 3.12+
- `pip`
- access to the Groq API
- a virtual environment is recommended

---

## Environment setup

### 1) Clone the repository

```bash
git clone https://github.com/seu-usuario/Emporio-da-Musica.git
cd Emporio-da-Musica
```

### 2) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure environment variables

Create a `.env` file at the project root with the following content:

```env
GROQ_API_KEY=sua_chave_aqui
LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-20b
GROQ_MODEL=openai/gpt-oss-20b
LLM_TEMPERATURE=0.6
```

> The Groq key must be obtained from the Groq Cloud dashboard.

---

## Data preparation

Before running the application, it is necessary to prepare the SQLite database and index the policies in ChromaDB.

### Relational database

```bash
python scripts/preprocess_db.py
```

This command generates the `data/emporio.db` file with tables for products, customers, orders, order items, and categories.

### Vector database for policies

```bash
python scripts/ingest_polices.py
```

This command reads the store policy PDF and creates the vector index in `vector_store/`.

---

## How to run the project

### Option 1: web interface with Streamlit

```bash
streamlit run app.py
```

Open the browser at:

```text
http://localhost:8501
```

### Option 2: interactive terminal

```bash
python main.py
```

This mode keeps a live CLI conversation and is useful for validating the agent behavior quickly.

---

## Tests

### Tool tests

```bash
python scripts/tests/test_tools.py
```

### Agent tests

```bash
python scripts/tests/test_agent.py
```

The tests cover:

- product search;
- order status queries;
- policies and returns;
- out-of-scope guardrails;
- contextual conversation memory.

---

## Examples of use

Some examples of questions supported by the agent:

- Which guitars do you have for under R$ 1000?
- What is the status of my order number 1?
- What is the purchase history for lucas.mendes@jmail.com?
- Can I return an order due to buyer’s remorse?
- Do you sell picks and accessories?

---

## Known limitations

- the vector database is persisted locally on disk and depends on the presence of the `vector_store/` folder;
- the inference model depends on the availability of the Groq API;
- the project was designed for demonstration and prototyping contexts, focused on functional robustness and architectural clarity.

---

## Final notes

This project was developed as a solution to a technical AI challenge, focused on:

- agent orchestration;
- tool use inside a pipeline;
- contextual recovery via RAG;
- relational database search;
- designing guardrails and scope restrictions;
- practical customer support experience in a commercial environment.

The proposal aims to demonstrate the ability to apply AI engineering to customer service and simulate a real-world use case in an online music instrument store.

---

## Challenge declaration

This project is part of a technical challenge for the AI Engineer role at Artefact, developed with the aim of demonstrating practical knowledge of:

- agent architecture;
- integration with language models;
- RAG and semantic search;
- transactional databases;
- tool-oriented programming and AI workflows;
- and the application of good engineering and validation practices.

---

## Declaration of use of AI assistants

In compliance with transparency requirements for the selection process, it is declared that Generative AI tools (ChatGPT / Claude / Gemini) were used as **development partners** to accelerate boilerplate code writing, structure unit tests, and refactor documentation. In this project, the selected tool was GitHub Copilot, used to speed up repetitive sections, suggest structural improvements, review documentation passages, and support validation of integration flows. All business logic, agent architecture design, library choices, and validation of data were designed, implemented, and audited by the project author.
