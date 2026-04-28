# SynapseIP - Project State & Features

**Last Updated:** 2026-04-24

## 🧠 Project Overview
SynapseIP is an AI-powered "Vibe Coding Architect" platform. It takes a user's raw notes or ideas, evaluates their market viability, and automatically generates a highly granular, step-by-step "Architecture Blueprint" to guide developers using AI IDEs (like Cursor, Windsurf, or Antigravity).

## 🏗️ Architecture & Infrastructure
- **Backend:** FastAPI (Python)
- **Frontend:** Vanilla JS / HTML / CSS (No heavy framework, uses `script.js` and `style.css`)
- **Database:** SQLite hosted on a persistent disk mounted at `/data`. (Previously PostgreSQL on Neon).
- **Vector Storage:** Pinecone (for semantic RAG search across project notes).
- **AI Models:** Gemini 2.5 Flash / Pro (via `google-genai` SDK) for blueprint generation and synthesis.
- **Hosting:** Render (Web Service for backend).

## ✨ Current Features
- **User Authentication:** Custom JWT-based auth stored in `localStorage` (`synapseip_token`). Passwords hashed with `bcrypt`.
- **Project Organization:** Users can create multiple projects. State is isolated per project.
- **Onboarding Funnel:** A multi-step UI where users input their project name, platform, budget, and raw notes.
- **Intelligence Dashboard:** Evaluates the project's viability (Score 1-100), provides SWOT analysis, Market Analysis, and the "Harsh Truth". It also generates a preliminary high-level timeline (outline) of the required architecture steps.
- **Master Architect Blueprint:** 
  - Automatically generates an atomic, step-by-step feature build plan (up to ~50 steps).
  - Uses Pinecone RAG to embed specific context into each step.
  - Generates highly detailed, copy-pasteable Vibe Coding prompts for the user's target IDE.
  - Features interactive HTML checkboxes to track progress (state is saved to the database).
  - Alerts users via visually distinct yellow boxes when a step requires manual action (e.g., creating an API account).
  - Supports exporting the entire blueprint as a PDF.
- **Automated Blueprint QA Pipeline (Self-Healing):**
  - **Devil's Advocate QA Review:** Debates the initial architecture draft to find logical and database flaws.
  - **NPM Package Verification:** Pings `registry.npmjs.org` to ensure no dependencies are hallucinated.
  - **Lookback Validation:** Prevents context drift during the 50-step generation by strictly enforcing previous decisions.
  - **Zero-Token Path Validation:** Regex-based checker to automatically catch and correct file path drift without unnecessary LLM overhead.
- **Visual Architecture:** Automatically renders a `mermaid.js` flowchart of the component tree and database.
- **Multi-Modal Vision Ingestion:** Chrome extension allows capturing UI inspiration and extracts design tokens natively.
- **Vector Drift Pruning:** Built-in garbage collection to sync SQLite notes with Pinecone vector embeddings.
- **Follow-up AI Chat:** An integrated chatbot that can answer architectural questions based on the generated blueprint context.

## 🛠️ Developer Protocol
- Whenever a feature is added, modified, or removed, **UPDATE THIS FILE** immediately.
- Never edit `PROJECT_STATE.md` destructively unless removing deprecated features.
