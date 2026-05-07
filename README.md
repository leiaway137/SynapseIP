# SynapseIP - Vibe Coding Architect Platform

## 🧠 Project Overview
SynapseIP is an AI-powered "Vibe Coding Architect" platform. It takes a user's raw notes or ideas, evaluates their market viability, and automatically generates a highly granular, step-by-step "Architecture Blueprint" to guide developers using AI IDEs (like Cursor, Windsurf, or Antigravity).

## ✨ Key Features
- **User Authentication:** Custom JWT-based auth stored in `localStorage`.
- **Intelligence Dashboard:** Evaluates project viability, SWOT analysis, and generates a preliminary timeline.
- **Master Architect Blueprint:** 
  - Automatically generates an atomic, step-by-step feature build plan.
  - Uses vector search (ChromaDB/Pinecone) to embed specific context into each step.
  - Generates highly detailed, copy-pasteable Vibe Coding prompts for target IDEs.
- **Interactive Blueprint Editor:** A frontend-first interactive loop allowing users to view, edit, and collaborate on architectural blueprints with the AI.
- **Automated Blueprint QA:** Devil's advocate review, NPM dependency validation, lookback validation, and zero-token path validation.
- **Multi-Modal Vision Ingestion:** Chrome extension allows capturing UI inspiration.
- **Offline & Local LLM Support:** Fully integrated with local LLMs (e.g., RTX Qwen 122B) via an OpenAI-compatible interface, eliminating cloud dependencies.

## 🏗️ Architecture & Infrastructure
- **Backend:** FastAPI (Python)
- **Frontend:** Vanilla JS / HTML / CSS
- **Database:** SQLite (previously PostgreSQL)
- **Vector Storage:** ChromaDB for local vector search (previously Pinecone).
- **AI Models:** Local Qwen 122B Pro via `vLLM` and OpenAI-compatible interfaces (previously Google Gemini).

## 🚀 Project Iterations & History
The project has evolved through several major iterations to arrive at a fully local, privacy-preserving, high-performance architecture:

1. **Initial Cloud Architecture:** Built on FastAPI, Google Gemini 2.5 Flash/Pro, Pinecone, and Neon PostgreSQL. Focus was on generating multi-step blueprints.
2. **QingPath Interactive Loops:** Transitioned from rigid, non-transparent script-based blueprint generation to an interactive, frontend-first "Outside-In" development loop. Allowed collaborative iteration with the AI on UI and UX before technical implementation.
3. **Local & Offline Transition (The "Legacy Nexus" Migration):** Shifted infrastructure from cloud services to local alternatives to reduce prototyping costs. Substituted Neon PostgreSQL with local SQLite and replaced Pinecone with ChromaDB. 
4. **Local LLM Integration (Qwen 122B):** Integrated local NVIDIA RTX hardware running the Qwen 122B model. Implemented an OpenAI-compatible Duck Typing adapter to route all AI generation requests (Blueprints, Intel Reports, Schema Generation) to the local LLM.
5. **Architect Workbench Refinements:** Added Contextual Smart Edit capabilities, embedded executive summaries (Loop 0-2 drafts) into the final blueprint, and introduced a Database Schema Subagent to generate markdown tables of data models.
6. **Robust Parsing & Error Handling:** Improved regex parsing to handle markdown blocks from local LLMs, injected Pydantic response schemas into system prompts, and saved AI reasoning text to the database for debugging and transparency.
