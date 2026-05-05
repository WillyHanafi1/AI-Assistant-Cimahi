# CIMAS — AI-Powered Public Service Assistant for Kota Cimahi

<p align="center">
  <strong>A production-grade RAG (Retrieval-Augmented Generation) chatbot for citizen services, built with FAISS Vector Database, Jina Embeddings v3, and DeepSeek LLM.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.8+-blue" alt="Python">
  <img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B" alt="Framework">
  <img src="https://img.shields.io/badge/AI-RAG%20Architecture-purple" alt="AI">
  <img src="https://img.shields.io/badge/Vector%20DB-FAISS-orange" alt="Vector DB">
  <img src="https://img.shields.io/badge/LLM-DeepSeek-green" alt="LLM">
</p>

---

## Overview

**CIMAS** (Cimahi Masyarakat Assistant) is a Generative AI-powered public service chatbot that provides 24/7 automated citizen support for Kota Cimahi. It uses a **RAG Architecture** to answer questions based on official government documents (Peraturan Daerah, Peraturan Walikota) with high accuracy and source attribution.

The system also includes an **AI-powered complaint classification module** that automatically routes citizen complaints to the correct government department using LLM-based classification with keyword fallback.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CIMAS Architecture                      │
│                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │  User     │───▶│  Streamlit   │───▶│  Query Pipeline  │   │
│  │  Query    │    │  Frontend    │    │                  │   │
│  └──────────┘    └──────────────┘    └────────┬─────────┘   │
│                                               │             │
│                        ┌──────────────────────┤             │
│                        ▼                      ▼             │
│              ┌──────────────────┐   ┌──────────────────┐    │
│              │  Jina Embeddings │   │  Embedding Cache  │    │
│              │  v3 API          │   │  (LRU, max 50)    │    │
│              └────────┬─────────┘   └──────────────────┘    │
│                       │                                      │
│                       ▼                                      │
│              ┌──────────────────┐                            │
│              │  FAISS Vector DB │  ← 870 document chunks     │
│              │  (L2 Search)     │    from 3 Perda/Perwal     │
│              └────────┬─────────┘                            │
│                       │ Top-K results (k=50)                 │
│                       ▼                                      │
│              ┌──────────────────┐                            │
│              │  Context Builder │  ← Top 3 chunks × 800 char │
│              └────────┬─────────┘                            │
│                       │                                      │
│                       ▼                                      │
│              ┌──────────────────┐                            │
│              │  DeepSeek LLM    │  ← Via OpenRouter API      │
│              │  (Streaming)     │    temperature=0.1          │
│              └────────┬─────────┘                            │
│                       │                                      │
│                       ▼                                      │
│              ┌──────────────────┐                            │
│              │  Streamed Answer │  + source attribution       │
│              │  + Performance   │  + response time metrics    │
│              └──────────────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

### 🤖 RAG Chatbot (Main Feature)
- **Vector search** over government documents using FAISS with Jina Embeddings v3
- **Streaming responses** with real-time character rendering for better UX
- **Source attribution** — shows which documents were used to generate the answer
- **Performance metrics** — displays search time and LLM inference time per query
- **Embedding cache** (LRU, max 50 entries) to reduce redundant API calls
- **Batch embedding** support for multi-query processing
- **Graceful fallback** — continues working even when FAISS files are unavailable

### 📣 AI Complaint Classification System
- **LLM-based department routing** — classifies citizen complaints to the correct department using DeepSeek LLM with structured system prompts
- Routes across **8 government agencies**: Dinas PU, Dinas Perhubungan, PDAM, DLH, Disdukcapil, Dinkes, Inspektorat, and Lainnya
- **Keyword-based fallback** — if LLM classification fails, falls back to rule-based keyword matching for resilience
- Auto-generates **unique ticket IDs** for complaint tracking

