# 🎸 Empório da Música

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/LLM-Groq-green.svg)](https://groq.com/)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple.svg)](https://www.trychroma.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)

Este projeto foi desenvolvido como solução para o desafio técnico para a vaga de AI Engineer da empresa Artefact.

O objetivo do desafio era criar um assistente virtual inteligente para a loja Empório da Música, capaz de responder dúvidas sobre catálogo, pedidos, políticas internas e fornecer uma experiência de atendimento natural e contextualizada usando IA, RAG e tool calling.

---

## Visão geral

O Empório da Música é um agente conversacional de atendimento ao cliente construído com LangGraph, SQLite e ChromaDB, usando modelos de linguagem da Groq para execução rápida e eficiente.

O agente consegue:

- consultar produtos do catálogo com filtros por nome, preço e categoria;
- verificar o status de pedidos com base em ID ou código de rastreio;
- buscar histórico de compras por email ou telefone;
- responder dúvidas sobre políticas da loja usando busca semântica em documentos;
- manter memória contextual por sessão;
- rejeitar perguntas fora de escopo e evitar alucinações.

---

## Arquitetura do sistema

O projeto combina três camadas principais:

1. Orquestração do agente com LangGraph
2. Ferramentas de consulta estruturada em SQLite
3. Recuperação semântica de conhecimento em ChromaDB

Fluxo geral:

```text
Usuário
  ↓
CLI / Streamlit
  ↓
LangGraph Agent
  ├─ busca em SQLite
  ├─ busca semântica em documentos
  └─ resposta contextualizada via Groq
```

---

## Stack tecnológica

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

## 🛠️ Decisões Técnicas e Justificativas Arquiteturais

### 1. Escolha do Provedor de LLM: **Groq API (`llama-3.3-70b-versatile` / `llama3-8b-8192`)**
* **Decisão:** Optou-se pela infraestrutura da **Groq** utilizando o modelo **Llama 3.3 70B** (ou Llama 3 8B como fallback) em substituição a APIs de cotas estritas como a do Gemini.
* **Justificativa FinOps & Performance:**
  - **Gratuito e Sem Restrições Rígidas de Rate Limit:** A Groq oferece um plano gratuito generoso com taxa de requisições por minuto (RPM) e tokens por minuto (TPM) significativamente superiores para desenvolvimento.
  - **Latência Próxima a Zero:** A aceleração via LPU (Language Processing Unit) da Groq entrega respostas em milissegundos, resolvendo o gargalo de tempo de espera do ciclo de *Tool Calling* do LangGraph.
  - **Suporte Nativo a Function Calling:** O Llama 3.3 ajustado pela Groq possui altíssima precisão na estruturação de argumentos JSON para acionamento de ferramentas.

### 2. Embeddings Locais Gratuitos: **`sentence-transformers/all-MiniLM-L6-v2`**
* **Decisão:** Uso do modelo open-source via `langchain-huggingface` para vetorização dos chunks do PDF.
* **Justificativa:**
  - **Custo Zero & Privacidade:** Executa localmente no processador da máquina sem depender de chamadas tarifadas de API externa.
  - **Eficiência:** Modelo compacto (80MB) com alta fidelidade semântica para textos em português, gerando vetores de 384 dimensões otimizados para busca por similaridade de cosseno no ChromaDB.

### 3. Banco de Dados Relacional (SQLite) & Pré-processamento Otimizado
* **Decisão:** Ingestão das 6 tabelas CSV em um banco relacional `emporio.db` com criação prévia de índices relacionais.
* **Justificativa:**
  - **Consultas em < 5ms:** Índices nas colunas `product_id`, `category_id`, `tracking_code`, `email` e `phone` garantem recuperações instantâneas.
  - **Integridade de Dados:** Validação do formato JSON do campo `specs` em produtos e suporte a buscas insensíveis a caracteres especiais em dados de contato dos clientes.

### 4. Orquestração de Estado: **LangGraph**
* **Decisão:** Estruturação do agente como um grafo de estados (*StateGraph*) com ciclo condicional ReAct (`call_model` ↔ `tools`).
* **Justificativa:**
  - **Determinismo e Controle:** Diferente de agentes legados de cadeia única (`AgentExecutor`), o LangGraph permite definir rotas explícitas de término (`END`) e controle de exceções.
  - **Memória Transacional:** Uso do `MemorySaver` com `thread_id` para manter o contexto completo da conversa entre múltiplos turnos do atendimento.

---

## 🛡️ Guardrails e Regras de Negócio

O assistente foi programado via *System Prompt* robusto (`src/prompt.py`) para operar sob três pilares fundamentais:

1. **Restrição de Escopo de Produtos (Acessórios):**
   * *Regra:* A Empório da Música vende **exclusivamente instrumentos musicais**.
   * *Comportamento:* Se o usuário solicitar cabos, palhetas, encordoamentos ou cases, o agente recusa cordialmente a venda e orienta o cliente a procurar parceiros locais.
2. **Perguntas Fora de Escopo Geral:**
   * *Regra:* Dúvidas não relacionadas à loja ou a instrumentos (ex.: programação, notícias, conselhos).
   * *Comportamento:* O agente redireciona a conversa educadamente para a loja sem alucinar.
3. **Anti-Alucinação Financeira e de Estoque:**
   * *Regra:* O modelo nunca inventa preços ou status de entrega. Toda informação factual deve obrigatoriamente ser oriunda do retorno de uma *Tool* (`search_products`, `get_order_status`, `consult_store_policies`).

---

## Regras de negócio e guardrails

O agente foi desenhado para seguir políticas explícitas de atendimento:

- responde apenas sobre produtos e serviços da Empório da Música;
- não inventa estoque, preço ou status de entregas;
- usa ferramentas para consultar dados reais do banco antes de responder;
- trata dúvidas sobre devolução e arrependimento com base em documentos da loja;
- recusa pedidos fora de escopo com resposta educada e segura;
- mantém contexto de conversa por sessão.

---

## Estrutura do repositório

```text
Emporio-da-Musica/
├── app.py                     # interface web em Streamlit
├── main.py                    # interface em linha de comando
├── requirements.txt           # dependências do projeto
├── .env                       # variáveis locais de ambiente (não versionado)
├── README.md                  # documentação do projeto
├── data/
│   ├── desafio_tecnico_ai_eng - categories.csv
│   ├── desafio_tecnico_ai_eng - customers.csv
│   ├── desafio_tecnico_ai_eng - order_items.csv
│   ├── desafio_tecnico_ai_eng - orders.csv
│   ├── desafio_tecnico_ai_eng - products.csv
│   ├── desafio_tecnico_ai_eng - promotions.csv
│   ├── emporio.db             # banco SQLite gerado
│   └── políticas_da_loja.pdf
├── vector_store/              # índice vetorial do ChromaDB
├── src/
│   ├── agent.py               # orquestração do agente
│   ├── db_tools.py            # consultas estruturadas no SQLite
│   ├── prompt.py              # instruções do sistema e guardrails
│   └── rag_tools.py           # busca semântica para políticas da loja
├── scripts/
│   ├── preprocess_db.py       # criação do banco SQLite
│   ├── ingest_polices.py      # ingestão do PDF em ChromaDB
│   ├── eda.py                 # análise exploratória
│   └── tests/
│       ├── test_agent.py      # testes de integração do agente
│       └── test_tools.py      # testes das ferramentas
├── conversations/
│   ├── scenario_1_catalogo_e_preco.md
│   ├── scneario_2_informacoes_gerais.md
│   ├── scneario_3_politica_devolucao.md
│   ├── scenario_4_status_pedido.md
│   └── scenario_5_guardrail_acessorios.md
└── .gitignore
```

---

## Pré-requisitos

- Python 3.12+
- `pip`
- acesso à API da Groq
- ambiente virtual recomendado

---

## Configuração do ambiente

### 1) Clone o repositório

```bash
git clone https://github.com/seu-usuario/Emporio-da-Musica.git
cd Emporio-da-Musica
```

### 2) Crie e ative um ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Instale as dependências

```bash
pip install -r requirements.txt
```

### 4) Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
GROQ_API_KEY=sua_chave_aqui
LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-20b
GROQ_MODEL=openai/gpt-oss-20b
LLM_TEMPERATURE=0.6
```

> A chave da Groq deve ser obtida no painel da Groq Cloud.

---

## Preparação dos dados

Antes de rodar a aplicação, é necessário preparar o banco SQLite e indexar as políticas em ChromaDB.

### Banco relacional

```bash
python scripts/preprocess_db.py
```

Esse comando gera o arquivo `data/emporio.db` com tabelas de produtos, clientes, pedidos, itens e categorias.

### Base vetorial de políticas

```bash
python scripts/ingest_polices.py
```

Esse comando lê o PDF de políticas da loja e cria o índice vetorial em `vector_store/`.

---

## Como executar o projeto

### Opção 1: interface web com Streamlit

```bash
streamlit run app.py
```

Acesse o navegador em:

```text
http://localhost:8501
```

### Opção 2: terminal interativo

```bash
python main.py
```

Esse modo mantém uma conversa em CLI e é útil para validar rapidamente o comportamento do agente.

---

## Testes

### Testes de ferramentas

```bash
python scripts/tests/test_tools.py
```

### Testes do agente

```bash
python scripts/tests/test_agent.py
```

Os testes cobrem:

- busca de produtos;
- consulta de status de pedido;
- políticas e devolução;
- guardrail de fora de escopo;
- memória contextual da conversa.

---

## Exemplos de uso

Alguns exemplos de perguntas suportadas pelo agente:

- Quais violões vocês têm até R$ 1000?
- Qual o status do meu pedido número 1?
- Qual o histórico de compras do cliente lucas.mendes@jmail.com?
- Posso devolver um pedido por arrependimento?
- Vocês vendem palhetas e acessórios?

---

## Limitações conhecidas

- a base vetorial é persistida localmente em disco e depende da presença da pasta `vector_store/`;
- o modelo de inferência depende da disponibilidade da API da Groq;
- o projeto foi pensado para uso em contexto de demonstração e prototipagem, com foco em robustez funcional e clareza de arquitetura.

---

## Observações finais

Este projeto foi construído como solução para um desafio técnico de IA, com foco em:

- orchestration de agentes;
- uso de ferramentas em pipeline;
- recuperação de contexto por RAG;
- busca em banco de dados relacional;
- desenho de guardrails e restrição de escopo;
- experiência prática de atendimento em ambiente comercial.

A proposta busca demonstrar capacidade de engenharia de IA aplicada ao atendimento de clientes e simular um cenário real de uso em e-commerce de instrumentos musicais.

---

## Declaração do desafio

Este projeto faz parte de um desafio técnico para a vaga de AI Engineer na empresa Artefact, desenvolvido com foco em demonstrar domínio prático de:

- arquitetura de agentes;
- integração com modelos de linguagem;
- RAG e busca semântica;
- bancos de dados transacionais;
- programação orientada a ferramentas e workflows de IA;
- e aplicação de boas práticas de engenharia e validação do sistema.

---

## Declaração de Uso de Assistentes de IA

Em conformidade com a transparência do processo seletivo, declara-se que ferramentas de IA Generativa (ChatGPT / Claude / Gemini) foram utilizadas como **parceiras de desenvolvimento** para a aceleração de escrita de código boilerplate, estruturação de testes unitários e refatoração de documentos. No presente projeto, a ferramenta escolhida foi o GitHub Copilot, utilizado para agilizar trechos repetitivos, sugerir melhorias estruturais, revisar trechos de documentação e apoiar a validação de fluxos de integração. Toda a lógica de negócios, design da arquitetura de agentes, escolhas de bibliotecas e validação dos dados foram projetadas, implementadas e auditadas pelo autor do projeto.
