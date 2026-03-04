# AI Document Assistant

A fully **local** AI chat assistant that lets you have a conversation with any PDF or text document — no API keys, no cloud, no data leaving your machine.

Built with a **Retrieval-Augmented Generation (RAG)** pipeline using LangChain, ChromaDB, and Ollama.

![demo](assets/demo.png)

## How it works

```
┌─────────────────────────────────────────────────────────────────┐
│                         INGESTION                               │
│                                                                 │
│  PDF / TXT  ──►  text chunks  ──►  nomic-embed-text  ──►        │
│                                        ChromaDB (local)         │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                           CHAT                                  │
│                                                                 │
│  Question  ──►  embed  ──►  top-5 chunks from ChromaDB          │
│                ──►  prompt (system + context + history)         │
│                ──►  llama3 via Ollama  ──►  streamed answer      │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **100% offline** — runs llama3 locally via [Ollama](https://ollama.com)
- Multi-document knowledge base — load as many files as you want
- Conversation history — follow-up questions work naturally
- Streaming responses — tokens print as they arrive
- Source attribution — shows which document and page each answer came from
- Persistent vector store — ChromaDB survives restarts

## Quick start

**Prerequisites:** [Ollama](https://ollama.com/download) installed and running.

```bash
# 1. Pull the required models
ollama pull llama3
ollama pull nomic-embed-text

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run
python app.py
```

## Usage

```
You: /load ./reports/annual_report_2024.pdf
  Ingesting annual_report_2024.pdf …
  ✓ Stored 142 chunks from 'annual_report_2024.pdf'

You: What was the total revenue in Q3?

Assistant: According to the annual report, total revenue in Q3 2024 was $4.2 billion,
representing an 18% year-over-year increase driven primarily by cloud services.

  Sources:
    • annual_report_2024.pdf (p.23)
    • annual_report_2024.pdf (p.31)

You: /docs
  Ingested documents (1):
    • annual_report_2024.pdf

You: /rm annual_report_2024.pdf
  ✓ Removed 142 chunks for 'annual_report_2024.pdf'
```

### All commands

| Command | Description |
|---|---|
| `/load <path>` | Ingest a PDF or .txt file |
| `/docs` | List all loaded documents |
| `/rm <name>` | Remove a document |
| `/new` | Clear conversation history |
| `/model <name>` | Switch Ollama LLM model |
| `/help` | Show help |
| `/quit` | Exit |

## Project structure

```
docuchat/
├── app.py           – CLI interface and command dispatcher
├── ingest.py        – PDF/text loading, chunking, embedding, ChromaDB storage
├── chat.py          – RAG retrieval + Ollama streaming chat session
├── requirements.txt
└── chroma_db/       – auto-created persistent vector store
```

## Switching models

Any model pulled in Ollama works:

```
You: /model mistral
You: /model phi3
You: /model gemma2
```

## Tech stack

| Layer | Tool |
|---|---|
| LLM runtime | Ollama (local) |
| LLM model | llama3 (default) |
| Embeddings | nomic-embed-text |
| Vector store | ChromaDB |
| Orchestration | LangChain |
| PDF parsing | PyMuPDF |