### 🛠️ Admin Dashboard
- View all submitted complaints with expandable ticket details
- Real-time **status management** (Menunggu Tanggapan → Diproses → Selesai)
- Displays reporter name, contact info, complaint content, timestamp, and assigned department

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Multi-page web application |
| **LLM** | DeepSeek (via OpenRouter API) | Generative AI responses + complaint classification |
| **Embeddings** | Jina Embeddings v3 (API) | Query & document vectorization |
| **Vector Database** | FAISS (faiss-cpu) | Similarity search over document chunks |
| **Document Processing** | Custom chunking pipeline | PDF → Text → Chunks → Embeddings → FAISS index |
| **NLP Framework** | LangChain | LLM abstraction (ChatOpenAI, message schemas) |
| **Caching** | Streamlit `@cache_resource` + LRU dict | FAISS index & embedding caching |
| **Deployment** | Streamlit Cloud | Production hosting |

---

## Knowledge Base

The RAG system is built on official government documents:

| Document | Size | Description |
|----------|------|-------------|
| Perda Kota Cimahi No. 8 Tahun 2014 | 148 KB (text) | Municipal regulation |
| Perda No. 8 Tahun 2011 (IMB) | 96 KB (text) | Building permit regulations |
| Perwal Cimahi No. 6 Tahun 2024 | 138 KB (text) | Mayor's regulation |

**Vector DB Stats:**
- Total chunks: **870+** document segments
- FAISS index size: **3.5 MB**
- Embedding dimensions: **1024** (Jina v3)

---

## Project Structure

```
AI-Assistant-Cimahi/
├── app4.py                    # Main application (557 lines)
│                              #   - RAG chatbot with streaming
│                              #   - Complaint system + AI classification
│                              #   - Admin dashboard
├── mergechunk.py              # FAISS search utility / testing script
├── deploy_helper.py           # Deployment preparation script
├── requirements.txt           # Python dependencies
├── secrets_template.toml      # API key template
├── EmbeddingModel.ipynb       # Embedding experiments notebook
├── JinaEmbedding.ipynb        # Jina Embeddings pipeline notebook
├── DEPLOYMENT_GUIDE.md        # Production deployment guide
├── .streamlit/
│   └── config.toml            # Streamlit UI configuration
├── docs/                      # Source PDF documents (Perda/Perwal)
├── extracted/                 # Processed data
│   ├── faiss_index            # FAISS vector index (3.5 MB)
│   ├── faiss_metadata.json    # Index-to-document mapping
│   ├── chunks.json            # Document chunks with metadata
│   ├── embeddings.json        # Raw embedding vectors
│   └── *.txt                  # Extracted text from PDFs
└── vectordb/                  # ChromaDB (legacy, replaced by FAISS)
```

---

## Quick Start

### Prerequisites
- Python 3.8+
- [OpenRouter API Key](https://openrouter.ai) (free tier available)
- [Jina AI API Key](https://jina.ai) (1,000 requests/day free)

### Installation

```bash
# Clone the repository
git clone https://github.com/WillyHanafi1/AI-Assistant-Cimahi.git
cd AI-Assistant-Cimahi

# Create virtual environment
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp secrets_template.toml .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your API keys

# Run the application
streamlit run app4.py
```

### Environment Variables

```toml
OPENROUTER_API_KEY = "sk-or-..."
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "deepseek/deepseek-chat"
JINA_API_KEY = "jina_..."
```

---

## Deployment (Streamlit Cloud)

1. Fork/push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account → Select this repository
4. Set main file: `app4.py`
5. Add API keys in **Advanced Settings → Secrets**
6. Click **Deploy**

For detailed instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

---

## Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **FAISS over ChromaDB** | Faster L2 similarity search for production; ChromaDB was used in early development but replaced for performance |
| **Jina v3 over OpenAI embeddings** | Better multilingual (Indonesian) support, free tier with 1K req/day |
| **DeepSeek over GPT** | Cost-effective for Bahasa Indonesia responses via OpenRouter free tier |
| **Streaming enabled** | `llm.stream()` provides real-time character rendering — better UX vs waiting for full response |
| **Embedding cache (LRU)** | Reduces Jina API calls for repeated/similar queries; capped at 50 entries to prevent memory issues |
| **Dual classification** | LLM-first for accuracy, keyword-fallback for resilience when API fails |
| **Top-3 × 800 chars context** | Balances response quality vs token cost; top 3 from 50 FAISS results |

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built by <a href="https://github.com/WillyHanafi1">Willy Hanafi</a> · AI Automation Engineer
</p>
