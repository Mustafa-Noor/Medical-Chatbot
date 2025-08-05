# Voice-Enabled Medical Chatbot 💬🩺

A smart, voice-first medical chatbot that dynamically chooses between structured Q&A, medical document RAG, or fallback LLM reasoning — all powered by open-source tools and deployed using free resources.

## 🌟 Project Highlights

- **Truly conversational AI** — no rigid flows or scripts.
- **Multi-source reasoning** — structured Q&A from CSVs, PDF-based RAG, and LLM fallback.
- **Full voice interaction** — seamless speech-to-text and text-to-speech.
- **All built using free-tier tools** — Hugging Face, Vercel, and Groq.

## 🧠 How It Works

The chatbot dynamically decides how to respond based on answer confidence using cosine similarity over semantic embeddings.

### 🔁 Retrieval Flow

We use `LangChain` and `LangGraph` to orchestrate conditional logic between:

- ✅ **CSV Q&A search** using Qdrant + Gemini embeddings  
- 📄 **RAG over structured PDF chunks** parsed with AI  
- 💬 **LLM fallback** (Mixtral via Groq) if confidence is low

LangGraph's node-based architecture handles branching and fallbacks in a clean, scalable way.

### 🔊 Voice AI Stack

- **Transcription:** [Whisper (Groq)]
- **Text-to-Speech:** [ElevenLabs]
- **Frontend:** React (with full voice-mode UI)
- **Backend:** FastAPI + PostgreSQL (session + user management)

### 📦 Embeddings

- **Gemini embeddings** power semantic chunking and retrieval
- All embeddings stored and searched using **Qdrant vector store**

### 🧾 PDF → Q&A Pipeline

We created a custom pipeline to:

1. Chunk medical PDFs intelligently (semantic-aware)
2. Extract structured Q&A pairs from each chunk
3. Embed them for RAG-style retrieval

## 🧪 Demo

Watch the [demo video](#) to see the system in action.  
Deployed here:
- [Frontend (Vercel)](#)
- [Backend API (Hugging Face Spaces)](#)

## 🚀 Stack

| Layer | Tech |
|------|------|
| Frontend | React + TailwindCSS |
| Backend | FastAPI + PostgreSQL |
| STT | Whisper (Groq API) |
| TTS | ElevenLabs |
| LLM | Mixtral via Groq |
| RAG | LangChain + LangGraph |
| Vector DB | Qdrant |
| Embeddings | Gemini |
| Deployment | Vercel + Hugging Face Spaces |

## 🤝 Acknowledgements

This project was built as part of our AI internship at **Nuclieos**.  
Big thanks to the team for the opportunity and support!

## 🧑‍💻 Contributors

- Mustafa (AI Intern)  
- Marwah Mohammed (AI Intern)

---

> Feel free to fork or reach out if you want to build something similar. This repo is a playground for combining retrieval, voice interfaces, and multi-hop reasoning using free and open tooling.
