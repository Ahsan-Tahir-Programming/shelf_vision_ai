---
title: ShelfVision AI
emoji: 🏪
colorFrom: red
colorTo: yellow
sdk: docker
pinned: false
---

# 🏪 ShelfVision AI

### AI-Powered Retail Shelf Compliance Analyzer

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb?style=flat&logo=react)](https://react.dev)
[![LangChain](https://img.shields.io/badge/LangChain-1.2-blue?style=flat)](https://langchain.com)
[![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-orange?style=flat&logo=google)](https://ai.google.dev)
[![HuggingFace](https://img.shields.io/badge/🤗-Live_Demo-yellow?style=flat)](https://ahsantahir1-shelfvision-ai.hf.space)

## 🔗 Live Demo

**[https://ahsantahir1-shelfvision-ai.hf.space](https://ahsantahir1-shelfvision-ai.hf.space)**

> Upload a shelf photo → Get instant compliance analysis → Chat with AI about results → Track trends over time

---

## 📌 What It Does

ShelfVision AI allows retail managers to:

- Upload shelf photos and get **AI-powered compliance scores (0-100)**
- Receive **zone-by-zone analysis** (Eye Level, Golden Zone, Top/Bottom shelf)
- **Chat naturally** with an AI agent about the shelf: _"Which brand is misplaced?"_
- **Track compliance trends** across multiple audits over time
- Generate **automated audit reports** with violation history

---

## 🧠 LLM Concepts Covered

| Concept                | Implementation                                |
| ---------------------- | --------------------------------------------- |
| **Multimodal LLM**     | Gemini Vision analyzes shelf images           |
| **Prompt Engineering** | Domain-specific retail compliance prompts     |
| **Structured Output**  | Pydantic-validated JSON from LLM responses    |
| **RAG**                | ChromaDB stores and retrieves audit history   |
| **Chat Memory**        | LangChain maintains full conversation context |
| **LLM Agents**         | LangGraph ReAct agent with 4 custom tools     |
| **Tool Use**           | Agent autonomously calls analytical functions |
| **LLM Deployment**     | FastAPI + Docker + Hugging Face Spaces        |

---

## 🛠️ Tech Stack

**AI / LLM**

- Google Gemini 2.0 Flash (Vision + Text generation)
- LangChain + LangGraph (Agent framework)
- ChromaDB (Vector database for RAG)
- Pydantic (Structured output validation)

**Backend**

- FastAPI (REST API — 5 endpoints)
- Uvicorn (ASGI server)
- Python 3.11

**Frontend**

- React 18 + Vite
- Tailwind CSS
- Axios

**DevOps**

- Docker
- Hugging Face Spaces (deployment)
- Git + GitHub

---

## 🏗️ Architecture

Shelf Image Upload
↓
Gemini Vision API
↓
Structured JSON Analysis (Pydantic)
↓
ChromaDB RAG ←→ LangGraph Agent
↓ ↓
Audit History 4 Custom Tools
↓
FastAPI Backend
↓
React Frontend

---

## 🤖 AI Agent Tools

The LangGraph ReAct agent autonomously decides which tool to call:

- `calculate_compliance_trend` — computes score trends over time
- `get_worst_performing_zones` — finds zones that fail most often
- `generate_audit_summary` — creates comprehensive audit reports
- `get_all_stores_stats` — returns database-wide statistics

---

## 🚀 Run Locally

### Prerequisites

- Python 3.11+
- Node.js 20+
- Gemini API Key (free at [aistudio.google.com](https://aistudio.google.com))

### Setup

```bash
# Clone repo
git clone https://github.com/Ahsan-Tahir-Programming/shelf_vision_ai
cd shelf_vision_ai

# Backend setup
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Create .env file
echo GEMINI_API_KEY=your_key_here > .env

# Start backend
uvicorn server:app --reload --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`

### Or Run With Docker

```bash
docker build -t shelfvision-ai .
docker run -p 7860:7860 -e GEMINI_API_KEY=your_key shelfvision-ai
```

---

## 📂 Project Structure

shelf-vision-ai/
├── app/
│ ├── api/routes.py # FastAPI endpoints
│ ├── core/
│ │ ├── analyzer.py # Gemini Vision analysis
│ │ ├── chat.py # LangChain chat session
│ │ ├── rag.py # ChromaDB RAG pipeline
│ │ └── config.py # Central configuration
│ ├── agents/
│ │ ├── agent.py # LangGraph ReAct agent
│ │ └── tools.py # 4 custom agent tools
│ └── models/schemas.py # Pydantic data models
├── frontend/ # React + Vite + Tailwind
├── server.py # FastAPI entry point
├── Dockerfile # Container configuration
└── requirements.txt

---

## 👨‍💻 Author

**Ahsan Tahir** — Python / AI Engineer  
Lahore, Pakistan

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](your-linkedin-url)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat&logo=github)](https://github.com/Ahsan-Tahir-Programming)
[![HuggingFace](https://img.shields.io/badge/🤗-HuggingFace-yellow?style=flat)](https://huggingface.co/AhsanTahir1)

---

_Built as a portfolio project combining Computer Vision expertise with LLM engineering_
