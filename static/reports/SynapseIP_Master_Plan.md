# SynapseIP - Master Blueprint

**Designer:** leiaway

**Target Platform:** Antigravity

**Version:** 1.0.0

**Date:** 2026-04-20

---

## Executive Purpose
Automated via Follow-Up

---

## Table of Contents

1. [1. UI/UX Exploration & Frontend Scaffolding (Vibe Coder: Leiaway)](#1-ui/ux-exploration-&-frontend-scaffolding-(vibe-coder-leiaway))
2. [2. Backend Core: API & Database Foundation ('The Librarian')](#2-backend-core-api-&-database-foundation-('the-librarian'))
3. [3. Local Development Setup & Initial Proxy Configuration](#3-local-development-setup-&-initial-proxy-configuration)
4. [4. Chrome Extension Development: Ingestion ('The Collector')](#4-chrome-extension-development-ingestion-('the-collector'))
5. [5. Basic Document Generation Logic (Proof of Concept) & Formatting Manifest](#5-basic-document-generation-logic-(proof-of-concept)-&-formatting-manifest)
6. [6. Frontend Integration: Display & User Interaction](#6-frontend-integration-display-&-user-interaction)
7. [7. Commercialization Foundation: User Authentication & Credit System](#7-commercialization-foundation-user-authentication-&-credit-system)
8. [8. Advanced Document Generation: Iterative Expansion & Output Formatting](#8-advanced-document-generation-iterative-expansion-&-output-formatting)
9. [9. Deployment Preparation: Hosting (Vercel) & External Services](#9-deployment-preparation-hosting-(vercel)-&-external-services)
10. [10. Global Accessibility & LLM Abstraction ('Shanghai-Proofing')](#10-global-accessibility-&-llm-abstraction-('shanghai-proofing'))
11. [11. SynapseIP Meta-Feature: Generic Idea Viability Rubric](#11-synapseip-meta-feature-generic-idea-viability-rubric)

---

## 1. UI/UX Exploration & Frontend Scaffolding (Vibe Coder: Leiaway)

# 1. UI/UX Exploration & Frontend Scaffolding (Vibe Coder: Leiaway)

This document outlines the initial UI/UX exploration and frontend scaffolding for SynapseIP, focusing on creating a beautiful, usable, and modern interface. This feature is the user's primary interaction point with the application's core functionality, enabling them to visualize synced Gemini chats, generate extensive reports, manage credits, and receive viability assessments.

## Purpose and Logic

The frontend serves as the interactive dashboard for SynapseIP (which hosts the 'GrandDraft' functionality). Its core purpose is to provide a seamless user experience for managing automated follow-up processes and long-form document generation.

### Core Frontend Logic:

*   **Data Display:** Fetch and render saved Gemini chat data and generated reports from the FastAPI backend. Data will be primarily Markdown, requiring a Markdown parsing library.
*   **User Interaction:** Provide clear UI elements for triggering actions like syncing chats (via the Chrome extension), initiating report generation, and purchasing credits.
*   **Feedback & Status:** Visually communicate the status of background tasks (e.g., report generation progress), display the "Idea Health Score," and provide actionable feedback.
*   **Consistency:** Ensure all displayed content, especially reports and chat histories, adheres to a strict visual formatting manifest.

---

## Expected Outcome

### If it works:

*   A visually appealing, modern, and responsive web dashboard (React-based).
*   Seamless display of synced Gemini chat conversations, maintaining their structure and readability.
*   An intuitive interface to initiate the generation of multi-page "GrandDraft" reports.
*   Clear presentation of the "Idea Health Score" with actionable suggestions (questions to ask Gemini, prompt for generating outlines/reports).
*   Consistent application of styling (fonts, colors, spacing) across all UI elements and generated content.
*   Functional navigation between different sections of the app (e.g., Dashboard, Reports, Billing).

### If it fails:

*   Broken layouts, unresponsive elements, or an unappealing aesthetic.
*   Inconsistent rendering of Markdown content from Gemini chats or generated reports (e.g., varying header styles, misaligned tables).
*   Inability to trigger backend processes (e.g., "Generate Report" button doesn't work).
*   Confusing or absent feedback mechanisms for long-running tasks.
*   Difficulties in navigating the application or understanding its features.

---

## UI Component: The SynapseIP Dashboard & Content Renderer

The central UI component will be a dynamic web dashboard that adapts to display various content types. It is designed to be modern, intuitive, and efficient, aligning with the 'Leiaway' vibe coder's focus on user experience.

### Key Interactive Elements & Visual Design:

*   **Global Navigation (Sidebar/Header):**
    *   **Look & Feel:** Clean, minimalist design with clear icons and text labels. Collapsible sidebar for content focus.
    *   **Components:** Links to "My Chats," "My Reports," "Idea Validation," "Billing/Credits," "Settings."
    *   **User Feedback:** Active link highlighting for current page, subtle hover effects.

*   **"My Chats" / "Project Buckets" View:**
    *   **Look & Feel:** A card-based or list-based layout displaying individual Gemini conversations (or "Project Buckets"). Each entry should show a `title`, `timestamp`, and a "View" or "Generate Report" action button.
    *   **Components:** `ChatCard` or `ChatListItem` components.
    *   **User Feedback:** Visual indicators for successfully synced chats, quick access to view content.

*   **The `ChatResponse` / `ReportSection` Content Renderer (Modern UI Component Focus):**
    *   **Purpose:** This reusable React component is crucial for consistently displaying both raw Gemini chat history and the generated "GrandDraft" report content. It transforms raw Markdown into styled HTML.
    *   **Look & Feel (`Gemini Theme` & `Professional Report`):**
        *   **Headers (`h1`, `h2`, `h3`, `h4`):** Bold, dark gray (e.g., `#3c4043`). `h2` elements (Chapter Titles) will have a subtle bottom border (`2px solid #e0e0e0`) and significant `margin-top` to visually separate chapters.
        *   **Paragraphs (`p`):** `line-height: 1.6` for readability, `color: #3c4043` (dark gray).
        *   **Code Blocks (`pre`):** Dark background (`#282c34`), rounded corners (`border-radius: 4px`), light-colored text, internal padding.
        *   **Blockquotes (`blockquote`):** Light-gray background (`#f0f0f0`), distinct left vertical border (`4px solid #ccc`), indented text.
        *   **Lists (`ul`, `ol`):** Standard bullet points and numbered lists, with consistent indentation.
        *   **Tables (`table`):** Full width (`width: 100%`), subtle borders (`1px solid #ccc`), alternating row background colors for readability (e.g., `tbody tr:nth-child(even)`).
        *   **Horizontal Rules (`---`):** A thin, light-gray line across the page (`border-top: 1px solid #e0e0e0; margin: 20px 0;`).
        *   **Print Mode CSS:** Critical for generated PDFs. Ensure `page-break-before: always` for `h2` (Chapter Titles) and `page-break-inside: avoid` for `table` to prevent awkward page breaks.
    *   **User Interaction:**
        *   **Download Button:** Prominently displayed for generated reports.
        *   **Copy to Clipboard:** Icon next to code blocks or entire responses for easy copying.
    *   **Logic:**
        *   Accepts Markdown string as a prop.
        *   Uses a Markdown parsing library (e.g., `react-markdown`) to convert to HTML.
        *   Applies the specified CSS classes to the rendered HTML elements.

*   **"Idea Validation" View:**
    *   **Look & Feel:** A dedicated area to display the "Idea Health Score" prominently (e.g., a large, color-coded score indicator).
    *   **Components:**
        *   **Score Dial/Badge:** Circular or rectangular badge with the 0-100 score, dynamically colored (Green for >80, Yellow for 50-80, Red for <50).
        *   **Feedback Cards:** Separate cards for "Flop Risk," "Pivot Path," and the overall "Verdict" (Green Light, Yellow Light, Red Light). Each card should have clear headings and concise, actionable text.
        *   **Refinement Suggestions:** If the score is low, display a bulleted list of suggested questions for the user to ask Gemini, possibly with direct "Ask Gemini" links.
    *   **User Feedback:** Instant visual feedback on score changes after new data is synced or parameters are adjusted.

*   **Credit Management View:**
    *   **Look & Feel:** A clean interface showing current "Expansion Credits."
    *   **Components:** Credit balance display, a list of "Credit Packs" with clear pricing and "Buy Now" buttons (linking to Stripe checkout).

---

## Antigravity Designer Prompt for UI/UX Exploration & Frontend Scaffolding

```
Antigravity, assume the role of 'Leiaway', a Vibe Coder specializing in clean, modern, and highly usable React frontends for agentic applications. Your task is to scaffold the frontend UI/UX for the 'SynapseIP' application, which integrates the 'GrandDraft' document generation and 'Idea Validator' features. The target platform is a web dashboard.

I require a React.js frontend project structure with comprehensive styling using Tailwind CSS (or a modern CSS-in-JS solution if more appropriate for component-based styling, but keep it minimal and performance-focused). Ensure the application is responsive and looks great on desktop and mobile.

Specifically, build the following:

1.  **Project Initialization & Base Layout:**
    *   Create a new React project.
    *   Implement a clean, modern dashboard layout with a collapsible sidebar for navigation (e.g., "My Chats", "My Reports", "Idea Validation", "Billing", "Settings") and a main content area.
    *   Use a modern, professional sans-serif font (e.g., 'Inter', 'Roboto', or 'Open Sans').
    *   Establish a consistent color palette: a primary accent color (e.g., a professional blue like `#1a73e8`), a neutral dark gray for text (`#3c4043`), and subtle grays for backgrounds/borders.

2.  **Reusable `MarkdownRenderer` Component:**
    *   Create a React component named `<MarkdownRenderer />` that accepts a `markdownContent` prop (string).
    *   Utilize `react-markdown` or a similar robust library to parse the Markdown content into HTML.
    *   Apply the following strict CSS styling rules to the *rendered HTML elements within this component*:
        *   `h1`: Large, bold title (used once per overall document).
        *   `h2`: Section title, bold, primary accent color (`#1a73e8`), with a `2px solid #e0e0e0` bottom border and `margin-top: 40px`. This should visually signify new chapters.
        *   `h3`, `h4`: Sub-headers, bold, dark gray (`#3c4043`).
        *   `p`: `line-height: 1.6`, `color: #3c4043`.
        *   `code` blocks (`pre`): Dark background (`#282c34`), `border-radius: 4px`, `padding: 10px 15px`, light text color.
        *   `blockquote`: Light gray background (`#f0f0f0`), `border-left: 4px solid #ccc`, `padding: 10px 15px`, `margin: 15px 0`.
        *   `ul`, `ol`: Standard list styling with `padding-left` and `margin-bottom`.
        *   `table`: `width: 100%`, `border-collapse: collapse`, `border: 1px solid #ccc`. Style `th` (table headers) with a slightly darker background and `padding: 8px`. Style `td` (table data) with `padding: 8px` and subtle top borders.
        *   `hr` (horizontal rule `---`): `border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;`.
    *   Include a `@media print` query in the CSS to ensure:
        *   `h2` elements trigger a `page-break-before: always;`.
        *   `table` elements trigger `page-break-inside: avoid;`.
        *   Adjust font sizes and colors for optimal print readability (e.g., `h2` `color: #003366`, `font-size: 24pt`).

3.  **Dashboard Content Areas:**
    *   **"My Chats" / "Source Material" Section:** Display a list or grid of synced Gemini chats using the `<MarkdownRenderer />` component for each chat's content. Each item should have a title, timestamp, and a clear "View Details" button.
    *   **"Generate Report" Section:** A prominent button labeled "Generate 100-Page Report," with a placeholder for a progress indicator (e.g., a spinner or percentage bar) and an area for a downloadable link once the report is ready.
    *   **"Idea Validation" Section:**
        *   A clear display for the "Idea Health Score" (0-100), perhaps a circular progress bar or large numerical badge. Dynamically change color based on score (Red <50, Yellow 50-80, Green >80).
        *   Dedicated areas to display "Flop Risk" (in a warning-style card), "Pivot Path" (in an informational card), and the final "Verdict" (e.g., "Green Light (Build)") with appropriate iconography.
        *   A dynamically generated bulleted list of "Suggested Gemini Prompts" to improve the score, each with a copy button.
    *   **"Billing/Credits" Section:** Display the current "Available Credits" as a clear number. Include visually distinct "Buy Credit Pack" buttons linking to various tiers (e.g., "$19 for 100 pages," "$49 for 500 pages").

4.  **API Integration (Client-Side Stubs):**
    *   Create placeholder API calls (e.g., using `fetch` or Axios) for:
        *   `GET /api/chats` (to fetch synced Gemini data)
        *   `POST /api/generate-report` (to initiate report generation, expecting a `task_id` in return)
        *   `GET /api/report-status/{task_id}` (to poll for report generation status)
        *   `GET /api/report-download/{report_id}` (to get a download URL)
        *   `GET /api/user-credits` (to display credit balance)
        *   `POST /api/buy-credits` (to initiate a Stripe checkout session)
        *   `POST /api/assess-idea` (to trigger the viability engine)

Ensure all components are modular, reusable, and adhere to modern React best practices. Prioritize visual clarity, readability, and a smooth user experience.
```

---

## 2. Backend Core: API & Database Foundation ('The Librarian')

# 2. Backend Core: API & Database Foundation ('The Librarian')

## 1. Feature Description & Purpose

This feature establishes the foundational backend for SynapseIP, acting as the central "Librarian" for all user data. Its primary purpose is to receive, validate, and securely store Gemini chat discussions (which serve as "source material") from the Chrome Extension. It also lays the groundwork for user authentication, monetization logic, and resilient API interaction, especially considering deployment in regions with network restrictions. This backend must be built first, providing a stable target for the Chrome Extension to communicate with.

### Calculation and Logic

The backend core involves several intertwined logical components:

*   **API Endpoint for Ingestion:** A specific HTTP POST endpoint (`/ingest`) is created to act as a "digital mailbox." It is configured to accept incoming data (JSON payload) from the Chrome Extension, containing the `title`, `content`, `timestamp`, and `source_url` of a Gemini chat.
*   **Database Integration:** The received data is then processed and stored in a persistent database. Initially, SQLite is used for local development, with a schema designed to capture all necessary chat metadata and content. For a production environment, this would scale to a cloud-hosted solution like Supabase or PostgreSQL.
*   **Cross-Origin Resource Sharing (CORS):** The API must be configured to allow requests from different origins (i.e., the Gemini website where the Chrome Extension operates) to prevent browser security blocks.
*   **System Status Endpoint:** A simple root (`/`) endpoint provides a basic status check, indicating the operational health of the backend and the number of items stored.
*   **User & Credit Management (Monetization Foundation):** A `User` model is introduced into the database schema to track user-specific data, including 'Available Credits'. This is crucial for implementing a "Token Credit" monetization model, ensuring users have sufficient credits before resource-intensive operations (like report generation).
*   **LLM Abstraction Layer:** To mitigate vendor lock-in and enhance flexibility, an interface (`LLMInterface`) for Large Language Model (LLM) calls is defined. The initial implementation (`GeminiProvider`) adheres to this interface, allowing for easy swapping to other LLM providers (e.g., Claude, OpenAI, or local models) in the future without significant refactoring.
*   **Reverse Proxy Logic (Shanghai-Proofing):** For users in restricted regions, the backend acts as a reverse proxy. Instead of the client (Chrome Extension) directly calling the Gemini API, it sends data to SynapseIP's server. SynapseIP's server, hosted in an unrestricted region (e.g., Singapore, Tokyo), then makes the call to the actual Gemini API. This bypasses geographical restrictions for the LLM interaction. A "Timeout and Retry" mechanism is implemented for outbound LLM calls to handle network instability.
*   **Background Task Handling for Large Outputs:** To overcome hosting limitations (e.g., Vercel's 4.5MB payload limit for serverless functions), large processes like report generation are treated as background tasks. The API immediately returns a `task_id`, allowing the frontend to poll for status updates. The actual large output is saved to cloud storage (e.g., Vercel Blob), and a secure download link is provided upon completion.

---

## 2. Step-by-Step Logic Guide

This guide outlines the logical sequence for building the backend core, integrating necessary components and considerations for Antigravity development.

### 2.1. Project Initialization & API Setup

*   **Action:** Initialize a Python FastAPI project.
*   **Purpose:** Establishes the core web framework for the backend.
*   **Logic:**
    *   Use FastAPI for its speed, automatic interactive API documentation (Swagger UI), and ease of asynchronous programming.
    *   Configure the server to run on a local development port (e.g., `8000`).
*   **Antigravity Command / Skill:**
    `Initialize a Python FastAPI project.`

---

### 2.2. Database Schema Definition

*   **Action:** Define the database schema for `Gemini Sources` and `User` models.
*   **Purpose:** To systematically store raw chat data and manage user-specific information, including monetization credits.
*   **Logic:**
    *   **Gemini Sources Table:**
        *   `id`: Primary key, unique identifier for each chat entry.
        *   `title`: A brief title for the chat, allowing easy identification.
        *   `content`: The full Markdown text of the Gemini conversation (long text field).
        *   `timestamp`: When the chat was synced (for ordering and context).
        *   `source_url`: The original URL of the Gemini chat (for traceability).
    *   **User Table:**
        *   `id`: Primary key, unique user identifier.
        *   `username`/`email`: User identification.
        *   `available_credits`: Integer field to track remaining credits for monetization.
*   **Antigravity Command / Skill:**
    `Create a SQLite database using SQLAlchemy. Define a 'Gemini Sources' schema with 'id', 'title', 'content' (long text), 'timestamp', and 'source_url'. Add a 'User' model with 'id', 'username', and 'available_credits'.`

---

### 2.3. Data Ingestion Endpoint

*   **Action:** Create a POST endpoint `/ingest` to receive chat data.
*   **Purpose:** Serves as the dedicated entry point for the Chrome Extension to push Gemini chat content to the backend.
*   **Logic:**
    *   The endpoint expects a JSON object containing the `title`, `content`, `timestamp`, and `source_url`.
    *   Upon receiving data, it saves the content into the `Gemini Sources` table.
    *   Implement data validation to ensure the incoming payload meets the expected format.
*   **Antigravity Command / Skill:**
    `Create a POST endpoint at /ingest that accepts a JSON object with 'title', 'content', 'timestamp', and 'source_url'. This endpoint should save the received data to the 'Gemini Sources' table in the SQLite database.`

---

### 2.4. Core Logic & LLM Abstraction

*   **Action:** Implement an LLM abstraction layer and proxy logic.
*   **Purpose:** Decouples the application from a specific LLM provider and enables access from restricted regions.
*   **Logic:**
    *   **`LLMInterface`:** Define an abstract base class or interface (e.g., `ChatService`) with methods like `generate_content(prompt, context)`.
    *   **`GeminiProvider`:** Implement `ChatService` using the Gemini API. This is where the actual Gemini API calls happen. Configure it to use a custom `base_url` for proxying.
    *   **Reverse Proxy Endpoint (`/generate-report`):** This endpoint, when called, will use the `GeminiProvider` (or whichever LLM is configured). It acts as a middleman, forwarding sanitized requests to the actual Gemini API and handling the responses.
    *   **Network Resilience:** Include "Timeout and Retry" logic for all outbound LLM calls within the proxy to handle transient network issues, especially critical for connections across firewalls.
*   **Antigravity Command / Skill:**
    `Create a Python 'ChatService' interface with a 'generate_content()' method. Implement a 'GeminiProvider' class that adheres to this interface. Build a FastAPI proxy endpoint `/generate-report` that accepts user requests, utilizes the 'GeminiProvider' to make API calls, and includes 'Timeout and Retry' decorators for all external LLM interactions. Ensure the Gemini API call logic can swap the official Google endpoint for a proxy relay via a configurable 'base_url'.`

---

### 2.5. Monetization Foundation

*   **Action:** Integrate user authentication and credit-based access control.
*   **Purpose:** To enable commercialization via a "Token Credit" model, ensuring that resource-intensive operations are gated by user credits.
*   **Logic:**
    *   **Authentication (Future):** While not fully implemented in this MVP, the `User` model prepares for future user authentication services (e.g., Clerk, NextAuth).
    *   **Credit Check Middleware:** Implement logic to check a user's `available_credits` before executing calls to the `/generate-report` endpoint.
    *   **Credit Cost Calculation:** Define the logic to deduct credits based on the requested report's length or complexity (e.g., 1 credit per 1,000 words generated). This will happen as part of the report generation workflow.
*   **Antigravity Command / Skill:**
    `Modify the backend to integrate a basic credit system. The 'User' model (from schema) should track 'available_credits'. Implement middleware for the '/generate-report' endpoint to check if the user has a positive credit balance before allowing generation. Deduct credits based on an estimated 'Credit Cost' (e.g., 1 credit per 1,000 words or per chapter).`

---

### 2.6. Hosting & Scalability Considerations (for Future Deployment)

*   **Action:** Prepare the backend for potential cloud deployment, addressing payload limits.
*   **Purpose:** Ensures the app can scale beyond local development and handles large report outputs efficiently.
*   **Logic:**
    *   **Vercel Optimization:** Acknowledge Vercel's 4.5MB payload limit for serverless functions.
    *   **Background Processing:** Implement a mechanism where calling `/generate-report` initiates a background task, returning a `task_id` immediately.
    *   **Cloud Storage for Outputs:** The large report output from the LLM should be streamed or saved directly to a cloud storage service (e.g., Vercel Blob).
    *   **Download Link:** The API should provide a temporary, signed download URL for the generated report once processing is complete.
*   **Antigravity Command / Skill:**
    `Configure the FastAPI backend to handle large report generation as a background task. The '/generate-report' endpoint should return a 'task_id' immediately. Implement polling logic via '/status/{task_id}' for the frontend. Once complete, save the generated report (potentially large) to Vercel Blob and return a signed download URL. Ensure this architecture handles Vercel's 4.5MB payload limit by not returning the full report directly.`

---

## 3. Expected Outcome

### 3.1. If the Feature Works

*   **API Responsiveness:**
    *   Navigating to `http://127.0.0.1:8000/` (or your deployed URL) displays a simple "Status" message, including the current count of items in the `Gemini Sources` database.
    *   Swagger UI (`http://127.0.0.1:8000/docs`) correctly lists the `/ingest` and `/generate-report` endpoints with their expected request/response schemas.
*   **Data Ingestion:**
    *   When the Chrome Extension sends data to `/ingest`, the backend successfully receives the JSON payload.
    *   A new record appears in the `Gemini Sources` table within the database, containing the `title`, `content`, `timestamp`, and `source_url`.
    *   The `content` field should accurately store the full Markdown text from the Gemini chat.
*   **Monetization Foundation:**
    *   A `User` record can be created or exists with an `available_credits` balance.
    *   Attempts to call `/generate-report` for a user with zero or negative credits are blocked, returning an appropriate error (e.g., HTTP 403 Forbidden).
*   **LLM Abstraction & Proxy:**
    *   The backend can successfully make outbound API calls to the configured LLM (e.g., Gemini) via the `GeminiProvider`.
    *   For restricted regions, the backend acts as a successful proxy, forwarding requests to the LLM and receiving responses, without the client needing a VPN for this step.
*   **Background Report Generation:**
    *   Calling `/generate-report` immediately returns a `task_id` to the client.
    *   The client can poll `/status/{task_id}` and receive progress updates, eventually getting a secure download URL for the complete report stored in Vercel Blob.

### 3.2. If the Feature Fails

*   **API Unreachable:**
    *   Browser shows "Connection refused" or "Site can't be reached" when trying to access `http://127.0.0.1:8000/`.
    *   Backend logs show server startup errors or port conflicts.
*   **CORS Errors:**
    *   Browser console displays "Cross-Origin Request Blocked" messages when the Chrome Extension tries to send data to `/ingest`.
*   **Data Ingestion Failure:**
    *   Backend logs show database connection errors, SQLAlchemy errors, or data validation failures (`Pydantic` errors in FastAPI).
    *   The `/` status page does not show an increment in stored items after an ingestion attempt.
*   **Monetization Logic Errors:**
    *   `/generate-report` endpoint fails with unexpected errors even when credits are available, or allows generation when credits are zero.
    *   Credit deductions are incorrect or not applied.
*   **LLM Integration/Proxy Failure:**
    *   Backend logs show errors connecting to the Gemini API (`requests` library errors, API key issues).
    *   For proxy, internal API calls to Gemini fail due to firewall blocks or incorrect `base_url` configuration.
    *   "Timeout and Retry" logic might fail to recover from temporary network issues, leading to unhandled exceptions.
*   **Payload Limit Exceeded:**
    *   If large reports are attempted to be sent directly, Vercel (or similar serverless platforms) will return a 413 Payload Too Large error.
    *   Background tasks fail to save to cloud storage or provide invalid download URLs.

---

## 4. UI Component for this Feature

While primarily a backend feature, a minimal UI is needed for status and future interaction.

### UI Component: 'Backend Status Dashboard' (Admin/Diagnostic)

*   **Purpose:** To provide a simple visual confirmation that the backend is operational and receiving data. This is an administrative or developer diagnostic tool, not a primary user-facing feature.
*   **Component Type:** Simple text/number display.
*   **Placement:** The root URL of the backend API (e.g., `http://localhost:8000/`).
*   **Functionality:**
    *   Displays a greeting or "Backend Operational" message.
    *   Shows the current count of "Gemini Sources" stored in the database.
*   **Modern UI Considerations:**
    *   **Aesthetics:** Clean, minimal text-based display. No complex styling needed for a diagnostic page, but ensuring readability with a clear font.
    *   **Usability:** Instantly recognizable status. A simple refresh should update the count.

### Future User-Facing UI Components (Conceptual)

*   **Saved Chats List:** A main dashboard in the React frontend (`www.synapseip.com`) displaying a list of all synced Gemini chats, each with its `title`, `timestamp`, and `source_url`. Each item could be styled to resemble a Gemini chat bubble using `ChatResponse.css`.
*   **Credit Balance Display:** A prominent display of the user's `Available Credits` in the user dashboard.
*   **Generate Report Button:** A button next to "Saved Gemini Chats" or within a selected "Project Bucket" to initiate the `/generate-report` process. This button should visually indicate "processing" when clicked and eventually provide a download link.

---

## 5. Antigravity Designer Prompt

```
Antigravity, let's build the 'Backend Core: API & Database Foundation' for SynapseIP, focusing on robust data handling, monetization groundwork, LLM abstraction, and international accessibility for local deployment.

Here's the comprehensive plan:

1.  **Project Initialization:**
    *   Initialize a Python FastAPI project named 'SynapseIP-Backend'.
    *   Configure the backend to run locally on `http://127.0.0.1:8000`.

2.  **Database Setup:**
    *   Use SQLAlchemy to create a SQLite database (`synapseip.db`) within the project.
    *   Define two database models:
        *   `GeminiSource`:
            *   `id`: Primary Key (Integer), auto-incrementing.
            *   `user_id`: Foreign Key to `User.id`.
            *   `title`: String, non-nullable.
            *   `content`: Text (long text), non-nullable.
            *   `timestamp`: DateTime, auto-populated on creation.
            *   `source_url`: String, nullable.
        *   `User`:
            *   `id`: Primary Key (Integer), auto-incrementing.
            *   `username`: String, unique, non-nullable.
            *   `email`: String, unique, non-nullable.
            *   `available_credits`: Integer, default 0, non-nullable.

3.  **API Endpoints:**
    *   **GET `/` (Status Page):**
        *   Returns a JSON response indicating "SynapseIP Backend Operational" and the total count of `GeminiSource` entries in the database. This is a basic diagnostic endpoint.
    *   **POST `/ingest` (Data Ingestion):**
        *   Accepts a JSON payload with `user_id`, `title`, `content`, `timestamp`, `source_url`.
        *   Validates the incoming data using Pydantic.
        *   Saves the data as a new `GeminiSource` entry in the database.
        *   Returns a success message with the ID of the new entry.
    *   **POST `/generate-report` (Report Generation Initiator):**
        *   Accepts a `user_id` and a `project_bucket_id` (representing a collection of `GeminiSource` entries).
        *   **Credit Check:** Before processing, verify if the `User` associated with `user_id` has sufficient `available_credits`. If not, return HTTP 403 Forbidden.
        *   Initiates the report generation as a background task.
        *   Immediately returns a `task_id` in the response, indicating the task has started. This avoids exceeding HTTP timeout limits.
    *   **GET `/report-status/{task_id}` (Report Status Checker):**
        *   Accepts a `task_id`.
        *   Returns the current status of the background report generation task (e.g., "pending," "processing," "completed," "failed").
        *   If "completed," returns a signed, temporary download URL for the report.

4.  **Core Logic Components:**
    *   **CORS Configuration:** Enable CORS for all origins (`*`) for local development, allowing the Chrome Extension to communicate.
    *   **LLM Abstraction:**
        *   Create a Python abstract class `ChatService` with an abstract method `generate_content(prompt: str, context: List[Dict]) -> str`.
        *   Implement `GeminiProvider(ChatService)` which uses the `google.generativeai` library.
        *   Ensure `GeminiProvider` uses a configurable `base_url` for its API calls, allowing it to easily switch from Google's official endpoint to a proxy endpoint.
    *   **Reverse Proxy / Outbound Call Logic:**
        *   Modify the `GeminiProvider`'s `generate_content` method to act as a reverse proxy for LLM calls. The backend will forward requests to the actual Gemini API.
        *   Implement a `@retry` decorator (e.g., using `tenacity` library) for all outbound Gemini API calls to handle network instability with retries and exponential backoff.
    *   **Background Task Management:**
        *   Implement a simple in-memory task queue or integrate with a lightweight solution like `rq` or `Celery` (for eventual production scaling) for handling the `generate-report` background process.
        *   The background task should handle chunking the report generation to avoid LLM timeouts and payload limits, iteratively calling the `GeminiProvider`.
    *   **File Storage Integration:**
        *   When generating reports, save the final large `.docx` or `.pdf` file to a temporary local directory. For cloud deployment, this will be replaced with `Vercel Blob` (or a similar cloud storage solution).
        *   The `/report-status` endpoint should serve a download link to this stored file, generating a signed URL if necessary.

5.  **Development & Deployment Instructions:**
    *   Provide a `README.md` with detailed instructions on:
        *   Setting up the Python virtual environment.
        *   Installing `requirements.txt` (FastAPI, SQLAlchemy, google-generativeai, tenacity, uvicorn, python-docx/reportlab).
        *   How to run the FastAPI server locally using `uvicorn`.
        *   How to configure environment variables (e.g., `GEMINI_API_KEY`, `BASE_LLM_URL`).
        *   Basic instructions for testing endpoints (e.g., using `curl` or Postman).

Ensure the generated code is clean, follows best practices, and includes inline comments for clarity.
```

---

## 3. Local Development Setup & Initial Proxy Configuration

# 3. Local Development Setup & Initial Proxy Configuration

## 1. Feature Purpose and Logic

This feature establishes the fundamental local environment for SynapseIP, allowing for development and testing without immediate public deployment. It addresses the critical need for seamless data ingestion from Gemini chat sessions into the application's backend.

*   **Why Needed (Local Development Setup)**
    *   Provides a dedicated environment on the developer's machine to build, test, and debug the SynapseIP application's core functionalities.
    *   Creates the initial "Librarian" (FastAPI backend) which will receive and store Gemini chat data.
    *   Enables rapid iteration and development cycles before deployment.
*   **Why Needed (Initial Proxy Configuration)**
    *   **The Challenge: Mixed Content**: Gemini runs on a secure HTTPS connection (`https://gemini.google.com`), while local development servers typically run on an insecure HTTP connection (`http://localhost:8000`). Web browsers enforce strict security policies, blocking direct communication between an HTTPS page and an HTTP local server.
    *   **The Solution: Service Worker Proxy**: The Chrome Extension's "Service Worker" (a special background script) acts as a local proxy. It receives scraped data from the content script (running on `gemini.google.com`) and then securely forwards it to the local HTTP FastAPI backend, bypassing the browser's "Mixed Content" security restrictions.
    *   This ensures that Gemini chat data can be reliably sent to the local SynapseIP backend.
*   **Calculation/Logic**
    *   **Backend (FastAPI)**: Initializes a Python FastAPI application. It defines a `/ingest` POST endpoint that expects a JSON payload containing `title`, `content`, `timestamp`, and `source_url` of a Gemini chat. This data is then stored in a local SQLite database. A root `/` endpoint provides a simple status check.
    *   **Frontend (Chrome Extension)**:
        *   **Content Script**: Injects a UI button on the Gemini chat page. This script is responsible for identifying and scraping the relevant chat message content when the button is clicked.
        *   **Service Worker (Background Script)**: Receives the scraped data from the content script. It then performs a `fetch` request to `http://127.0.0.1:8000/ingest` (the local FastAPI endpoint), effectively bridging the HTTPS-to-HTTP communication gap.
    *   **Database (SQLite)**: A local file-based database schema is set up to persist the ingested Gemini chat data.

---

## 2. Expected Outcomes

### If it Works (Success Scenario)

*   **Antigravity Output**:
    *   The Antigravity Agent reports successful creation of a Python FastAPI project structure (e.g., `app/main.py`, `requirements.txt`).
    *   It indicates that the FastAPI server is running locally, typically on `http://127.0.0.1:8000`.
    *   A new folder (e.g., `/extension`) is created containing the Chrome Extension's files (`manifest.json`, `content.js`, `background.js`).
    *   Antigravity provides instructions on how to load an unpacked Chrome Extension in the browser.
*   **User Experience (Post-Setup)**:
    *   After loading the unpacked extension, navigating to `chrome://extensions` shows "SynapseIP Extension" loaded without errors.
    *   When visiting `https://gemini.google.com` and refreshing, a visually distinct "Sync to SynapseIP" button appears next to each Gemini chat response.
    *   Clicking this button on a Gemini response results in a brief visual confirmation (e.g., "Synced!").
    *   The Antigravity console (or FastAPI server logs) shows a successful POST request to `http://127.0.0.1:8000/ingest`.
    *   Accessing `http://127.0.0.1:8000/` in a browser displays a status page showing an incremented count of stored Gemini chats.

### If it Fails (Failure Scenario)

*   **Antigravity Output**:
    *   **Backend Errors**: Antigravity reports errors during Python dependency installation (`pip install`) or FastAPI server startup (e.g., "Port 8000 already in use," "ModuleNotFoundError").
    *   **Extension Errors**: Antigravity reports syntax errors in JavaScript files or malformed `manifest.json`.
*   **User Experience (Post-Setup)**:
    *   **Extension Load Failure**: In `chrome://extensions`, the SynapseIP Extension shows a red error banner (e.g., "Manifest file is missing or unreadable," "Failed to load extension").
    *   **Button Not Visible**: The "Sync to SynapseIP" button does not appear on `https://gemini.google.com` after refreshing, indicating an issue with the content script's injection or selectors.
    *   **Mixed Content Block**: Clicking the button causes a console error in the browser developer tools (F12) on the Gemini page, stating "Mixed Content: The page at 'https://gemini.google.com' was loaded over HTTPS, but requested an insecure resource 'http://localhost:8000/ingest'." This confirms the Service Worker's proxy logic is not correctly implemented or active.
    *   **Server Processing Error**: The FastAPI server logs show errors after receiving data, such as database write failures or JSON parsing issues, even if the request reached the server. The `http://127.0.0.1:8000/` status page would not reflect new entries.

---

## 3. User Interface Component

The primary user interaction for this feature will be a "Sync to SynapseIP" button within the Gemini chat interface.

*   **Component**: SynapseIP Sync Button
*   **Visual Design Requirements**:
    *   **Placement**: Integrate seamlessly within the existing Gemini chat bubble interface, ideally alongside the native "Copy" or "Share" actions. It should be unobtrusive yet easily discoverable.
    *   **Iconography**: Use a modern, minimalist icon. A cloud icon with an upward arrow (`cloud_upload`), a stylized 'S' (for SynapseIP), or a simple database icon (`database`) are suitable choices. The icon should have a contemporary, flat design.
    *   **Label**: "Sync to SynapseIP". The text should be concise and clear. For smaller screens or tighter layouts, the text could be omitted in favor of a tooltip on hover.
    *   **Styling**:
        *   **Appearance**: A subtle, rounded rectangular button with a light background and a contrasting brand color (e.g., a soft blue or green) for the icon/text. It should visually align with Gemini's modern UI.
        *   **Hover State**: Slightly darken the background or lighten the icon color to indicate interactivity.
        *   **Click/Active State**: Provide immediate feedback. This could be a quick color change to a vibrant green or a checkmark icon temporarily replacing the upload icon, along with a "Synced!" text message that fades out.
        *   **Disabled State**: If the button is temporarily unavailable (e.g., while a sync is in progress), it should appear faded or grayed out.
*   **Interactivity**:
    *   **On Click**: Initiates the scraping of the current Gemini chat response and sends it to the local SynapseIP backend.
    *   **Tooltip**: On hover, display a tooltip: "Send this Gemini response to SynapseIP for automated follow-up."
    *   **Confirmation**: Upon successful sync, display a temporary, non-intrusive "Synced!" message next to the button or as a small toast notification.
    *   **Loading State**: During active syncing, display a small spinner animation within the button or temporarily disable it.

---

## 4. Antigravity Designer Prompt

```
Antigravity, let's set up the local development environment for SynapseIP, focusing on secure local data ingestion from Gemini.

**PHASE 1: Core FastAPI Backend & Local Database (The Librarian)**

1.  **Project Initialization**: Create a new Python FastAPI project.
2.  **Local Server Configuration**: Configure this backend to run locally on `http://127.0.0.1:8000`.
3.  **Database Setup**:
    *   Use SQLAlchemy to create and manage a SQLite database file named `synapseip_local.db` in the project root.
    *   Define a `GeminiSource` model with the following schema:
        *   `id`: Primary Key, Integer
        *   `title`: String (e.g., "Gemini Chat [Date]")
        *   `content`: Text (stores the full Markdown chat response)
        *   `timestamp`: DateTime (records when the chat was synced)
        *   `source_url`: String (the URL of the Gemini chat)
4.  **API Endpoint (`/ingest`)**:
    *   Create a `POST` endpoint at `/ingest`.
    *   This endpoint should accept a JSON payload matching the `GeminiSource` model (excluding `id`).
    *   Upon receiving data, it should validate the payload and save it as a new record in the SQLite database.
5.  **CORS Configuration**: Ensure Cross-Origin Resource Sharing (CORS) is explicitly enabled for all origins (`*`) for development purposes, allowing the Chrome Extension to communicate with it.
6.  **Status Endpoint (`/`)**:
    *   Create a simple `GET` endpoint at the root path `/`.
    *   This endpoint should return a JSON response indicating the current status of the backend and the total count of `GeminiSource` entries in the database.
7.  **Local Run Instructions**: Provide a `README.md` file with clear instructions on how to install dependencies and run the FastAPI server locally using `uvicorn`.

**PHASE 2: Chrome Extension for Gemini Auto-Sync (The Messenger)**

1.  **Extension Structure**: Create a Manifest V3 Chrome Extension within a subfolder named `/extension` inside the main project directory.
2.  **Domain Permissions**: Configure the `manifest.json` to only run its content scripts on `https://gemini.google.com/*`.
3.  **Content Script (`content.js`)**:
    *   Inject a new button element next to *each* Gemini response message bubble on the `gemini.google.com` page. Look for the class `.message-content` or a similar stable selector for Gemini's response containers.
    *   The button should have:
        *   A modern, minimalist cloud-upload icon (`cloud_upload`).
        *   Text label: "Sync to SynapseIP".
        *   A tooltip on hover: "Send this Gemini response to SynapseIP for automated follow-up."
        *   On click, it should extract the full Markdown text content of its parent message bubble.
    *   Upon click, it should send a message containing the extracted chat text, current page URL, and a generated title (e.g., "Gemini Chat - [Current Date]") to the extension's `Service Worker`.
    *   Provide visual feedback (e.g., change button to a temporary green checkmark and "Synced!") upon successful transmission of data to the Service Worker.
4.  **Service Worker (`background.js`)**:
    *   Implement the Service Worker to listen for messages from the `content.js` script.
    *   When a message is received, construct a JSON payload for the FastAPI `/ingest` endpoint using the data from the content script.
    *   Crucially, the Service Worker must initiate a `fetch` POST request to `http://127.0.0.1:8000/ingest`. This will act as the local proxy to bypass the browser's "Mixed Content" security restrictions.
    *   Handle potential errors in the fetch request and send appropriate feedback back to the content script for UI updates.
5.  **Manifest Configuration**: Ensure `manifest.json` correctly declares content scripts, host permissions, and the service worker.

Once Antigravity has completed these tasks, run the FastAPI server locally and provide instructions for how to load the unpacked Chrome Extension. Then, test the full data flow.
```

---

## 4. Chrome Extension Development: Ingestion ('The Collector')

# SynapseIP Feature: 4. Chrome Extension Development: Ingestion ('The Collector')

## Why This Feature is Needed and its Logic

### Feature Rationale
The '4. Chrome Extension Development: Ingestion ('The Collector')' feature is crucial for SynapseIP as it directly addresses a core inefficiency: the manual copying and pasting of Gemini chat discussions. This feature streamlines the data ingestion process, transforming it from a laborious, error-prone task into a seamless, automated workflow. By acting as a direct 'Collector,' the extension ensures that valuable brainstorming sessions from Gemini are automatically and effortlessly integrated into SynapseIP's knowledge base. This significantly enhances user experience, preserves critical chat context and metadata, and allows users to maintain their creative flow without interruption, directly feeding the system for subsequent automated follow-up processing.

---

### Calculation/Logic
The ingestion logic is a multi-step process orchestrated between the Chrome Extension and the SynapseIP FastAPI backend:

1.  **Extension Activation & Script Injection:**
    *   The Chrome Extension's `manifest.json` is configured to activate its `content.js` script exclusively when the user navigates to `https://gemini.google.com/*`.
    *   Upon page load, the `content.js` script dynamically identifies chat message bubbles (using robust CSS selectors like `.message-content` or `data-testid` attributes) and injects interactive "Sync to SynapseIP" buttons.
2.  **User Interaction & Data Capture:**
    *   **In-Page Button:** When a user clicks an injected "Sync to SynapseIP" button next to an individual AI response, the `content.js` script extracts the Markdown text of that specific message.
    *   **Toolbar Popup Buttons:**
        *   "Sync Latest Response": Captures only the most recent AI response.
        *   "Sync Entire Conversation": Gathers all visible user and AI messages in the current chat thread.
    *   In both cases, the script also captures essential metadata: the `title` of the chat, a `timestamp` of the ingestion, and the `source_url` of the Gemini conversation.
3.  **Secure Data Transmission (Local Development & Reverse Proxy):**
    *   To overcome "Mixed Content" security blocks (where an HTTPS website like Gemini cannot directly post to a local HTTP server), a **Service Worker (Background Script)** in the extension mediates the communication.
    *   The `content.js` script sends the captured data to the background script.
    *   The background script then performs a `fetch` `POST` request to the SynapseIP FastAPI backend's `/ingest` endpoint. During local development, this targets `http://localhost:8000/ingest`. For public deployment, it targets the hosted API (e.g., Vercel), acting as a "Reverse Proxy" for enhanced stability and accessibility from regions like Shanghai.
4.  **Backend Ingestion & Storage:**
    *   The SynapseIP FastAPI backend receives the incoming JSON payload (containing `title`, `content`, `timestamp`, `source_url`) at its `/ingest` endpoint.
    *   The backend's business logic sanitizes and processes this raw data, then stores it securely in a persistent database (e.g., SQLite for local, Supabase/MongoDB for cloud). This forms the "source material" for generating comprehensive, multi-page reports.

---

## Expected Outcomes: Success and Failure

### On Successful Operation
*   **User Interface:**
    *   A prominent SynapseIP icon is visible in the Chrome browser's toolbar. Clicking it reveals a clean popup with "Sync Latest Response" and "Sync Entire Conversation" buttons.
    *   Within `gemini.google.com`, a subtle, branded "Sync to SynapseIP" button appears next to each AI-generated chat response.
*   **Data Flow & Feedback:**
    *   **In-Page Button Click:** The in-page button visually confirms the action with a brief animated checkmark or "Synced!" text. The corresponding chat message content and metadata are successfully sent to and stored in the SynapseIP backend database.
    *   **Toolbar Popup Button Click:** The popup's status indicator updates (e.g., "Last synced: [timestamp]") to confirm the action. The selected chat data (latest response or entire conversation) is sent to and stored in the SynapseIP backend database.
*   **Backend & Storage:**
    *   The SynapseIP backend logs successful `POST` requests to the `/ingest` endpoint.
    *   The database (local or cloud) shows new entries with the ingested chat content, title, timestamp, and source URL. A backend status endpoint (e.g., `/`) reflects an incremented count of stored Gemini sources.

---

### On Failed Operation
*   **User Interface Failures:**
    *   **No Button/Icon Display:** The SynapseIP toolbar icon is absent, or the "Sync to SynapseIP" buttons fail to appear on `gemini.google.com`. This indicates an issue with the extension's `manifest.json` configuration, permissions, or the `content.js` script failing due to a recent UI change on Gemini, preventing it from finding the correct injection points.
    *   **Non-Responsive Buttons:** Clicking any sync button (in-page or popup) yields no visual feedback or a generic browser error (e.g., "Page unresponsive"). This suggests a JavaScript error in `content.js` or `background.js` preventing event listeners or data capture logic from executing.
*   **Data Ingestion Failures:**
    *   **Network Errors/Mixed Content:** The browser's developer console displays "Mixed Content" warnings/errors, or network request failures to `localhost:8000/ingest`. This is a critical indicator that the service worker is not correctly mediating the HTTPS-to-HTTP communication, or that CORS headers on the FastAPI backend are misconfigured, blocking cross-origin requests.
    *   **API Errors (Backend):** The SynapseIP backend's logs show errors such as "404 Not Found" (if the `/ingest` endpoint path is incorrect), "422 Unprocessable Entity" (if the incoming JSON payload from the extension is malformed or missing required fields), or database-related errors (e.g., connection issues, schema mismatches).
    *   **Data Not Stored:** Despite apparent successful API calls, the SynapseIP backend's status page (`/`) does not update its item count, or direct inspection of the database reveals no new entries. This points to a problem within the backend's data processing, validation, or actual write operations to the database.

---

## Beautiful, Usable, Modern UI Components

The user interface for 'The Collector' Chrome Extension will prioritize a sleek, intuitive, and non-intrusive design that blends seamlessly with the modern web.

### 1. SynapseIP Collector Toolbar Icon & Popup
*   **Toolbar Icon:**
    *   **Design:** A custom vector-based icon featuring a stylized 'S' for SynapseIP. The 'S' should subtly incorporate an upward-moving arrow or a series of dots/lines flowing upwards, symbolizing data collection and automation.
    *   **Aesthetics:** The icon will utilize a `linear-gradient(45deg, #673AB7, #2196F3)` (deep purple to calm blue) for a premium, modern feel. A `box-shadow: 0 1px 3px rgba(0,0,0,0.2);` will add a slight depth effect.
    *   **Interaction:** On hover, a tooltip will display "SynapseIP: Sync Current Chat".
*   **Popup Menu (Accessed via Toolbar Icon Click):**
    *   **Container:** A minimalist card-like design with `border-radius: 12px;` and a soft, unobtrusive `box-shadow: 0 4px 12px rgba(0,0,0,0.1);`. Background will be `#FFFFFF` for light mode, adaptable for future dark mode support.
    *   **Header:**
        *   **Title:** "SynapseIP Collector" - bold, centered, using a clean sans-serif font (e.g., 'Inter' or 'Roboto' at 16pt) in a dark grey color (`#3C4043`).
        *   **Separator:** A thin `1px solid #E0E0E0;` horizontal rule for a subtle visual break below the title.
    *   **Action Buttons:**
        *   **"Sync Latest Response":** A prominent, full-width button with `border-radius: 8px;` and `padding: 10px 15px;`. It will use the `linear-gradient(45deg, #673AB7, #2196F3)` background with crisp white text. Hovering will trigger a slight `transform: translateY(-2px);` effect for responsiveness.
        *   **"Sync Entire Conversation":** An equally sized, secondary action button, styled as an outline. It will have a transparent background, text in SynapseIP's primary purple (`#673AB7`), and a matching `1px solid #673AB7` border, with `border-radius: 8px;` and `padding: 10px 15px;`. It will also feature a subtle hover effect.
    *   **Status Indicator:** Positioned discreetly below the buttons, a small text block (`font-size: 10pt; color: #7F878F;`) will display dynamic status messages like "Status: Connected" (with a small green circle icon) or "Last synced: [HH:MM AM/PM]". A subtle, looping spinner or "Syncing..." text will be used during active data transmission.

### 2. In-Page Contextual "Sync to SynapseIP" Button (on `gemini.google.com`)
*   **Placement:** This button will be intelligently injected into the Gemini chat interface, strategically placed next to each AI-generated message, ideally adjacent to Gemini's native interaction elements (like the "Copy" button) to maintain visual harmony.
*   **Design:** A small, unobtrusive square button (`width: 32px; height: 32px;`).
    *   **Aesthetics:** It will feature a light grey background (`#F0F2F5`) for light mode, dynamically adapting to a dark grey (`#2C2C2C`) for dark mode compatibility. A subtle `1px solid #E0E0E0;` border and `border-radius: 4px;` will give it a refined look.
    *   **Iconography:** The button will house a minimalist SVG icon depicting a cloud upload or a circular sync symbol, rendered in SynapseIP's primary brand purple (`#673AB7`), ensuring crispness and brand recognition.
    *   **Interaction:**
        *   **Hover:** The button will gently scale up (`transform: scale(1.05);`) and display a tooltip "Sync to SynapseIP".
        *   **Click Feedback:** Upon clicking, the icon within the button will smoothly animate into a vibrant green checkmark (`&#10003;`) or briefly display "Synced!" text for 1-2 seconds, then smoothly transition back to its original sync icon. This provides clear, immediate visual confirmation of successful ingestion.

---

## Antigravity Designer Prompt

```
Antigravity, design and implement the user-facing UI for the 'SynapseIP Collector' Chrome Extension.
The goal is to create beautiful, usable, and modern components for seamless Gemini chat ingestion.

**Project Name:** SynapseIP
**Feature:** Chrome Extension - Ingestion ('The Collector')
**Target Platforms:** Chrome Web Browser (for extension UI), gemini.google.com (for in-page injection)
**Brand Colors:** Primary Purple: #673AB7, Accent Blue: #2196F3, Neutral Grey: #F0F2F5 (light), #2C2C2C (dark)
**Typography:** Modern sans-serif (e.g., Inter, Roboto).

**UI Components Specifications:**

1.  ### Chrome Toolbar Icon
    *   **Visual Design:** Create a minimalist, elegant 'S' glyph for SynapseIP. Incorporate a subtle upward-moving arrow or a data-stream element within or around the 'S' to symbolize data collection.
    *   **Color Scheme:** Apply a `linear-gradient(45deg, #673AB7, #2196F3)` to the icon for a sophisticated brand presence. Add a soft, `1px 1px 3px rgba(0,0,0,0.2)` shadow for depth.
    *   **Interaction:** On hover, display a tooltip: "SynapseIP: Sync Current Chat".
    *   **Manifest Integration:** Define this icon in `manifest.json` as `icons` for different sizes (16, 32, 48, 128px).

2.  ### Extension Popup Menu (Accessed via Toolbar Icon Click)
    *   **Overall Aesthetic:** Card-like, modern design with `border-radius: 12px;` and a soft, unobtrusive `box-shadow: 0 4px 12px rgba(0,0,0,0.1);`. Background will be `#FFFFFF` for light mode, adaptable for future dark mode support.
    *   **Header:**
        *   **Title:** "SynapseIP Collector" - bold, centered, using a clean sans-serif font (e.g., 'Inter' or 'Roboto' at 16pt) in a dark grey color (`#3C4043`).
        *   **Separator:** A thin `1px solid #E0E0E0;` horizontal rule for a subtle visual break below the title.
    *   **Action Buttons:**
        *   **Button 1: "Sync Latest Response"**
            *   **Design:** Full-width, prominent button. Apply the `linear-gradient(45deg, #673AB7, #2196F3)` background. Text `color: #FFFFFF;`.
            *   **Shape:** `border-radius: 8px; padding: 10px 15px; margin-bottom: 10px;`.
            *   **Interaction:** Subtle `transform: translateY(-2px);` and `box-shadow` on hover.
        *   **Button 2: "Sync Entire Conversation"**
            *   **Design:** Outlined button. `background: transparent; color: #673AB7; border: 1px solid #673AB7;`.
            *   **Shape:** `border-radius: 8px; padding: 10px 15px;`.
            *   **Interaction:** Similar subtle hover effect.
    *   **Status Indicator:**
        *   **Placement:** Small text block below buttons.
        *   **Content:** Dynamic display like "Status: Connected" (with a small green circle icon `&#9679;`) or "Last synced: [HH:MM AM/PM]".
        *   **Font:** `font-size: 10pt; color: #7F878F;` (muted grey).
        *   **Loading State:** Implement a small, looping spinner or "Syncing..." text when data is being sent.

3.  ### In-Page Contextual "Sync to SynapseIP" Button (on gemini.google.com)
    *   **Injection Target:** Next to each AI response bubble (e.g., near Gemini's default "Copy" button).
    *   **Visual Design:**
        *   **Shape:** Small square button, `width: 32px; height: 32px;`.
        *   **Background:** Subtle light grey (`#F0F2F5`) for light mode, dark grey (`#2C2C2C`) for dark mode compatibility.
        *   **Border:** `1px solid #E0E0E0; border-radius: 4px;`.
        *   **Icon:** A minimalist cloud upload or sync icon in SynapseIP's primary brand color (`#673AB7`). Use an SVG for crispness.
    *   **Interaction:**
        *   **Hover:** Slightly increase scale (`transform: scale(1.05);`) and display a tooltip "Sync to SynapseIP".
        *   **Click Feedback:** Smoothly animate the icon to a green checkmark (`&#10003;`) or briefly display "Synced!" text. After 1-2 seconds, smoothly revert to the original icon. Use CSS transitions for this effect.

**Implementation Details for Antigravity Agent:**
*   Ensure the injected in-page button uses `position: absolute` or `flex` with appropriate offsets to not disrupt Gemini's native UI layout.
*   All styles should be encapsulated within a shadow DOM or by using highly specific class names to prevent CSS conflicts with Gemini's existing styles.
*   Provide the necessary HTML, CSS, and JavaScript for these components, ensuring full compatibility with the Manifest V3 Chrome Extension architecture.
*   Include placeholders for dynamic data (e.g., `[timestamp]`) and event listeners for button clicks to trigger the underlying data capture and transmission logic via the service worker.
```

---

## 5. Basic Document Generation Logic (Proof of Concept) & Formatting Manifest

# 5. Basic Document Generation Logic (Proof of Concept) & Formatting Manifest

This document outlines the architectural and logical steps for implementing the core document generation and formatting capabilities within SynapseIP on the Antigravity platform.

---

## 1. Feature Overview: The SynapseIP "GrandDraft" Engine

This feature introduces the "GrandDraft" engine, SynapseIP's core capability to transform fragmented Gemini brainstorming discussions into comprehensive, professionally formatted multi-page reports (initially a 10-page Proof of Concept, expandable to 100+ pages). It addresses the limitations of tools like NotebookLM by providing unrestricted output length and customizable formatting.

### Why this feature is needed
*   **Overcome Output Restrictions**: Existing tools often limit document length or customization, preventing users from creating truly extensive reports. SynapseIP will bypass these limitations.
*   **Professional Deliverables**: Users require polished, well-structured documents (business plans, whitepapers, step-by-step guides) for formal use cases.
*   **Consistency and Quality**: Without a defined structure, AI-generated content can "drift" in style and format over long documents, reducing credibility. This feature ensures uniformity.

### Calculation and Logic: The "Recursive Expansion" Loop
The core logic for generating multi-page reports relies on an iterative, agentic expansion process, carefully managing context and formatting across a large volume of content. This avoids a single, large API call that could lead to timeouts or loss of quality (AI "memory wall").

*   **Initialization**: The user triggers report generation via the SynapseIP dashboard.
*   **Outline Generation**: An Antigravity agent (Agent A) first generates a high-level, 20-chapter outline based on the entire set of ingested Gemini discussions (utilizing Gemini's large token window for initial context). This outline is structured as a JSON object.
*   **Iterative Chapter Expansion**: For each chapter in the outline:
    *   A dedicated Antigravity agent (Agent B) focuses *only* on expanding that specific chapter.
    *   It retrieves relevant "Source Material" (from the database/vector store) for that chapter.
    *   It uses the Gemini 1.5 Pro API to "Deep Dive" and generate 4-5 pages of professional content, adhering strictly to the "Formatting Manifest" (detailed below).
    *   The generated content for the chapter is saved as a Markdown artifact.
*   **Consistency Verification**: An Antigravity agent (Agent C, "Global Context Agent") performs cross-chapter checks to ensure logical flow and prevent contradictions between the newly generated chapter and preceding ones. This maintains narrative coherence across the entire document.
*   **Document Assembly**: Once all chapters are drafted and verified, the backend stitches together all individual Markdown chapter files into a single, cohesive document using a library like `python-docx` or `reportlab`.
*   **Final Output**: The assembled document is saved to cloud storage (e.g., Vercel Blob) and a secure download link is provided to the user.

---

## 2. Expected Outcomes

### If it works
*   **Document Generation**: Upon clicking the "Generate Report" button, a progress indicator will appear, updating dynamically as chapters are outlined, drafted, and verified.
*   **Successful Output**: After a processing period (which may be several minutes for a 100-page report), a clear "Download Report" button will become available on the UI.
*   **Consistent Formatting**: The downloaded `.docx` or `.pdf` file will adhere perfectly to the defined formatting rules:
    *   Correct hierarchy of headings (`#`, `##`, `###`, `####`).
    *   Proper use of horizontal rules (`---`) for visual breaks and page separation.
    *   Data presented in bulleted lists or Markdown tables.
    *   Professional tone with no "AI Talk" phrases.
    *   Mathematically formatted sections using LaTeX syntax.
*   **Error Resiliency**: The underlying `ChatService` abstraction allows seamless swapping of AI models if one provider faces issues. Large report generation will not hit Vercel payload limits as documents are stored externally and delivered via download links.

### If it fails
*   **Generation Timeout/Error**: The progress indicator might stall, or an error message like "Report Generation Failed: Please try again or simplify your request" could appear. This might be due to an API timeout (if the iterative loop isn't implemented correctly), an issue with the Gemini API key, or unexpected content causing the model to break.
*   **Inconsistent Formatting (AI Drift)**: The generated report may show varying header styles, inconsistent use of bolding, or informal language across different sections, indicating a failure to enforce the "Formatting Manifest."
*   **Memory Wall / Contradictions**: Later chapters might contradict earlier ones, or the narrative flow could break down, suggesting the "Global Context Agent" or prompt chaining is insufficient.
*   **Payload Limit Error**: If hosted on Vercel without proper cloud storage integration, attempts to directly return large documents will result in a 4.5 MB payload limit error, preventing the user from downloading the report.
*   **Broken Download Link**: The download button may appear, but clicking it results in a 404 error or a corrupted file, indicating an issue with cloud storage integration or file assembly.

---

## 3. User Interface (UI) Component: The "GrandDraft" Report Generator

This feature requires a dedicated, visually appealing UI component to initiate, track, and retrieve generated reports. It must provide clear feedback to the user throughout the asynchronous generation process.

### UI Component Name: `GrandDraftReportPanel`

This component will be accessible from the main SynapseIP dashboard, potentially linked from a "My Projects" or "Generate Reports" section.

### Visual Design Principles
*   **Clean and Modern**: Utilize Antigravity's default UI styling with subtle shadows, rounded corners, and a balanced layout.
*   **Action-Oriented**: Clearly highlight the primary "Generate" action.
*   **Feedback-Rich**: Provide real-time updates on generation progress to manage user expectations for long tasks.
*   **Accessible**: Ensure all interactive elements are clearly labeled and navigable.

### Component Structure and Elements

*   **Report Configuration Card (Initial State)**
    *   **Title**: "Generate Detailed Report"
    *   **Description**: "Turn your brainstormed ideas into a comprehensive business plan or whitepaper."
    *   **Input Field (Optional - for Report Title)**: A text input with a placeholder like "Enter your report title (e.g., 'Q3 Business Strategy')"
    *   **"Generate Report" Button**: A primary call-to-action button, e.g., `<button class="primary-button">Generate [10-Page PoC] Report</button>`. This button should clearly state the current target page count (e.g., "10-Page PoC") and become disabled once generation starts.
    *   **Context Selector (Future MVP+):** A dropdown or list to select which "Project Bucket" of Gemini conversations to use as source material. (For PoC, assume all available notes are used).

*   **Report Progress & Status Panel (During Generation)**
    *   This panel will replace or overlay the configuration card once "Generate Report" is clicked.
    *   **Title**: "Generating Your GrandDraft Report..."
    *   **Progress Bar**: A sleek, animated progress bar (e.g., `ProgressBar` component) that updates in real-time.
        *   Visually represents the overall completion (e.g., 0-100%).
        *   Can show discrete steps (e.g., "Step 1/4: Outlining Document...", "Step 2/4: Drafting Chapter X...", "Step 3/4: Verifying Consistency...", "Step 4/4: Compiling Final Document...").
    *   **Status Text**: A dynamic text display showing the current task or chapter being processed. E.g., "Currently drafting 'Market Analysis' chapter..."
    *   **Estimated Time Remaining (Optional but Recommended)**: A small text element showing a rough estimate.
    *   **"Cancel Generation" Button (Optional)**: A secondary button to halt the process if needed.

*   **Report Completion & Download Panel (After Generation)**
    *   **Title**: "Your GrandDraft Report is Ready!"
    *   **Success Message**: "Your [Report Title] (X pages) has been successfully generated."
    *   **Download Button**: A prominent button with a clear download icon and label, e.g., `<a href="[download_URL]" class="download-button" target="_blank">Download Report (.docx)</a>`.
    *   **"View in App" Button (Future MVP+)**: To open a rendered version of the report directly within the SynapseIP UI.
    *   **"Generate Another" Button**: A secondary button to return to the initial configuration state.

*   **Error State Panel**
    *   **Title**: "Report Generation Failed"
    *   **Error Message**: A clear, concise message explaining what went wrong (e.g., "API Timeout: The AI took too long to process. Try reducing the complexity of your notes." or "Server Error: Unable to save the document. Please try again.").
    *   **Action Buttons**: "Retry" (primary) and "Contact Support" (secondary).

### Designer Prompt for Antigravity

```
Antigravity, design a modern, functional UI component in React called `GrandDraftReportPanel` for the SynapseIP dashboard. This panel will manage the generation of long-form reports.

Follow these strict design principles:
1.  Use a clean, card-like layout with subtle shadows and rounded corners.
2.  Ensure clear visual hierarchy for states: Configuration, In-Progress, Completed, Error.
3.  Use an accessible color palette.

The component should include the following states and elements:

**1. Initial Configuration State**
*   A prominent title: "Generate Detailed Report"
*   A brief description: "Turn your brainstormed ideas into a comprehensive business plan or whitepaper."
*   An optional `TextField` for "Report Title" (placeholder: "Enter your report title (e.g., 'Q3 Business Strategy')").
*   A primary `Button` labeled "Generate [10-Page PoC] Report". This button should be disabled once clicked.

**2. In-Progress State**
*   Dynamically display a title: "Generating Your GrandDraft Report..."
*   Include a `ProgressBar` component (animated from 0-100%).
*   Display dynamic `StatusText` below the progress bar (e.g., "Currently drafting 'Market Analysis' chapter...").
*   An optional `EstimatedTimeRemaining` text (e.g., "Approx. 5 min remaining").
*   An optional `CancelButton` with a secondary style.

**3. Completed State**
*   Display a success title: "Your GrandDraft Report is Ready!"
*   Show a success message: "Your [Report Title] (X pages) has been successfully generated."
*   A primary `LinkButton` (looks like a button but acts as a link) with a clear download icon, labeled "Download Report (.docx)". The `href` will be dynamically set.
*   A secondary `Button` labeled "Generate Another Report" to reset the component.

**4. Error State**
*   Display an error title: "Report Generation Failed"
*   Show a clear `ErrorMessage` (e.g., "API Timeout: The AI took too long to process. Please try again.").
*   A primary `Button` labeled "Retry".
*   A secondary `Button` labeled "Contact Support".

**For the formatting of the actual report content and saved Gemini notes within the app's display areas:**
Create a reusable React component `<MarkdownRenderer content={markdownString} />` that:
*   Utilizes the `react-markdown` library to parse Markdown input.
*   Applies a CSS file (`MarkdownRenderer.css`) to style the generated HTML, adhering to a "Professional Report Theme". This theme should mimic the Gemini chat's GFM rendering for individual notes, but with print-optimized styles for reports:
    *   `h1, h2, h3` should be bold and a dark, professional gray (`#3c4043`). `h2` elements should have a subtle bottom border (`2px solid #e0e0e0`).
    *   `p` elements should have a `line-height` of `1.6` for readability.
    *   `pre` (code blocks) should have a dark background (`#282c34`) with rounded corners (`4px`).
    *   `blockquote` should have a light-gray background (`#f0f0f0`) and a prominent vertical border on the left (`4px solid #1a73e8`).
    *   Include a `@media print` block in the CSS to enforce:
        *   `h2 { page-break-before: always; color: #003366; font-size: 24pt; }` (for new chapters to start on new pages).
        *   `table { width: 100%; border: 1px solid #ccc; page-break-inside: avoid; }` (to prevent tables from splitting across pages in print).
```

---

## 4. Basic Document Generation Logic (Proof of Concept)

This section details the backend logic for performing the initial document generation. We will focus on creating a 10-page proof-of-concept (PoC) report to validate the core expansion loop and formatting manifest.

### 4.1. Core Logic: The `GenerateReport` Endpoint

*   **Function**: This endpoint orchestrates the entire document generation process, from outline creation to final document assembly.
*   **Trigger**: A `GET` request from the frontend (triggered by the `GrandDraftReportPanel` UI component).
*   **Input**: The system will fetch all available "Gemini Sources" from the database for the PoC. In future iterations, it will accept a `project_id` or similar identifier.
*   **Output**: A `task_id` immediately, and a signed download URL upon successful completion of the background task.

### 4.2. Step-by-Step Implementation Guide (Antigravity)

1.  **Introduce LLM Abstraction Layer (Critical First Step)**
    *   **Why**: Decouples your application from a specific AI provider, allowing you to switch between Gemini, Claude, OpenAI, or local models without a major refactor. This is crucial for stability (especially in regions like Shanghai) and cost optimization.
    *   **Prompt for Antigravity**:
        ```
        "Create a `ChatService` interface in Python. It should define a method `generate_content(prompt: str, context: list) -> str`. Then, implement a `GeminiProvider` class that implements this `ChatService` interface. The `GeminiProvider` should use the `Gemini 1.5 Pro API` (with API key from .env). My main app logic should interact only with `ChatService`, not directly with `GeminiProvider`."
        ```
    *   **Expect if it works**: You will see Python files (`chatservice.py`, `geminiprovider.py`) defining the interface and its Gemini implementation. Your backend code will instantiate `GeminiProvider` but refer to it via `ChatService`.
    *   **Expect if it fails**: Antigravity might struggle with the `interface` concept in Python or place the API key directly in code. If so, refine the prompt to be more specific about abstract base classes (`abc` module) or environment variable usage.

2.  **Implement Asynchronous Task Processing**
    *   **Why**: Prevents API timeouts for long-running report generations, provides real-time progress to the user, and adheres to Vercel's 4.5MB payload limit by saving large files externally.
    *   **Prompt for Antigravity**:
        ```
        "Modify the FastAPI backend to handle long-running `/generate-report` requests as background tasks.
        1.  When a GET request hits `/generate-report`, it should immediately return a `task_id` (UUID).
        2.  The actual report generation (using the `ChatService`) should run in a separate background process or worker (e.g., using `Celery` or a simple `asyncio` task if Celery is too complex for this PoC).
        3.  Create a `GET /status/{task_id}` endpoint that returns the current progress (e.g., 'OUTLINING', 'CHAPTER 1/20 DRAFTING', 'COMPLETED') and a `download_url` if complete.
        4.  Integrate `Vercel Blob` for file storage. The generated `.docx` or `.pdf` file should be saved there, and the `/status/{task_id}` endpoint should return a signed public URL for download upon completion. Ensure the `python-docx` or `reportlab` library is installed and used for document assembly."
        ```
    *   **Expect if it works**: The `/generate-report` endpoint returns a `task_id` instantly. Repeated calls to `/status/{task_id}` show progress updates until a `download_url` is returned. The final document is accessible from Vercel Blob.
    *   **Expect if it fails**: The initial `GET /generate-report` call might still block or time out if the background task setup is incorrect. The `/status` endpoint might return incorrect statuses or fail to provide a download link. Vercel Blob integration issues could lead to files not being saved.

3.  **Create the `GenerateReport` Endpoint with Iterative Logic**
    *   **Why**: This is the core "Architect" logic that leverages multi-agent orchestration to build the large document page by page.
    *   **Prompt for Antigravity**:
        ```
        "Add the `/generate-report` logic to the FastAPI backend.
        1.  Fetch ALL 'Gemini Sources' from the SQLite database.
        2.  Use the `ChatService` (specifically the `GeminiProvider` implementation) to first generate a `JSON Outline` for a 10-page 'Initial Blueprint' report, comprising 2-3 main chapters, each with 2-3 sections.
        3.  Implement an `Iterative Loop`: For each chapter in the generated outline:
            a.  Use `ChatService` to expand that specific chapter into ~3-4 paragraphs of content, adhering strictly to the `GrandDraft Formatting Manifest` (provided in the next step).
            b.  Save the generated Markdown for each chapter temporarily.
            c.  (Self-correction/Verification): Add a basic check using `ChatService` to ensure the generated chapter content is consistent with the preceding content and the overall outline. If not, retry generation for that chapter.
        4.  After all chapters are generated, stitch them into a single `.docx` file using `python-docx` or `.pdf` using `reportlab`.
        5.  Save the final document to `Vercel Blob` and update the task status with the download URL."
        ```
    *   **Expect if it works**: The backend successfully calls the `ChatService`, generates an outline, iteratively drafts chapters, and produces a 10-page document. The progress bar in the UI updates smoothly.
    *   **Expect if it fails**: AI might generate repetitive content, deviate from the outline, or produce content that violates the formatting rules. If the iterative loop is poorly managed, it might still hit API rate limits or processing limits, even with background tasks.

---

## 5. Formatting Manifest: The "GrandDraft" Style Guide

This manifest is a strict set of rules that the AI (via `ChatService`) must follow during document generation. It ensures pixel-perfect consistency across hundreds of pages and is crucial for professional output.

### Why this feature is needed
*   **Eliminate AI Drift**: Prevents the AI from changing formatting or tone as it generates longer documents.
*   **Professional Appearance**: Ensures all reports have a consistent, high-quality, and readable layout.
*   **Scalable Styling**: By using semantic Markdown and a CSS stylesheet, future design changes can be applied globally with minimal effort.

### Calculation and Logic: Markdown for Structure, CSS for Style

*   **Markdown as Skeleton**: The AI is instructed to use specific Markdown syntax elements (`#`, `##`, `---`, `*`, `1.`, tables, blockquotes) for content structure and hierarchy.
*   **CSS as Skin**: The frontend application (React) takes the raw Markdown output from the backend, parses it into HTML using a library (e.g., `react-markdown`), and then applies a custom CSS stylesheet to render it beautifully and consistently. The CSS also contains print-specific rules.
*   **Server-Side Control**: To guarantee consistency, the application code (not the AI) programmatically inserts the top-level headings (e.g., `# Document Title`, `## Chapter Title`) before feeding prompts for the body content to the AI.

### 5.1. The GrandDraft Formatting Manifest (To be injected into AI prompts)

This manifest is a crucial part of the prompt engineering for the `ChatService.generate_content` method when generating chapters and sections.

*   **1. Document Hierarchy (The Skeleton)**
    *   **L1 - Document Title (`#`)**: Used *exactly once* at the very beginning of the entire report.
    *   **L2 - Chapter Titles (`##`)**: Used for main chapters (e.g., "1. Executive Summary"). Each Chapter Title *must* be preceded by a Horizontal Rule (`---`) to indicate a page break for the PDF/DOCX generator.
    *   **L3 - Section Headers (`###`)**: Used for thematic breaks *within* a chapter (e.g., "3.1. Market Opportunity").
    *   **L4 - Sub-points (`####`)**: Used only for specific data groupings or "Deep Dive" callouts, ensuring a maximum of four header levels.

*   **2. Standardized Components**
    *   **Tables**: Any comparison, financial projection, or timeline *must* be formatted in a Markdown table.
        *   *Constraint*: No more than 5 columns to ensure it fits on a standard A4 PDF page.
    *   **Blockquotes (`>`)**: Used *exclusively* for "Executive Summaries" at the start of each chapter and "Key Takeaways" at the end of sections or chapters.
    *   **Lists**:
        *   Use bullet points (`*`) for non-sequential items.
        *   Use numbered lists (`1.`) for step-by-step instructions or priorities.

*   **3. Typography & Tone**
    *   **Boldness**: Use `**Bold**` only for key terms, new technical concepts, or specific emphasis (e.g., product names). Do not bold entire sentences or paragraphs.
    *   **No "AI Talk"**: Prohibit conversational filler phrases like "Sure, here is chapter 5," "As an AI model," "In conclusion," or "I hope this helps." The output must be the *raw, professional content only*.
    *   **LaTeX for Math**: All financial formulas, technical metrics, or complex mathematical expressions must be wrapped in `$math$` for professional rendering (e.g., `$E=mc^2$`).

### 5.2. Implementing CSS in the Frontend for Consistent Display

The `MarkdownRenderer` component, as specified in the UI component prompt, will apply the following CSS to ensure consistent display and print readiness.

```css
/* MarkdownRenderer.css - This ensures every page of your report looks identical */

.report-container h1 {
    font-family: 'Inter', sans-serif; /* Modern sans-serif font */
    color: #1a73e8; /* SynapseIP primary blue */
    font-size: 32px;
    margin-bottom: 30px;
    text-align: center;
}

.report-container h2 {
    font-family: 'Inter', sans-serif;
    color: #3c4043; /* Dark gray for chapter titles */
    font-size: 28px;
    font-weight: 700;
    border-bottom: 2px solid #e0e0e0; /* Subtle underline */
    padding-bottom: 10px;
    margin-top: 40px;
    margin-bottom: 20px;
}

.report-container h3 {
    font-family: 'Inter', sans-serif;
    color: #3c4043;
    font-size: 22px;
    font-weight: 600;
    margin-top: 30px;
    margin-bottom: 15px;
}

.report-container h4 {
    font-family: 'Inter', sans-serif;
    color: #5f6368; /* Slightly lighter gray for sub-points */
    font-size: 18px;
    font-weight: 500;
    margin-top: 20px;
    margin-bottom: 10px;
}

.report-container p {
    font-family: 'Inter', sans-serif;
    line-height: 1.7;
    color: #3c4043;
    margin-bottom: 15px;
}

.report-container strong {
    font-weight: 700;
}

.report-container ul, .report-container ol {
    margin-left: 20px;
    margin-bottom: 15px;
    color: #3c4043;
}

.report-container li {
    line-height: 1.6;
    margin-bottom: 5px;
}

.report-container hr {
    border: none;
    border-top: 1px solid #c0c0c0;
    margin: 50px 0;
}

.report-container pre { /* Code blocks */
    background-color: #282c34;
    color: #abb2bf;
    padding: 15px;
    border-radius: 6px;
    overflow-x: auto;
    font-family: 'Fira Code', monospace;
    margin-bottom: 20px;
}

.report-container blockquote {
    background-color: #f0f0f0; /* Light gray for emphasis */
    border-left: 4px solid #1a73e8; /* Primary blue left border */
    padding: 15px 20px;
    margin: 25px 0;
    font-style: italic;
    color: #3c4043;
    border-radius: 4px;
}

.report-container table {
    width: 100%;
    border-collapse: collapse;
    margin: 25px 0;
    font-family: 'Inter', sans-serif;
    color: #3c4043;
}

.report-container th, .report-container td {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: left;
}

.report-container th {
    background-color: #f8f8f8;
    font-weight: 600;
}

/* Print-specific styles */
@media print {
  .report-container h1 {
    font-size: 36pt;
    page-break-after: always; /* Ensure title gets its own page or is at the top of page 1 */
  }
  .report-container h2 {
    page-break-before: always; /* Every Chapter starts on a new page */
    color: #003366; /* Darker blue for print */
    font-size: 24pt;
    margin-top: 60px; /* More space for print layout */
  }
  .report-container h3 {
    page-break-before: auto; /* Allow sections to follow */
    font-size: 18pt;
    margin-top: 40px;
  }
  .report-container p, .report-container li {
    font-size: 11pt;
    line-height: 1.5;
  }
  .report-container table {
    width: 100%;
    border: 1px solid #ccc;
    page-break-inside: avoid; /* Prevents tables from being split across pages */
  }
  .report-container hr {
      page-break-before: always; /* Force page break before each new chapter horizontal rule */
      visibility: hidden; /* Hide the visual rule in print but keep its function */
      height: 0;
  }
}
```

### Designer Prompt for Antigravity (for Formatting Manifest Integration)

```
Antigravity, refine the `GenerateReport` function within the FastAPI backend and the `MarkdownRenderer` React component to strictly enforce the `GrandDraft Formatting Manifest`.

**For the FastAPI Backend (GenerateReport logic):**
1.  **Inject Manifest into Prompts**: Ensure the entire "GrandDraft Formatting Manifest" (Document Hierarchy, Standardized Components, Typography & Tone sections) is included as a SYSTEM instruction for *every* `ChatService.generate_content` call, especially when generating chapter outlines and individual chapter content.
2.  **Programmatic Headers**: Instead of letting the AI generate the top-level headers (L1/L2), have the Python backend code explicitly prepend them to the AI's output for each chapter.
    *   For the overall report title, prepend `# [User Provided Report Title]` once at the very beginning.
    *   For each new chapter, prepend `---` (for page break) followed by `## [Chapter Name]` before the AI's content for that chapter.
3.  **Strict Enforcement**: Instruct the AI (via the prompt) that any deviation from these rules will result in a regeneration attempt, emphasizing the "MANDATORY FORMATTING" aspect.
4.  **LaTeX Rendering**: If the `python-docx` or `reportlab` library supports it, ensure that `$math$` syntax is correctly interpreted and rendered as mathematical equations in the final document output. If not, add a note about this limitation or suggest a alternative.

**For the React Frontend (`MarkdownRenderer` component):**
1.  **Integrate CSS**: Ensure the provided `MarkdownRenderer.css` (including the `@media print` rules) is correctly linked and applied to the component that displays both saved Gemini chats and generated reports.
2.  **Markdown Parsing**: Verify that `react-markdown` correctly parses all standard Markdown elements (headers, lists, tables, blockquotes, bolding).
3.  **Print Functionality**: Enable a browser-level print function for the report view that properly utilizes the `@media print` CSS rules, ensuring chapter page breaks and table integrity.

**Expected Outcome:**
The generated PoC report, when viewed in the app or downloaded, must consistently reflect all rules defined in the `GrandDraft Formatting Manifest` and appear professional across all sections.
```

---

## 6. Frontend Integration: Display & User Interaction

# 6. Frontend Integration: Display & User Interaction

## 1. Purpose & Core Logic

This feature is crucial for enabling users to interact with SynapseIP, visualize their processed data, and trigger the core value proposition of the application: generating comprehensive long-form reports. Without a clear and intuitive frontend, the powerful backend logic remains inaccessible.

*   **Display Logic:**
    *   **Synced Gemini Chats:** The frontend must display incoming Gemini conversations. The raw Markdown text received from the Chrome Extension via the `/ingest` API endpoint needs to be parsed and rendered as formatted HTML. Metadata such as `title`, `timestamp`, and `source_url` should also be displayed.
    *   **Idea Viability Score:** Before a full report is generated, the system will evaluate the collected notes and provide a "Viability Score" (0-100). This score, along with conditional feedback (e.g., specific questions to refine the idea, or a "Ready to Generate" prompt), must be prominently displayed. This score helps guide the user to provide better input, which is critical for generating a high-quality 100-page report.
    *   **Credit Balance:** As SynapseIP operates on a "Token Credit Model," users need to see their current credit balance. This balance directly gates the `/generate-report` endpoint, so its display and a clear call-to-action for purchasing more credits are essential.
    *   **Generated Reports:** The final, long-form reports (e.g., 100+ pages) delivered by the backend as Markdown will be rendered in a dedicated viewer, adhering to the "GrandDraft Formatting Manifest." A download link for the `.docx` or `.pdf` file will also be provided.
*   **User Interaction Logic:**
    *   **Chrome Extension Sync:** A "Sync to SynapseIP" button or icon within the Gemini (and other AI chat) interface will allow one-click transfer of chat data to the app's backend.
    *   **Report Generation Trigger:** A prominent "Generate Report" button on the app's dashboard will initiate the report creation process. This button's availability will be tied to the user's credit balance and potentially the viability score.
    *   **Credit Purchase:** Clear links or buttons to direct users to a credit purchase flow (Stripe integration) will be needed.
    *   **Feedback Interaction:** Buttons or prompts to encourage users to refine their notes based on the viability score, or to proceed with generation.

---

## 2. Expected Outcomes

### If it works

*   **Seamless Chat Sync:** Users will click a clearly visible "Sync to SynapseIP" button/icon on their AI chat platform, and the conversation content will appear almost instantly within their SynapseIP dashboard, formatted cleanly.
*   **Clear Viability Guidance:** Upon reviewing synced notes, users will see an "Idea Health Score" from 0-100, accompanied by actionable advice if the score is low (e.g., "Add a budget section") or a "Ready to Generate" button if the score is high.
*   **Transparent Monetization:** The user's current "Expansion Credits" balance will be visible. When attempting to generate a report, an estimated credit cost will be displayed, and if insufficient credits are available, a clear prompt to "Buy More Credits" will appear, linking directly to the Stripe checkout page.
*   **Professional Report Display:** Generated reports will be rendered on the screen with consistent, professional formatting (headers, lists, tables, code blocks as per the GrandDraft Formatting Manifest), looking like a polished document. A prominent "Download Report" button will allow users to save it as a `.docx` or `.pdf`.
*   **Responsive UI:** All interactions will feel fluid and responsive, providing immediate feedback (e.g., loading spinners during generation, success/error messages).

### If it fails

*   **Broken Sync:** The "Sync to SynapseIP" button may be missing, non-functional, or fail silently, preventing chats from appearing in the app.
*   **Confusing Feedback:** The viability score might not appear, or the feedback messages are generic, unhelpful, or lack clear calls to action.
*   **Monetization Blocker:** Users are unable to see their credit balance, the "Generate Report" button is greyed out without explanation, or the credit purchase flow fails or is confusing.
*   **Unformatted Output:** Generated reports display as raw Markdown or unstyled text, appearing unprofessional, or the download link is broken/missing.
*   **Performance Issues:** The UI is sluggish, hangs during data loading or report generation requests, leading to a poor user experience.

---

## 3. UI/UX Component Design & Logic

The frontend for SynapseIP will be built using React, ensuring a modern, interactive, and visually appealing experience. The styling will leverage a consistent design system to maintain professionalism across all components.

### Overall Design Principles

*   **Modern & Clean:** A minimalist design with ample whitespace, using a neutral color palette accented by SynapseIP's brand colors (e.g., a vibrant blue or green for primary actions).
*   **Intuitive & Usable:** Clear labels, prominent calls-to-action, and logical information flow. Minimize cognitive load.
*   **Responsive:** All components must adapt seamlessly to various screen sizes, from large desktop monitors to mobile devices.
*   **Feedback-Rich:** Provide immediate visual feedback for all user actions (loading states, success notifications, error alerts).

### Synced Chat Dashboard Component

*   **Purpose:** To display a user's collection of synced Gemini (and other AI) conversations.
*   **Structure:**
    *   A main container for a list of "Project Buckets" (folders).
    *   Within each bucket, a list of individual synced chat entries.
    *   Each chat entry displays its `title`, `timestamp`, and a clickable area to view its `content`.
*   **Styling (`ChatResponse.css`):**
    *   The `react-markdown` library will be used to parse the incoming Markdown `content`.
    *   **Headers (h1, h2, h3):** Bold, dark gray (e.g., `#3c4043`).
    *   **Code Blocks (`<pre>`):** Dark background (e.g., `#282c34`), rounded corners, light monospace font.
    *   **Blockquotes (`<blockquote>`):** Light-gray background (e.g., `#f1f3f4`) with a subtle vertical border on the left (e.g., `4px solid #dadce0`).
    *   **Paragraphs (`<p>`):** Standard readable font (e.g., 'Inter', sans-serif), `line-height: 1.6`, dark gray color (e.g., `#3c4043`).
    *   **Lists (`<ul>`, `<ol>`):** Clear indentation and spacing.
*   **Interactions:**
    *   Clicking a chat title expands to show its full content.
    *   Option to "Delete" or "Archive" chats.
    *   A prominent "Generate Report from This Bucket" button at the top of each bucket.

### Report Generation Control Panel

*   **Purpose:** The central hub for initiating report generation and managing credits.
*   **Structure:**
    *   **Credit Balance Display:** A clear display of "Available Credits" (e.g., a badge or number).
    *   **"Buy More Credits" Button:** A highly visible button linking to the Stripe integration.
    *   **"Generate Report" Button:** The primary call to action.
    *   **Estimated Cost Display:** Below the "Generate Report" button, show a dynamic estimate of "This report will cost X Credits."
    *   **Input Fields (Optional/Future):** Text area for additional user prompts or parameters for the report (e.g., "Target Audience: Investors," "Focus on Market Strategy").
*   **Styling:**
    *   A card-like structure with a subtle shadow.
    *   Primary button styling for "Generate Report" (e.g., SynapseIP brand blue/green, rounded).
    *   Secondary button styling for "Buy More Credits."
    *   Credit balance displayed in a clean, easily parsable format.
*   **Interactions:**
    *   Clicking "Buy More Credits" opens a Stripe checkout page in a new tab or modal.
    *   Clicking "Generate Report" triggers the backend process, changing the button state to "Generating..." and potentially displaying a progress bar.
    *   If insufficient credits, the "Generate Report" button is disabled or shows a tooltip with a message like "Insufficient credits. Please purchase more."

### Idea Viability Score Display

*   **Purpose:** To provide real-time feedback on the quality of the user's notes for report generation.
*   **Structure:**
    *   **Score Card:** A prominent card displaying "Idea Health Score: X/100."
    *   **Conditional Feedback:**
        *   If score `< 50` (Too Vague): Display a message like "Your notes are too scattered for a professional plan. Consider these questions:" followed by 3 specific questions for refinement and a "Refine Notes" button.
        *   If score `50-80` (Brainstorming): Display "Good foundation! Consider focusing on X to improve your score." with an "Outline Architect" button.
        *   If score `> 80` (Execution): Display "Excellent notes! You're ready to generate a high-quality report." with a prominent "Ready to Generate 100-Page Report" button.
*   **Styling:**
    *   Color-coded score (e.g., red/orange for low, yellow for medium, green for high).
    *   Visually distinct sections for score and feedback.
    *   Action buttons (Refine, Outline, Generate) that are clear and accessible.
*   **Interactions:**
    *   "Refine Notes" button could open a text editor or guide for adding more detail.
    *   "Outline Architect" button (future feature) could lead to an AI-assisted outlining tool.
    *   "Ready to Generate 100-Page Report" button directly triggers the generation process (similar to the main control panel button).

### Long-Form Report Viewer & Downloader

*   **Purpose:** To display the generated report content in a browser-friendly, professional format and allow for download.
*   **Structure:**
    *   A large, scrollable content area for the report.
    *   A "Download Report" button (for `.docx` or `.pdf`).
    *   Optional: "Print Preview" button.
*   **Styling (`ReportViewer.css` extending `ChatResponse.css`):**
    *   This component will also use `react-markdown` but apply a more formal, print-oriented CSS.
    *   **L1 - Document Title (`#`):** Large, centered, bold title.
    *   **L2 - Chapter Titles (`##`):** Blue (e.g., `#1a73e8`), bold, 24pt, with a `2px solid #e0e0e0` bottom border, forcing a `page-break-before: always` in print mode.
    *   **L3 - Section Headers (`###`):** Bold, dark gray, 18pt.
    *   **L4 - Sub-points (`####`):** Bold, slightly smaller.
    *   **Horizontal Rules (`---`):** A subtle, thin line across the page, also acting as a `page-break-before: always` in print mode.
    *   **Tables:** `100% width`, `1px solid #ccc` border, `page-break-inside: avoid` in print mode.
    *   **Blockquotes:** As defined in `ChatResponse.css`, but potentially more prominent for Executive Summaries.
    *   **LaTeX for Math:** Displayed using a math rendering library (e.g., `react-katex`).
*   **Interactions:**
    *   Scrolling through the extensive document.
    *   Clicking "Download Report" triggers the download of the file from the Vercel Blob URL provided by the backend.

### Chrome Extension User Interaction

*   **Purpose:** To facilitate frictionless data ingestion from AI chat platforms.
*   **Structure:**
    *   **Browser Bar Icon:** A small, branded icon in the Chrome browser toolbar.
    *   **In-Page Button:** A small, discreet "Sync to SynapseIP" button injected next to each AI response bubble (e.g., near the Gemini "Copy" icon).
*   **Styling:**
    *   The browser icon should be SynapseIP's logo.
    *   The in-page button should be small, perhaps a subtle gray or blue, with a clear icon (e.g., a cloud upload arrow). It should not significantly disrupt the native chat UI.
*   **Interactions:**
    *   Clicking the browser bar icon "sucks up" the *entire* current conversation history and sends it to the app.
    *   Clicking the in-page button next to a specific response sends *only that response* to the app.
    *   Visual feedback on successful sync (e.g., a brief green checkmark, small notification).

---

## 4. Antigravity Designer Prompt

```text
Antigravity, design and implement the complete React frontend for SynapseIP, focusing on a beautiful, usable, and modern UI.

**Core Requirements:**
1.  **Project Setup:** Initialize a new React project integrated with the existing FastAPI backend (running on `http://localhost:8000` initially). Ensure proper routing for dashboard, report viewer, and credit management pages.
2.  **Global Styling:** Create a `globals.css` file to define a clean, modern design system:
    *   **Font:** "Inter" sans-serif.
    *   **Primary Accent Color:** #1a73e8 (Google Blue, or similar vibrant blue/green).
    *   **Neutral Palette:** Dark Gray (#3c4043), Medium Gray (#e0e0e0), Light Gray (#f1f3f4), White (#ffffff).
    *   **Shadows:** Subtle, consistent box-shadows for cards and interactive elements.
    *   **Spacing:** Use a consistent grid system (e.g., multiples of 8px).
3.  **Authentication/User Profile Section:**
    *   Implement basic user login/logout UI.
    *   Display the user's name/email.
    *   Show "Available Credits: [X]" prominently as a badge or card.
    *   Include a clear call-to-action button: "Buy More Credits" linking to `/credits-purchase`.
4.  **Synced Chat Dashboard Component (`src/components/ChatDashboard.jsx` & `ChatDashboard.css`):**
    *   Display a scrollable list of "Project Buckets" (e.g., `div` elements representing folders).
    *   Inside each bucket, render individual "Gemini Source" entries.
    *   For each source: Display `title`, `timestamp`. Clicking expands to show `content`.
    *   Use the `react-markdown` library to render the `content` Markdown.
    *   Style the markdown output using `ChatDashboard.css` to mimic Gemini's appearance:
        *   `h1, h2, h3`: bold, dark gray.
        *   `pre` (code blocks): dark background, rounded corners, light font.
        *   `blockquote`: light-gray background, vertical left border (e.g., 4px solid #dadce0).
5.  **Report Generation Control Panel Component (`src/components/ReportControls.jsx`):**
    *   Integrate the "Available Credits" display from the user profile.
    *   Add a prominent "Generate New Report" primary button.
    *   Below it, dynamically display "Estimated Cost: [X] Credits."
    *   If credits are insufficient, disable the "Generate New Report" button and display a tooltip "Insufficient credits. Buy more."
    *   Add placeholder input fields for "Report Type (e.g., Business Plan)" and "Additional Instructions" (multi-line text area).
6.  **Idea Viability Score Display Component (`src/components/ViabilityScore.jsx`):**
    *   Display "Idea Health Score: [X]/100" in a visually distinct card.
    *   Conditionally render feedback based on score (mock data for now, actual integration later):
        *   `< 50`: Red text, "Your notes need more detail." List 3 bulleted questions (e.g., "Define your target market."). Include a "Refine Notes" button.
        *   `50-80`: Orange/Yellow text, "Good start! Consider adding a competitive analysis." Include an "Outline Report" button.
        *   `> 80`: Green text, "Excellent! Ready for a full 100-page report." Include a "Generate 100-Page Report" button.
7.  **Long-Form Report Viewer & Downloader Component (`src/pages/ReportViewer.jsx` & `ReportViewer.css`):**
    *   This page should render the full generated report content (from the backend).
    *   Use `react-markdown` and apply a new `ReportViewer.css` for professional document styling, overriding `ChatDashboard.css` where necessary:
        *   `h1`: Large, centered document title.
        *   `h2` (Chapter Titles): #1a73e8 color, 24pt, `2px solid #e0e0e0` border, `page-break-before: always` (for print media query).
        *   `h3` (Section Headers): Dark gray, 18pt.
        *   `p`: `line-height: 1.6`, standard readable font.
        *   `hr` (`---`): thin line, `page-break-before: always` (for print media query).
        *   Tables: `width: 100%`, `1px solid #ccc` borders, `page-break-inside: avoid` (for print media query).
    *   Include a prominent "Download Report" button that will receive a URL for the generated `.docx` or `.pdf` file.
    *   Implement responsive design for optimal viewing on all devices.

**Interaction Flows:**
*   When a user clicks "Generate New Report," update the UI to show a "Generating Report..." spinner or progress bar.
*   Once the backend responds with a report URL, display it in the `ReportViewer` component.

**Focus:** Create a beautiful, functional UI structure that can be easily extended and styled. Prioritize clarity and user guidance. Assume backend API endpoints `/ingest`, `/generate-report`, `/check-viability`, and `/credits-purchase` are available.
```

---

## 7. Commercialization Foundation: User Authentication & Credit System

# 7. Commercialization Foundation: User Authentication & Credit System

## 1. Feature Justification and Logic

### A. Why User Authentication & Credit System is Essential
This feature establishes the commercial viability and financial sustainability of SynapseIP. Without it, the application, which leverages high-cost AI models (Gemini API), would incur significant "Cost of Goods Sold" (COGS) without a revenue mechanism, making it unsustainable.

*   **High AI API Costs**: Generating extensive reports (100+ pages) incurs substantial Gemini API token costs, estimated at $1.00 to $5.00 per report.
*   **Risk Mitigation**: A direct flat subscription model is risky as "power users" could generate many expensive reports for a fixed fee, leading to significant financial losses.
*   **Revenue Generation**: This system enables SynapseIP to earn revenue to cover API expenses, operational overhead (hosting, payment fees, marketing), and generate profit, transforming it into a sustainable SaaS business.

### B. Core Commercialization Logic: The "Token Credit" Model
The recommended "Token Credit" model ensures a direct correlation between user consumption and revenue, effectively protecting profitability.

*   **User Value Proposition**: Users purchase "Credit Packs" (e.g., "$15 for 500 Expansion Credits"), directly paying for the AI resources they utilize. This is easy to understand: "You only pay for the AI you actually use."
*   **Credit Calculation**: Each major high-cost operation within SynapseIP, primarily report generation, consumes a predefined number of credits.
    *   **Unit Cost Examples**:
        *   Generating a single chapter (as part of an iterative loop) might cost 5 credits.
        *   Generating a full 100-page business plan might cost 100 credits.
    *   **Dynamic Costing**: Credit costs are dynamically calculated based on the report's requested length or estimated token usage (e.g., 1 credit per 1,000 words generated). This integrates seamlessly with the "Iterative Loop" generation strategy, where credits are consumed per chunk or chapter as content is generated.
*   **Profit Margin Target**: Aim for a **60-70% gross margin** for AI-native applications. This typically translates to a **3x markup** on the raw API token costs.
    *   **1/3 (API Cost)**: Covers the direct variable cost of Gemini API tokens.
    *   **1/3 (Operational Overhead)**: Covers fixed and semi-variable costs including hosting (Vercel), payment gateway fees (Stripe: ~2.9% + $0.30 per transaction), database storage (Supabase/MongoDB Atlas free tiers), and marketing efforts.
    *   **1/3 (Net Profit)**: Represents the actual profit for SynapseIP, ensuring business sustainability and room for reinvestment.
*   **Freemium Strategy**: Implement a "Freemium Sync" model to attract users:
    *   **Free Tier**: Users can sync unlimited Gemini chats to their dashboard without direct credit consumption (this is a low cost to the app owner).
    *   **Paid Tier**: Users pay "Credits" only when they initiate high-value operations like clicking the "Expand to 100-Page Plan" button or other advanced generation features.

---

## 2. Expected Outcomes

### A. Success Criteria
*   **Secure Access**: Users can successfully register and log in to SynapseIP using email/password or integrated social logins (Google, GitHub).
*   **Credit Transparency**: Authenticated users can clearly view their current "Available Credits" balance on their dashboard.
*   **Seamless Purchase**: Users can smoothly purchase "Credit Packs" via the integrated Stripe payment gateway.
*   **Instant Updates**: The purchase of credit packs instantly and accurately updates the user's "Available Credits" balance.
*   **Gated Functionality**: When a user attempts to generate a report, the system accurately calculates the `credit_cost` and only proceeds if `available_credits` >= `credit_cost`.
*   **Credit Consumption**: Upon successful initiation of report generation, credits are correctly deducted according to the report's length/complexity (e.g., per chapter in an iterative loop).
*   **Report Delivery**: The generated report is successfully processed and delivered (e.g., as a download link), consistent with the credit consumption.
*   **Data Security**: All user data (authentication details, credit balance, transaction history) is securely stored and protected.

### B. Failure Conditions
*   **Authentication Failure**:
    *   Users are unable to register new accounts due to backend errors (e.g., database connection issues, misconfigured authentication service).
    *   Existing users cannot log in due to invalid credentials, expired sessions, or service outages.
    *   Unauthenticated users attempt to access protected endpoints and are correctly rejected with an authorization error.
*   **Payment Processing Failure**:
    *   Stripe integration fails, preventing users from completing credit purchases (e.g., misconfigured API keys, network issues).
    *   The Stripe webhook malfunctions, causing purchased credits not to be added to the user's account, leading to user frustration and support tickets.
*   **Insufficient Credits Handling**:
    *   If a user attempts to generate a report with fewer `available_credits` than `credit_cost`, the `/generate-report` endpoint does **not** correctly reject the request, or it fails to display an informative error message like "Insufficient credits. Please purchase a credit pack."
*   **Credit Deduction Errors**:
    *   Credits are not accurately or atomically deducted after a successful report generation, leading to financial loss for SynapseIP.
    *   Credits are incorrectly deducted without report generation completing, requiring a robust credit rollback or refund mechanism.
*   **API Gateway (Reverse Proxy) Failure**: If the backend is deployed in a restricted region (e.g., Shanghai) and relies on a reverse proxy to access the Gemini API, failure of this proxy setup will block report generation entirely, regardless of available user credits.

---

## 3. User Interface (UI) Components

A beautiful, usable, and modern user interface is crucial for user adoption and retention. The authentication and credit management UI should be intuitive, responsive, and visually consistent with the SynapseIP brand.

### A. User Authentication UI

The authentication flow will leverage modern design principles for clarity and ease of use.

*   **Login Page (`/login`)**
    *   **Layout**: Centered, clean card-like layout with ample whitespace.
    *   **Branding**: Prominent `SynapseIP` logo or brand name at the top.
    *   **Headline**: A friendly "Welcome Back!" or "Log In to Your Account" message.
    *   **Input Fields**:
        *   "Email Address" and "Password" input fields.
        *   Modern, clear labels (e.g., floating labels) and subtle placeholder text.
        *   Visual feedback for valid/invalid input.
    *   **Action Buttons**:
        *   Primary "Log In" button: Clear, distinct, and visually inviting (e.g., a primary brand color with a slight hover effect).
        *   "Forgot Password?" link: Discreetly placed, leading to a password reset flow.
    *   **Social Login Options**:
        *   "Or continue with..." separator.
        *   Clean, recognizable buttons for "Log in with Google", "Log in with GitHub", etc., leveraging the `Clerk` or `NextAuth` UI components for consistency and ease of integration.
    *   **Registration Link**: "Don't have an account? Sign up" link, guiding new users.
*   **Sign Up Page (`/signup`)**
    *   **Layout**: Consistent with the login page for a cohesive user experience.
    *   **Branding**: `SynapseIP` logo/name.
    *   **Headline**: "Create Your SynapseIP Account" or "Get Started".
    *   **Input Fields**:
        *   "Email Address", "Password", and "Confirm Password" input fields.
        *   Password strength indicator (optional but recommended for modern apps).
    *   **Terms & Privacy**: A checkbox "I agree to the [Terms of Service](link) and [Privacy Policy](link)" with linked text.
    *   **Action Button**: A clear "Sign Up" button.
    *   **Social Sign-up Options**: Identical social login buttons as the login page.
    *   **Login Link**: "Already have an account? Log In" link.

### B. Credit System UI

A transparent and user-friendly credit management interface is crucial for monetization.

*   **Credit & Billing Dashboard (`/billing`)**
    *   **Layout**: A main content area with a left-hand navigation (e.g., "Overview", "Credit Packs", "Transaction History") for future expansion.
    *   **Current Credit Balance Card**:
        *   **Design**: A prominent, visually appealing card (e.g., with a subtle gradient, icon).
        *   **Title**: "Your Available Expansion Credits" or "Current Credits".
        *   **Value**: Display the current credit balance in a large, easy-to-read font (e.g., "500").
        *   **Context**: Below the value, add explanatory text like "1 Draft Page ≈ 2 Credits" (adjusting based on final pricing logic).
    *   **Credit Pack Purchase Section**:
        *   **Headline**: "Purchase More Credits"
        *   **Display**: Present credit packs as distinct, modern **cards** or a clear **comparison table**.
        *   **Card Structure (for each pack)**:
            *   **Tier Name**: e.g., "Starter Pack", "Pro Bundle", "Executive" (use distinct colors or icons for each).
            *   **Price**: Clearly visible, large font (e.g., "$19", "$49", "$99").
            *   **Benefits**: A concise bulleted list of what the user gets (e.g., "100 Draft Pages", "500 Draft Pages", "1,500 Draft Pages").
            *   **Call to Action**: A prominent "Buy Now" or "Purchase" button linked to Stripe Checkout.
            *   **Visual Enhancements**: Subtle animations on hover, clean borders, consistent spacing.
    *   **Transaction History (Table)**:
        *   **Optional (for MVP but highly recommended)**: A simple, sortable table showing past transactions.
        *   **Columns**: "Date", "Description" (e.g., "Purchased Pro Bundle", "Generated 100-page Report: 'Project Phoenix'"), "Credits Change" (+/- amount), "Remaining Credits".

*   **Report Generation Button Integration**
    *   **Dynamic Cost Display**: The main "Generate Report" button (e.g., on the `SynapseIP` dashboard or chat interface) should clearly show the credit cost: "Generate 100-Page Report (100 Credits)".
    *   **Insufficient Credits State**: If the user's `available_credits` are less than the `credit_cost`:
        *   The button text changes to: "Insufficient Credits".
        *   The button is visually disabled (e.g., grayed out) or a tooltip appears on hover.
        *   A prominent "Purchase Credits" link (or an actionable banner/modal) appears next to or above the button, navigating directly to the `/billing` page.

---

## 4. Antigravity Designer Prompt

```antigravity
"Architect, establish the complete commercialization infrastructure for the SynapseIP application. This must include robust user authentication, a comprehensive credit system with purchase and consumption logic, and integrated payment processing.

**Project Name:** SynapseIP (Backend: FastAPI, Frontend: React.js)
**Objective:** Enable user registration, secure login, credit purchases via Stripe, and credit-gated report generation.

**1. Backend Development (FastAPI with PostgreSQL/Supabase):**

*   **Database Models (SQLAlchemy/Pydantic):**
    *   **User Model:** Create/update `User` schema to include:
        *   `id`: Primary Key (UUID).
        *   `email`: String, Unique, Indexed, Non-nullable.
        *   `password_hash`: String, Non-nullable (for local authentication, use `argon2` or `bcrypt`).
        *   `available_credits`: Integer, Default 0, Non-nullable.
        *   `stripe_customer_id`: String, Nullable (for Stripe customer management).
        *   `created_at`, `updated_at`: Timestamps.
    *   **CreditTransaction Model:** Create a model to log all credit movements:
        *   `id`: Primary Key (UUID).
        *   `user_id`: Foreign Key to `User.id`.
        *   `type`: Enum (e.g., 'purchase', 'deduction', 'refund').
        *   `amount`: Integer (credits added/deducted), Non-nullable.
        *   `description`: String (e.g., 'Executive Credit Pack purchased', '100-page report generation for Project X').
        *   `timestamp`: Datetime, Non-nullable.
        *   `reference_id`: String, Nullable (e.g., Stripe charge ID, report ID).

*   **User Authentication Endpoints:**
    *   Implement `/auth/register` (POST) for new user sign-up.
    *   Implement `/auth/login` (POST) for user login, returning JWT tokens for session management.
    *   Implement `/auth/me` (GET, protected) to retrieve authenticated user details and credit balance.
    *   Integrate `Clerk` or `NextAuth.js` (for React) for secure OAuth (Google, GitHub) functionality. Ensure appropriate backend validation for tokens.

*   **Credit System Endpoints:**
    *   **Stripe Integration:**
        *   Create a `/stripe/checkout` (POST, protected) endpoint. This endpoint will create a Stripe Checkout Session for a selected Credit Pack and return the session URL to the frontend.
        *   Create a dedicated `/stripe-webhook` (POST, public) endpoint to securely receive events from Stripe (e.g., `checkout.session.completed`).
        *   Upon receiving a valid `checkout.session.completed` event:
            *   Verify the signature to ensure authenticity.
            *   Identify the user based on metadata in the session.
            *   Atomically update the user's `available_credits` in the `User` model.
            *   Log the transaction in the `CreditTransaction` model (type: 'purchase').
    *   Create a protected GET endpoint `/user/transactions` to retrieve the authenticated user's credit history.

*   **Report Generation Logic (Credit Gating):**
    *   Modify the `/generate-report` (POST, protected) endpoint:
        *   **Authentication Check**: Ensure the request is from an authenticated user.
        *   **Credit Cost Calculation**: Dynamically calculate the `credit_cost` for the requested report (e.g., define cost in a config or based on estimated output length). For a 100-page plan, assume a placeholder of `100` credits initially.
        *   **Credit Balance Check**: Query the database to compare `user.available_credits` with `credit_cost`.
        *   **Denial Logic**: If `user.available_credits` < `credit_cost`, immediately return a `403 Forbidden` JSON response: `{"detail": "Insufficient credits. Please purchase a credit pack to generate this report."}`.
        *   **Deduction & Generation**: If credits are sufficient:
            *   Atomically deduct `credit_cost` from `user.available_credits`.
            *   Log a `CreditTransaction` (type: 'deduction', description: "Report Generation: [Report Title]").
            *   Proceed with the iterative Gemini API calls for report generation.
            *   Implement a robust rollback mechanism: if report generation fails after deduction but before completion, refund credits to the user or mark the transaction for manual review.

*   **API Hosting & Region-Specific Proxy (Shanghai Context):**
    *   Ensure the FastAPI backend is designed for deployment on cloud platforms (e.g., Vercel, Render, Railway, Google Cloud Run) with proper environment variable handling.
    *   Crucially, design the Gemini API integration to utilize a **reverse proxy pattern**. The FastAPI backend should be configurable to route Gemini API calls through a custom `base_url` (e.g., `Laozhang.ai` or a self-hosted relay in Singapore/Tokyo) to ensure stability and accessibility for users in restricted regions (like Shanghai) without requiring them to use a VPN for app functionality after initial Gemini brainstorming.

**2. Frontend Development (React.js):**

*   **Authentication Pages & Components:**
    *   Develop high-fidelity, modern UI components for `/signup` and `/login` pages.
    *   **Visuals**: Use `SynapseIP` branding, clear typography, and a minimalist aesthetic.
    *   **Functionality**: Implement email/password forms, "Forgot Password" links, and integrate `Clerk` or `NextAuth.js` components for Google/GitHub sign-in/up.
    *   **State Management**: Implement client-side routing, display user authentication status, and redirect users based on login state.
    *   **Error Handling**: Display clear, user-friendly error messages for failed logins/registrations.

*   **Credit & Billing Dashboard (`/billing` page):**
    *   **Design Goal**: Create an intuitive and visually engaging page for credit management.
    *   **Current Balance Display**:
        *   Display `user.available_credits` prominently in a styled "Credit Balance" card.
        *   Include a concise explanation of credit value (e.g., "Approximately 100 Draft Pages").
    *   **Credit Pack Purchase Options:**
        *   Present `Credit Packs` as visually distinct, modern **cards** (Starter, Pro, Executive).
        *   Each card should include:
            *   **Tier Name** (e.g., "Starter Pack").
            *   **Price** (e.g., "$19").
            *   **Benefits** (e.g., "100 Draft Pages", "Covers one 100-page report").
            *   **Call to Action**: A vibrant "Buy Now" button that triggers the Stripe Checkout process.
        *   Ensure consistent styling, hover effects, and clear differentiation between tiers.
    *   **Transaction History:** Display a recent `CreditTransaction` history in a clean, scrollable table.

*   **Report Generation UI Integration:**
    *   **Dynamic Cost Display**: Update the primary "Generate Report" button in the app to dynamically display the estimated `credit_cost` (e.g., "Generate Report (100 Credits)").
    *   **Insufficient Credits State**: If the user's `available_credits` are insufficient for the requested report:
        *   Change the button text to "Insufficient Credits".
        *   Disable the button visually (e.g., gray it out).
        *   Display a prominent, actionable "Purchase Credits" link nearby, directly navigating the user to the `/billing` page.
    *   **Feedback**: Implement loading indicators, success messages, and error alerts after report generation attempts.

**3. Quality Assurance & Testing:**

*   **Unit Tests**: Write comprehensive unit tests for all authentication endpoints, credit purchase logic, credit deduction, and transaction logging.
*   **Integration Tests**: Test the full user flow from registration, login, credit purchase (Stripe webhook), to successful credit deduction for report generation.
*   **UI/UX Testing**: Verify the responsiveness, accessibility, and visual consistency of all authentication and billing UI components across major browsers and devices.

Begin by setting up the FastAPI backend with the `User` and `CreditTransaction` models, then integrate the core `Clerk`/`NextAuth.js` and `Stripe` webhook logic. Once the backend foundations are stable and payment processing is verified, proceed with building the React frontend UI components for authentication and credit management."

---

---

## 8. Advanced Document Generation: Iterative Expansion & Output Formatting

# 8. Advanced Document Generation: Iterative Expansion & Output Formatting

## 1. Feature Overview & Core Logic

This feature enables SynapseIP to generate extensive, professionally formatted documents (e.g., 100+ page business plans, whitepapers) from user-provided Gemini chat discussions. It overcomes length and formatting restrictions found in tools like NotebookLM by employing an iterative, agentic approach.

*   **Why this feature is needed:** Users require the ability to transform raw brainstorming notes into polished, long-form reports without manual compilation or re-formatting. This feature automates the expansion, structuring, and styling of content to meet professional standards.
*   **Calculation/Logic:**
    *   **Iterative Expansion Loop:** The generation process is broken down into smaller, manageable steps to prevent AI drift, timeouts, and maintain contextual coherence over many pages.
        *   An initial "Outline Agent" creates a multi-chapter skeleton.
        *   "Drafting Agents" then expand each chapter sequentially, referencing the outline and previous chapters to maintain flow.
        *   "Auditing Agents" perform quality checks against a defined "Formatting Manifest" and factual accuracy.
    *   **Credit Consumption:** Document generation costs are calculated based on the output length (e.g., words, pages). This consumption is tied to a user's "Available Credits."
    *   **Output Formatting:** Raw Markdown generated by the AI is strictly controlled by a "Formatting Manifest" and then rendered into a professional `.docx` or `.pdf` file using pre-defined CSS styling.
    *   **Large File Handling:** For outputs exceeding platform payload limits (e.g., Vercel's 4.5MB), documents are saved to cloud storage (e.g., Vercel Blob), and a secure download link is provided to the user.

---

## 2. Expected Outcomes

### If it works:

*   **Successful Generation:** A "Generate Report" button (or similar UI trigger) initiates a background process.
*   **User Feedback:** A clear progress indicator or status updates are displayed (e.g., "Generating Chapter 5 of 20...").
*   **Professional Output:** Upon completion, the user receives a download link to a comprehensive, multi-page (100+ pages) document.
*   **Consistent Formatting:** The downloaded document adheres strictly to predefined layout rules (consistent headers, lists, tables, font styles).
*   **Credit Deduction:** The user's "Available Credits" are accurately reduced based on the generated report's length/complexity.
*   **Pre-Flight Assessment:** Before generation, the system provides a viability score (0-100) and specific, actionable feedback if the input notes are insufficient, guiding the user to improve their source material.

### If it fails:

*   **Generation Error:** The generation process halts, and an error message is displayed (e.g., "Generation failed: Insufficient credits," "API Timeout," "Formatting Error in Chapter 7").
*   **Inconsistent Output:** The generated document exhibits "AI drift" in formatting (e.g., varying header styles, unformatted text blocks, contradictions).
*   **No Download:** If payload limits are hit without proper handling, the user receives an error instead of a download link, or the file is corrupted.
*   **Incorrect Credit:** Credits are either not deducted or deducted incorrectly, leading to revenue loss or user frustration.
*   **Poor Assessment:** The Pre-Flight Assessment provides generic, unhelpful feedback, or an inaccurate viability score.

---

## 3. UI Components and User Interaction

The user will primarily interact with this feature through a dedicated web dashboard (React frontend).

### UI Components

*   **Dashboard Navigation:**
    *   A prominent section or tab named "Reports" or "Documents."
*   **Report Generation Interface:**
    *   **"Generate New Report" Button:** A clear, distinct button to initiate the document generation process.
        *   *Design:* Modern, primary action button (e.g., `background-color: #4CAF50; color: white; border-radius: 8px; padding: 12px 24px; font-weight: bold; cursor: pointer;`).
    *   **Source Selection:** A component allowing users to select which "Project Buckets" (collections of Gemini chats) or specific chats should be used as source material for the report.
        *   *Design:* A multi-select dropdown or a list with checkboxes, visually distinct and easy to manage large numbers of sources. Each source might have a small icon (e.g., Gemini logo, document icon).
    *   **Report Type Selector (Optional but Recommended):** A dropdown or radio buttons to choose the desired output type (e.g., "Business Plan," "Whitepaper," "Technical Manual"). This could influence the AI's prompt chain.
        *   *Design:* Clean, intuitive selection widget, potentially with tooltips explaining each report type.
    *   **Estimated Cost Display:** Below the "Generate" button, clearly show the estimated credit cost for the selected report length/complexity before generation.
        *   *Design:* Small text label: "Estimated Cost: X Credits" (e.g., `font-size: 0.9em; color: #555;`).
    *   **User Credit Balance Display:** A persistent display of the user's current available credits.
        *   *Design:* Located in the user's profile dropdown or a dedicated section of the dashboard, clearly visible (e.g., "Credits: 450"). This should link to a "Buy Credits" page.
*   **Pre-Flight Assessment Display:**
    *   **Score Card:** A prominent visual card displaying the "Idea Health Score" (0-100).
        *   *Design:* A circular progress bar or a gradient-filled bar, clearly indicating the score with a corresponding color (e.g., Red for <50, Yellow for 50-80, Green for >80).
    *   **Feedback Section:** Below the score, a clear, bulleted list of 2-3 specific, actionable recommendations for improving the source material if the score is low. If the score is high, a "Ready to Generate!" message.
        *   *Design:* Use distinct styling for "Warnings" (e.g., yellow background, warning icon) and "Success" (e.g., green background, checkmark icon).
*   **Generation Progress & Status:**
    *   **Progress Bar:** A visual progress bar with text updates (e.g., "Processing Data...", "Generating Chapter 3...", "Finalizing Document...").
        *   *Design:* Modern, animated progress bar that updates dynamically.
    *   **Status Messages:** Real-time messages indicating the current stage of the generation or any alerts.
*   **Generated Reports List:**
    *   A list or table displaying previously generated reports, including their title, date, and current status (e.g., "Completed," "Processing," "Failed").
    *   **"Download Report" Button:** For completed reports, a button to initiate the download of the final `.docx` or `.pdf` file.
        *   *Design:* Clear download icon or text.

### User Flow

1.  User navigates to the "Reports" section of the SynapseIP dashboard.
2.  User selects relevant Gemini chats/Project Buckets as source material.
3.  The "Pre-Flight Assessment" automatically runs and displays a viability score and feedback.
4.  If the score is low, the UI guides the user on how to refine their notes.
5.  If the score is sufficient, the "Generate Report" button becomes active, showing the estimated credit cost.
6.  User clicks "Generate Report." The UI displays a progress bar and status messages.
7.  Once complete, a notification appears, and the report is added to the "Generated Reports List" with a "Download" button.
8.  Clicking "Download" fetches the document from Vercel Blob (or similar storage) via a secure link.

### UI Component Prompt for Antigravity (Designer)

"Antigravity, design a modern, clean, and intuitive web dashboard component in React for SynapseIP's 'Advanced Document Generation' feature. Focus on a minimalist aesthetic with clear calls to action.

*   **Main Section:** A prominent 'Generate New Report' area.
    *   Include a multi-select dropdown for 'Select Source Notes' (referencing available 'Project Buckets' or individual 'Gemini Chats').
    *   Add an interactive section for 'Report Type' (e.g., 'Business Plan', 'Whitepaper', 'Technical Manual') using radio buttons or a segmented control.
    *   Display 'Estimated Credit Cost: X Credits' dynamically below the input, updating based on selected options.
    *   Feature a large, primary 'Generate Report' button.
        *   *Styling:* `#4CAF50` background, white text, 8px border-radius, bold font.
*   **Pre-Flight Assessment Card:** A visually distinct card that appears immediately after source selection.
    *   Show a circular progress bar or an expressive badge for 'Idea Health Score (0-100)'.
        *   *Styling:* Green for >80, Yellow for 50-80, Red for <50.
    *   Below the score, present a dynamic 'Feedback' section. If score is low, list 3 actionable bullet points. If high, display a 'Ready to Generate!' message.
        *   *Styling:* Use subtle warning/success icons and background colors for feedback.
*   **Generation Status Area:** A collapsible or dedicated panel for real-time progress.
    *   Include an animated progress bar.
    *   Display clear text updates (e.g., 'Generating Outline...', 'Expanding Chapter 5...', 'Finalizing PDF...').
*   **Generated Reports List:** A clean, scrollable table listing past reports.
    *   Columns: 'Report Title', 'Date Generated', 'Status', 'Actions'.
    *   Under 'Actions', include a clear 'Download' button for completed reports.
        *   *Styling:* Download icon for easy recognition.
*   **Global Header/Footer:** Ensure the user's 'Available Credits' are clearly visible in the application's persistent header or a dedicated sidebar section, linking to a 'Buy Credits' page.
*   **Overall Styling:** Use a modern UI library (e.g., Material UI, Ant Design, or Tailwind CSS) for consistency. Ensure responsiveness for desktop and tablet views. Adhere to a light theme with accents of `#1a73e8` for primary text and interactive elements, and subtle `#e0e0e0` for borders/separators."

---

## 4. Step-by-Step Logic Guide to Build

### A. Backend Development (FastAPI, Python)

#### Phase 1: Establish Core Data Model & API Endpoints

This phase ensures the backend can store user data and notes, and manage the credit system.

*   **Why Needed:** To manage user accounts, store imported Gemini chats (`Gemini Sources`), track user credit balances, and serve as the central hub for document generation. This is the "Librarian" of the app.
*   **Steps:**
    1.  **Initialize FastAPI Project:** Set up the basic project structure and ensure local execution.
    2.  **Define Database Schema (SQLAlchemy + SQLite):** Create models for `User` and `GeminiSource`.
    3.  **Implement `User` Model with Credits:**
        *   Include fields for `id`, `email`, `hashed_password`, and `available_credits` (integer type).
    4.  **Implement `GeminiSource` Model:**
        *   Include fields for `id`, `user_id` (foreign key), `title`, `content` (long text), `timestamp`, and `source_url`.
    5.  **Create `/ingest` Endpoint:** A `POST` endpoint to receive Gemini chat data from the Chrome Extension and save it to `GeminiSource` table. Ensure CORS is enabled.
    6.  **Create `/user/credits` Endpoint:** A `GET` endpoint to display a user's `available_credits`.
    7.  **Create `/status` Endpoint:** A `GET` endpoint for basic database health, e.g., showing count of `GeminiSource` entries.

*   **What to expect:**
    *   **Works:** FastAPI server starts on `http://localhost:8000`. Database tables (`users`, `gemini_sources`) are created. Data can be successfully ingested via `/ingest`, and user credits can be viewed.
    *   **Fails:** Server fails to start, database connection errors, or data not saving correctly.

*   **Antigravity Prompt:**
    ```
    "Initialize a Python FastAPI project. I need a backend that runs locally on port 8000.
    1. Create a SQLite database using SQLAlchemy to store 'User' and 'Gemini Sources'.
    2. The 'User' schema should include: `id`, `email`, `hashed_password`, and `available_credits` (integer, default to 0).
    3. The 'GeminiSource' schema should include: `id`, `user_id` (foreign key to User), `title`, `content` (long text), `timestamp`, and `source_url`.
    4. Create a POST endpoint at `/ingest` that accepts JSON with 'title', 'content', 'source_url' and `user_id`, saving it to the `GeminiSource` DB.
    5. Create a GET endpoint at `/user/{user_id}/credits` that returns the `available_credits` for that user.
    6. Ensure CORS is enabled for all origins to allow interaction from a Chrome Extension.
    7. Provide a simple 'Status' page at the root `/` that shows the number of registered users and `GeminiSource` entries."
    ```

---

#### Phase 2: Implement Iterative Document Generation Logic

This phase builds the core intelligence for generating long-form reports.

*   **Why Needed:** To produce high-quality, multi-page reports by systematically outlining, drafting, and verifying content, avoiding the "memory wall" of large language models and ensuring consistent output.
*   **Steps:**
    1.  **Integrate Gemini 1.5 Pro API:** Set up the client to interact with the Gemini API, ensuring API keys are securely managed (e.g., `.env` file).
    2.  **LLM Abstraction Layer:** Create a `ChatService` interface and a `GeminiProvider` implementation. This allows easy swapping of LLMs later.
    3.  **Implement "Pre-Flight Assessment" Endpoint (`/assess-idea`):**
        *   This `POST` endpoint accepts a `user_id` and selected `GeminiSource` IDs.
        *   It fetches the combined notes and uses Gemini 1.5 Pro to evaluate them against the "SynapseIP Idea Validator Rubric."
        *   Returns an "Idea Health Score" (0-100) and actionable feedback.
    4.  **Implement Iterative Generation Endpoint (`/generate-report`):**
        *   This `POST` endpoint accepts `user_id`, `selected_source_ids`, and `report_type`.
        *   **Credit Check:** It first verifies if the user has sufficient `available_credits` for the estimated report length.
        *   **Background Task:** Initiates a background task (e.g., using Celery, or a simple async process for MVP) that:
            *   **Outline Generation:** Uses Gemini to create a 20-chapter outline based on aggregated notes, adhering to the "GrandDraft Formatting Manifest" (Chapter Titles `##`).
            *   **Chapter-by-Chapter Expansion:** Loops through each outline chapter. For each chapter:
                *   Retrieves relevant source notes (using RAG if a vector database is integrated, or simple keyword search).
                *   Prompts Gemini to expand the chapter into 4-5 pages of content, strictly following the "GrandDraft Formatting Manifest" (Section Headers `###`, Sub-points `####`, Tables, Blockquotes, Lists, no "AI talk").
                *   Saves the generated Markdown content for the chapter.
                *   (Optional MVP++) **Consistency Check:** Uses a separate agent to verify the new chapter doesn't contradict previous chapters.
        *   **Credit Deduction:** After successful generation of a chapter/section, deducts appropriate credits from the user.
        *   **Report Compilation:** Once all chapters are generated, uses a library like `python-docx` or `reportlab` to stitch all Markdown sections into a single, professionally formatted `.docx` or `.pdf` document.
    5.  **Implement Large File Handling (Vercel Blob / Cloud Storage):**
        *   The generated large document is saved to Vercel Blob (or AWS S3/GCS).
        *   The `/generate-report` endpoint returns a `task_id` immediately and later updates the user with a secure, time-limited download URL for the final document once the background task completes.
    6.  **Proxy Logic (Shanghai-Proofing):** Implement a reverse proxy logic within the FastAPI app. Your backend will make the actual calls to the Gemini API, abstracting the direct connection from the user's location.

*   **What to expect:**
    *   **Works:**
        *   `/assess-idea` returns a score and tailored feedback based on the input quality.
        *   `/generate-report` initiates quickly and returns a `task_id`.
        *   The background process runs without errors, incrementally generating chapters.
        *   Final document is a high-quality, long-form report with consistent formatting, accessible via a download link.
        *   User credits are accurately debited.
    *   **Fails:**
        *   `/assess-idea` gives generic or incorrect scores.
        *   `/generate-report` times out or fails silently without a `task_id`.
        *   AI drift leads to inconsistent or low-quality content/formatting within the report.
        *   Large file errors occur during download if not routed through cloud storage.
        *   Credit check or deduction logic errors.
        *   Connection issues to Gemini API if proxy logic is flawed (especially from Shanghai).

*   **Antigravity Prompt:**
    ```
    "Enhance the existing FastAPI backend to implement iterative document generation, output formatting, and pre-flight assessment.

    1.  **Integrate LLM Abstraction Layer:** Create a Python `ChatService` interface with a `generate_content` method. Implement a `GeminiProvider` class that uses `google.generativeai.GenerativeModel` and implements this interface. All LLM calls from the application should use this abstraction.
    2.  **Implement Pre-Flight Assessment:**
        *   Create a `POST /assess-idea` endpoint.
        *   It accepts a list of `gemini_source_ids` and a `user_id`.
        *   It fetches and combines the `content` from selected `GeminiSource` entries.
        *   It uses the `GeminiProvider` to analyze the combined content against the provided "SynapseIP Idea Validator Rubric" (Data Richness, Logic & Flow, Actionability, Target Clarity, weighted 30%, 30%, 20%, 20% respectively for a 0-100 score).
        *   Returns a JSON object with `score` (integer) and `feedback` (string: "Ready to Generate" or specific, actionable questions for improvement if score < 80).
        *   *Rubric Definition to Inject:*
            "SynapseIP Idea Validator Rubric:
            - Data Richness (30%): Specific goals, timelines, budget, market research? (15 = critical details, 0 = broad aspirations)
            - Logic & Flow (30%): Logical progression of ideas, or random thoughts? (15 = structured, 0 = scattered)
            - Actionability (20%): Concrete next steps or decisions made? (10 = clear actions, 0 = vague concepts)
            - Target Clarity (20%): Clearly defined audience, product, service? (10 = precise, 0 = undefined)"
    3.  **Develop Iterative Report Generation Endpoint:**
        *   Create a `POST /generate-report` endpoint. It accepts `user_id`, `selected_source_ids`, and `report_type` (e.g., "Business Plan").
        *   **Credit Check:** Before starting, verify `user.available_credits` against estimated cost. If insufficient, return a 402 Payment Required error.
        *   **Background Task Setup:** Use `python-rq` (Redis Queue) or similar for background task management. This endpoint should immediately return a `task_id` and start the heavy generation in the background.
        *   **Iterative Loop:**
            *   **Step 1: Outline Generation:** Call the `GeminiProvider` to generate a 20-chapter outline from the combined notes, strictly following the "GrandDraft Formatting Manifest" for Chapter Titles (`##`).
            *   **Step 2: Chapter-by-Chapter Expansion:** Iterate through the generated outline. For each chapter:
                *   Retrieve contextually relevant notes (basic RAG based on chapter title and source content).
                *   Call `GeminiProvider` to expand the chapter into 4-5 pages of detailed content, incorporating the "GrandDraft Formatting Manifest" (Section Headers `###`, Sub-points `####`, Mandatory Tables, Blockquotes for Summaries/Key Takeaways, Bulleted/Numbered Lists, LaTeX for math, NO "AI Talk").
                *   Save each chapter's Markdown output temporarily.
                *   Deduct credits based on the generated content for the chapter.
                *   (Optional but Recommended) Implement a self-correction loop where an internal agent reviews the chapter for formatting/coherence before proceeding.
        *   **Report Compilation:** Once all chapters are drafted, stitch them into a single document using `python-docx` or `reportlab` for PDF generation.
        *   **Cloud Storage & Download Link:** Save the final document (e.g., `report.docx` or `report.pdf`) to Vercel Blob (or similar cloud storage). Store the Blob URL and `task_id` in the database.
        *   **Status Polling:** Implement a `GET /report/status/{task_id}` endpoint for the frontend to query the progress of the background generation task and retrieve the final download URL.
    4.  **Implement Reverse Proxy Logic for Gemini API Calls:**
        *   Modify `GeminiProvider` to route all outbound Gemini API requests through a proxy mechanism within the FastAPI application.
        *   Configure the proxy to use an overseas endpoint (e.g., Vercel's hosting region in Singapore/Tokyo).
        *   Include a "Timeout and Retry" decorator for robustness against network instability.
    5.  **Add Credit Management Endpoints:**
        *   Create a `POST /purchase-credits` endpoint (stub for Stripe integration in a later step) that updates `user.available_credits`.
    6.  **Create README:** Provide a clear `README.md` on how to set up `google.generativeai` API keys (via `.env`), run the FastAPI server, and configure `python-rq` (if used). Ensure API keys are NOT hardcoded.
    ```

---

### B. Frontend Development (React)

#### Phase 3: Build Generation UI and Output Display

This phase creates the user-facing interface for interacting with the document generation feature.

*   **Why Needed:** To provide a clear, intuitive way for users to initiate report generation, monitor progress, view pre-flight assessments, manage credits, and download their final documents.
*   **Steps:**
    1.  **Integrate Authentication:** Implement user login/signup using a service like Clerk or NextAuth.js. This connects to the `User` model in the backend.
    2.  **Display User Credits:** Fetch and display the `user.available_credits` on the dashboard.
    3.  **Build "Generate Report" Component:**
        *   Create a form that allows selecting multiple `GeminiSource` items (e.g., checkboxes next to each source in a list).
        *   Include a dropdown for `report_type`.
        *   Dynamically display the "Estimated Credit Cost" fetched from the backend's assessment logic.
        *   Implement the "Generate Report" button, which triggers the `POST /generate-report` endpoint.
    4.  **Implement "Pre-Flight Assessment" UI:**
        *   When sources are selected, call the `POST /assess-idea` endpoint.
        *   Display the returned `score` visually (e.g., a progress circle or a colored badge).
        *   Render the `feedback` messages dynamically, using distinct visual styles for "Ready to Generate" vs. "Requires more detail."
    5.  **Implement Report Status & Progress:**
        *   After hitting "Generate Report," transition the UI to show a progress area.
        *   Use polling (`GET /report/status/{task_id}`) to update the user with real-time status messages and progress bar updates.
    6.  **Display Generated Reports:**
        *   Create a table or list component to show generated reports (title, date).
        *   For reports with `status: "completed"`, display a "Download" button.
        *   Clicking "Download" should use the provided secure URL to fetch the document.
    7.  **Apply "GrandDraft Formatting Manifest" CSS:**
        *   Create a global CSS file or a `ChatResponse.css` component file.
        *   Define styles for:
            *   `h1` (Document Title - used once at report start).
            *   `h2` (Chapter Titles - preceded by horizontal rule `---` for page break).
            *   `h3` (Section Headers).
            *   `h4` (Sub-points).
            *   `hr` (horizontal rules - rendered as full-width separators, triggering page breaks in print view).
            *   `ul`, `ol` (bulleted/numbered lists).
            *   `table` (Markdown tables with clear borders and professional spacing).
            *   `blockquote` (indented for summaries/key takeaways).
            *   `strong` (for emphasis, but NOT for headers).
            *   `pre`, `code` (for code blocks if applicable).
        *   Include `@media print` rules for optimal PDF output (e.g., `page-break-before: always` for `h2`, `page-break-inside: avoid` for tables).

*   **What to expect:**
    *   **Works:** Users can log in, select notes, get a viability score, generate a report, see live progress, and download a perfectly formatted document. Credit balance updates visibly.
    *   **Fails:** UI is unresponsive, API calls fail to trigger updates, formatting appears inconsistent on screen or in downloads, credit display is incorrect.

---

### C. Chrome Extension Enhancement (Existing `content.js` and `background.js`)

#### Phase 4: Universal Sync with Backend Proxy

This phase ensures the Chrome Extension can reliably send data to the backend, especially from restricted regions like Shanghai, and supports multiple AI platforms.

*   **Why Needed:** To seamlessly transfer Gemini chat data (or other AI chat data) to SynapseIP without manual copy-pasting, while circumventing "Mixed Content" security issues and regional network restrictions.
*   **Steps:**
    1.  **Refine Content Script (`content.js`):**
        *   Enhance the script to inject a "Sync to SynapseIP" button next to *each* AI response bubble (not just the latest).
        *   The button, when clicked, should extract the Markdown content of its associated response.
        *   Update `manifest.json` to include permissions for `https://gemini.google.com/*`, `https://chatgpt.com/*`, `https://claude.ai/*`, `https://doubao.com/*` for universal scraping.
    2.  **Implement Selector Abstraction:**
        *   Instead of hardcoded CSS selectors in `content.js`, create a `selectors.json` file on the backend.
        *   Modify `content.js` to fetch this `selectors.json` from the backend API on extension startup.
        *   Implement a `getChatData()` function that uses the current URL to lookup the correct selector from the fetched JSON.
        *   Include a fallback mechanism: if a selector fails, the function attempts a generic search for large text blocks or prompts the user to "Report Layout Change" which sends page HTML to the backend for analysis.
    3.  **Utilize Service Worker (`background.js`) for Proxying:**
        *   The `content.js` script sends the scraped chat data to the `background.js` (Service Worker).
        *   The `background.js` handles the actual `fetch` request to the *SynapseIP backend API's `/ingest` endpoint* (e.g., `https://your-api.com/ingest`).
        *   This bypasses "Mixed Content" security blocks by sending data from the secure Gemini page to the backend's publicly accessible HTTPS endpoint, which then acts as the reverse proxy to the Gemini API.
    4.  **User Authentication Flow for Extension:**
        *   When the "Sync" button is clicked for the first time or if the user is not logged in, trigger an OAuth flow that opens the SynapseIP web dashboard for login/account creation.
        *   The extension should then store a secure token (e.g., JWT) to authenticate future sync requests with the backend.

*   **What to expect:**
    *   **Works:** A "Sync to SynapseIP" button appears next to AI responses on configured chat platforms. Clicking it successfully sends the chat content to the SynapseIP backend, where it is stored. The process works from restricted regions due to the reverse proxy and Service Worker.
    *   **Fails:** Buttons do not appear, clicking buttons yields console errors (e.g., CORS, Mixed Content), data does not reach the backend, or authentication fails. UI changes on chat platforms break the scraper logic, requiring manual `selectors.json` updates or automated fallback.

---

## 5. Antigravity Build Prompt for 'Advanced Document Generation'

```
"Antigravity, let's refine SynapseIP's 'Advanced Document Generation' feature, focusing on robust iterative expansion, professional output formatting, and an intuitive user interface. Assume the basic FastAPI backend for data ingestion (POST /ingest) and a User model with 'available_credits' already exist.

**Project Name:** SynapseIP
**Current App State:** FastAPI backend with database for `User` and `GeminiSource`, React frontend for basic display. Chrome Extension for Gemini data ingestion.

**Goal:** Build a feature for iterative generation of 100+ page documents with consistent formatting, pre-flight assessment, and large file handling.

**Instructions for Antigravity Agent:**

1.  **Backend Enhancements (FastAPI - Python):**
    *   **LLM Abstraction Layer:** Create a `ChatService` interface (abstract base class) and a `GeminiProvider` concrete implementation using `google.generativeai.GenerativeModel`. Ensure all new LLM interactions use this interface.
    *   **Pre-Flight Assessment Endpoint:**
        *   Implement a `POST /assess-idea` endpoint that accepts `user_id` and a list of `gemini_source_ids`.
        *   Aggregate content from selected `GeminiSource` entries.
        *   Use the `GeminiProvider` to score the aggregated content (0-100) based on the "SynapseIP Idea Validator Rubric" provided below.
        *   Return the score and a contextual `feedback` message (e.g., "Ready to Generate!" or specific improvement questions).
        *   *SynapseIP Idea Validator Rubric:*
            - Data Richness (30%): Score based on presence of specific goals, timelines, budget, market research.
            - Logic & Flow (30%): Score based on logical progression and structure of ideas.
            - Actionability (20%): Score based on concrete next steps or decisions.
            - Target Clarity (20%): Score based on clearly defined audience, product, or service.
    *   **Iterative Report Generation Endpoint:**
        *   Implement a `POST /generate-report` endpoint that accepts `user_id`, `selected_source_ids`, and `report_type` (e.g., "Business Plan").
        *   **Credit Check:** Before any LLM calls, check if `user.available_credits` meets the `estimated_cost` (calculate as 1 credit per ~1000 words * 3x markup). If insufficient, return a `402 Payment Required` with a message.
        *   **Background Task Integration:** Use `python-rq` (Redis Queue) to process document generation in the background. The endpoint should immediately return a `task_id`.
        *   **Implement Iterative Generation Logic:**
            1.  **Outline Creation:** Use the `GeminiProvider` to generate a 20-chapter outline from aggregated sources, strictly following the "GrandDraft Formatting Manifest" for `## Chapter Titles`.
            2.  **Chapter Expansion Loop:** For each chapter in the outline:
                *   Retrieve relevant content from `GeminiSource` based on chapter context (simple keyword match for MVP).
                *   Call the `GeminiProvider` to expand this content into ~4-5 pages of professional text, strictly adhering to the "GrandDraft Formatting Manifest" for `### Section Headers`, `#### Sub-points`, tables, blockquotes, lists, and language tone.
                *   Save the generated Markdown for each chapter temporarily.
                *   Deduct credits incrementally after each successful chapter generation.
            3.  **Document Compilation:** Use `python-docx` or `reportlab` (preference for `.docx` output) to stitch all generated Markdown chapters into a single, cohesive document.
        *   **Large File Handling (Vercel Blob):** Save the final `.docx` or `.pdf` document to Vercel Blob storage.
        *   The background task should update the database with the `task_id` and the final Vercel Blob download URL.
    *   **Report Status Endpoint:** Implement a `GET /report/status/{task_id}` endpoint that returns the current progress (e.g., 'Outline Generated', 'Chapter 5/20 Completed', 'Finalizing'), and the `download_url` if complete.
    *   **Proxy Endpoint (Shanghai Compatibility):** Ensure all calls from `GeminiProvider` to the external Gemini API are routed through a reverse proxy mechanism within this FastAPI application, effectively making *your* server the middleman. Implement basic retry logic for external API calls.
    *   **Stripe Integration (MVP):** Implement a placeholder `POST /webhook/stripe` endpoint. The logic should parse incoming Stripe webhook events (e.g., `checkout.session.completed`) and update the `user.available_credits` accordingly based on purchased credit packs. (Example: $15 for 500 "Expansion Credits").
    *   **Dependencies:** Update `requirements.txt` with necessary libraries (e.g., `python-docx`, `reportlab`, `python-rq`, `google-generativeai`, `SQLAlchemy`, `FastAPI`, `Uvicorn`).

2.  **Frontend Implementation (React - Web Dashboard):**
    *   **Navigation:** Create a clear navigation link/tab for 'Reports'.
    *   **Credit Display:** Display the `user.available_credits` prominently (e.g., in the header) with a link to a 'Buy Credits' page.
    *   **Generate Report Form:**
        *   Develop a React component for selecting multiple `GeminiSource` items (checkbox list).
        *   Implement dynamic display of 'Estimated Credit Cost' based on selected sources and `report_type`.
        *   Create the 'Generate Report' button. On click, disable the button, show loading state, and initiate API call to `POST /generate-report`.
    *   **Pre-Flight Assessment UI:**
        *   Upon selecting source notes, call `POST /assess-idea`.
        *   Display the returned `score` using a visually appealing circular progress bar.
        *   Render `feedback` messages below the score, using distinct green for "Ready" and red/yellow for "Requires Improvement" messages.
    *   **Real-time Progress & Status:**
        *   After triggering report generation, display a dedicated UI element with a progress bar and text updates (e.g., "Generating Outline...").
        *   Periodically poll the `GET /report/status/{task_id}` endpoint to update the progress bar and status messages.
    *   **Generated Reports List:**
        *   A table/list component displaying all reports generated by the user (Title, Date, Status, Download Link).
        *   The 'Download Link' should become active and clickable once the report status is 'completed'.
    *   **Formatting Manifest (CSS):**
        *   Create a `report.css` file.
        *   Define comprehensive styles for rendering Markdown elements generated by the AI:
            *   `#`: For document title (large, centered).
            *   `##`: For chapter titles (bold, specific color, large margin-top, `border-bottom`). Ensure `@media print` rule for `page-break-before: always;`.
            *   `###`: For section headers (bold, slightly smaller).
            *   `####`: For sub-points.
            *   `---`: For horizontal rules (styled as clear separators, `@media print` rule for `page-break-before: always;`).
            *   `*` / `1.`: For bulleted/numbered lists (consistent indentation).
            *   Markdown `table` syntax: Styled with clear borders, padding, and `page-break-inside: avoid;` in print media.
            *   `> `: For blockquotes (distinct background/border).
            *   `**text**`: For bold text (NOT for headers).
            *   LaTeX rendering if a library is used (e.g., `react-latex`).
        *   Integrate a Markdown rendering library (e.g., `react-markdown`) to parse AI output and apply `report.css`.
    *   **User Feedback & Notifications:** Implement toast notifications or alerts for success messages (e.g., "Report generation started!") and error messages.

3.  **Chrome Extension Updates (JavaScript):**
    *   **Dynamic Selector Loading:** Modify `content.js` to fetch a `selectors.json` from the FastAPI backend at startup. Update `getChatData()` to use this dynamic mapping.
    *   **User Authentication:** Update the extension to include an authentication flow (redirect to web app login) and store the user token for `POST /ingest` requests.
    *   **`background.js` (Service Worker):** Ensure the `fetch` request for `/ingest` correctly handles user authentication and sends data to the main backend API.

**GrandDraft Formatting Manifest to inject into ALL LLM calls for content generation:**

"You are the Senior Document Architect for SynapseIP. You must strictly adhere to the following Markdown formatting rules. Your output will be processed and rendered by a professional document generator.

Strict Formatting Rules:
1. Use `#` ONLY for the Title of the entire document.
2. Use `##` for Chapter Titles. Each `## Chapter Title` MUST be preceded by a horizontal rule (`---`) to indicate a page break.
3. Use `###` for all Sub-headers.
4. Use `####` for detailed sub-points or specific data groupings.
5. Use `---` (horizontal rules) to separate distinct logic blocks within chapters/sections, in addition to preceding `## Chapter Titles`.
6. All comparison, financial projection, or timeline data points MUST be in a Markdown table.
7. Any introductory Executive Summaries for chapters and concluding Key Takeaways for sections MUST use Markdown blockquotes (`>`).
8. Use bullet points (`*` or `-`) for non-sequential items and numbered lists (`1.`) for step-by-step instructions or priorities.
9. Use `**Bold**` only for key terms or the first mention of a technical concept; DO NOT use bolding for headers.
10. Prohibit conversational phrases like 'Sure, here is...', 'In conclusion,', 'As an AI model, I...', 'Here's Chapter X:'. Provide raw content only.
11. All financial formulas or technical metrics must be wrapped in `$math$` for professional LaTeX rendering.
"

This comprehensive prompt ensures all aspects of the 'Advanced Document Generation' feature, from backend logic and UI to international compatibility and output quality, are addressed by Antigravity."
```

---

## 9. Deployment Preparation: Hosting (Vercel) & External Services

# 9. Deployment Preparation: Hosting (Vercel) & External Services

## 1. Feature Purpose & Logic

This feature establishes the foundational infrastructure and external service integrations required for SynapseIP to operate as a public, commercial SaaS application. Given SynapseIP's purpose of generating extensive reports via AI, efficient hosting and robust external services are critical for managing high API costs, user access, data storage, and global reach.

---

### Why this feature is needed:

*   **Public Accessibility:** To make SynapseIP available to users globally (or in specific regions like China), a continuously online and accessible backend is essential.
*   **Commercialization:** Implementing monetization (e.g., a token credit model) requires a payment gateway, user authentication, and a system to track usage against credits.
*   **Data Handling:** Generating 100+ page reports demands scalable storage for both input (Gemini chats) and output (generated documents).
*   **AI Orchestration:** The app's core logic, which involves complex multi-agent workflows and iterative calls to large language models (LLMs), must reside on a powerful and stable server.
*   **China-Specific Connectivity:** Users in restricted regions like China require a proxy mechanism to reliably interact with global AI services.

---

### Calculation & Logic:

*   **Hybrid Hosting Model:**
    *   The Chrome Extension (frontend) will be distributed via the Chrome Web Store.
    *   The core application backend (API, PDF generator, database interaction) and a user-facing web dashboard will be hosted on **Vercel**.
*   **Vercel Quota Management:**
    *   Vercel's Hobby (Free) Tier provides cumulative quotas (e.g., 100 GB bandwidth, 100 GB-hours serverless execution, 6,000 build minutes) across *all* projects on an account. This is typically sufficient for initial personal use but requires monitoring for growth.
    *   **Payload Limit Mitigation:** Vercel's serverless functions have a 4.5 MB payload limit. For 100+ page reports, direct output is infeasible.
        *   **Solution:** The backend will generate large reports, save them to **Vercel Blob Storage** (free 1GB tier), and return a secure download link to the user, rather than the report itself.
*   **LLM Abstraction Layer:**
    *   To prevent vendor lock-in and enable flexibility with AI model providers (Gemini, OpenAI, Anthropic), the application will interact with a generic `LLMInterface` rather than directly calling specific API methods (e.g., `gemini.generate()`). This design ensures easy swapping of underlying AI models.
*   **Payment Integration (Stripe):**
    *   A `User` model in the backend database will track `Available Credits`.
    *   The `/generate-report` API endpoint will be gated to only execute if the user possesses a positive credit balance.
    *   Credit costs will be calculated based on the requested report's length (e.g., 1 credit per 1,000 words generated).
    *   Payment processing will occur on SynapseIP's dedicated website via Stripe webhooks.
*   **Authentication (Clerk/NextAuth.js):**
    *   A robust authentication service is needed to manage user sign-ups, logins, and secure access to their data and credit balances.
*   **Transactional Email (SendGrid/Resend/Mailgun):**
    *   Automated emails for account verification, password resets, and credit notifications are crucial for user experience and account management.
*   **China-Specific Connectivity (Reverse Proxy):**
    *   The SynapseIP backend, hosted on Vercel (ideally in a nearby region like Tokyo or Singapore), will act as a reverse proxy. The Chrome Extension will send data to SynapseIP's API endpoint (e.g., `https://synapseip.com/ingest`), which is less likely to be blocked than direct Google services.
    *   The SynapseIP backend will then make the actual calls to the Gemini API, effectively bypassing regional access restrictions for the generation process.

---

## 2. Expected Outcomes

### If it works (Successful Deployment & Integration):

*   **Seamless User Flow:** Users can install the Chrome Extension, log in to SynapseIP's web dashboard, sync Gemini chats, view their credit balance, initiate report generation, and receive a download link for their multi-page reports.
*   **Stable Performance:** The Vercel backend handles incoming requests and orchestrates LLM calls efficiently, even for large document generations, and gracefully manages network instabilities (e.g., China access).
*   **Secure Transactions:** User payments are processed securely via Stripe, and credit balances are accurately reflected.
*   **Maintainable Architecture:** The LLM abstraction layer allows for easy switching of AI providers without extensive code refactoring, and a flexible scraper configuration minimizes breakage from UI updates on source platforms.
*   **Cost Efficiency:** The token credit model ensures profitability by directly linking revenue to API usage, with transparent costs and profit margins.

---

### If it fails (Deployment/Integration Issues):

*   **Vercel Deployment Errors:** Incompatible project structure, exceeding payload limits (if not mitigated by Blob storage), or excessive resource consumption on the free tier could lead to build failures or runtime errors.
*   **API Connectivity Issues:**
    *   **China Users:** Without the reverse proxy, users in China may be unable to sync chats or generate reports due to direct blocks on Google services. Even with a proxy, network instability could lead to timeouts.
    *   **LLM Provider:** Incorrect API keys, rate limits from the LLM provider, or unexpected changes in the LLM API could prevent report generation.
*   **Payment Failures:** Incorrect Stripe webhook configuration, API key issues, or network problems could prevent credit purchases or proper deduction upon report generation.
*   **Authentication Errors:** Users unable to sign up or log in, leading to a blocked user experience.
*   **Chrome Extension Rejection:** Failure to comply with Manifest V3 security policies (e.g., remotely hosted logic) could prevent the extension from being published.
*   **Data Inconsistency:** Reports may be incomplete, incorrectly formatted, or fail to generate if the internal logic (credit deduction, source retrieval, iterative generation) is flawed.

---

## 3. User Interaction & UI Component

User interaction for deployment preparation mostly revolves around setting up external services and managing billing/access once deployed.

### UI Component: 'SynapseIP Settings & Billing Dashboard'

This dashboard will serve as the central hub for users to manage their SynapseIP account, credits, and generated reports.

*   **Purpose:** Provide a clear, modern interface for users to control their account, monitor usage, purchase credits, and access their generated documents. It makes the monetization model transparent and easy to use.
*   **Design Principles:**
    *   **Clean & Intuitive:** Minimalist design, easy-to-understand navigation.
    *   **Responsive:** Works seamlessly on desktop and mobile devices.
    *   **Modern Aesthetics:** Utilizes contemporary UI trends (e.g., subtle shadows, rounded corners, clear typography).
    *   **Feedback-Driven:** Provides immediate visual feedback for actions (e.g., loading states, success/error messages).

### Component Breakdown:

*   **Navigation Sidebar (Left):**
    *   **Dashboard:** Overview of credits, recent activity.
    *   **My Reports:** List of generated reports with download links.
    *   **Credit Packs:** Purchase options.
    *   **Account Settings:** User profile, security.
    *   **Integrations:** Manage connected services (e.g., Google Drive sync).
*   **Main Content Area (Right):**
    *   **Credit Balance Display:** A prominent card showing "Available Credits" and potentially "Estimated Reports Remaining."
        *   *Visuals:* Large, clear number; progress bar for credit usage.
    *   **Credit Purchase Section:**
        *   *Title:* "Top Up Your SynapseIP Credits"
        *   *Credit Pack Cards:* Visually appealing cards for each tier (e.g., "Starter Pack: 100 Draft Pages - $19", "Pro Bundle: 500 Draft Pages - $49"). Each card includes:
            *   Price prominently displayed.
            *   Number of "Draft Pages" or "Expansion Credits".
            *   Clear "Purchase Now" or "Add to Cart" button.
            *   Small text about the value proposition (e.g., "Enough for one 100-page Executive Report").
        *   *Payment Form (Stripe Elements):* Integrated directly into the page or as a modal, providing a secure and familiar payment experience for credit card details.
            *   *Inputs:* Card Number, Expiry Date, CVC, Zip Code.
            *   *Buttons:* "Confirm Purchase"
    *   **Generated Reports List:**
        *   A table or card-based list showing:
            *   Report Title
            *   Date Generated
            *   Credit Cost
            *   Status (Generating, Completed, Failed)
            *   "Download" button (when complete) or "Retry" (if failed).
    *   **Chrome Extension Status:**
        *   Small section indicating if the extension is connected and active.
        *   Button to "Download Extension" or "Re-sync Extension".

---

## 4. Antigravity Designer Prompt

```
Antigravity, design and implement the user-facing 'Settings & Billing Dashboard' for SynapseIP. This dashboard needs to be highly performant, visually appealing, and intuitive for managing user accounts, credits, and access to generated reports. Target a modern, professional aesthetic with a focus on usability.

**UI Component: SynapseIP Settings & Billing Dashboard**

**Requirements:**

1.  **Layout:**
    *   A responsive two-column layout: a fixed navigation sidebar on the left and a dynamic content area on the right.
    *   Ensure the design is clean, minimalist, and uses modern UI elements (e.g., rounded corners, subtle shadows, clear typography).

2.  **Navigation Sidebar (Left Column):**
    *   Create a vertical navigation menu with the following items:
        *   `Dashboard` (Active by default, showing credit overview)
        *   `My Reports` (Lists user's generated documents)
        *   `Credit Packs` (Where users purchase more credits/subscriptions)
        *   `Account Settings` (User profile and security options)
        *   `Integrations` (Placeholder for future third-party service connections like Google Drive).
    *   Each navigation item should be clickable and change the main content area.

3.  **Main Content Area (Right Column) - Dashboard View:**
    *   **Credit Balance Card:** Display a large, prominent card at the top showing the user's "Available Credits". Include a small visual element like a circular progress bar to indicate credit usage.
    *   **Credit Purchase Section (within Credit Packs view):**
        *   Create 3-4 distinct "Credit Pack" cards (e.g., Starter, Pro, Executive).
        *   Each card must clearly display:
            *   The package Name (e.g., "Starter Pack").
            *   The Price (e.g., "$19").
            *   The quantity of "Draft Pages" or "Expansion Credits" included (e.g., "100 Draft Pages").
            *   A concise value proposition or example usage (e.g., "Enough for one 100-page business plan").
            *   A prominent "Purchase Now" button.
        *   **Integrated Payment Form:** Below the credit packs, embed a Stripe Elements payment form (no direct credit card input, use Stripe's secure iframe/components). Include fields for card number, expiry, CVC, and postal code. Add a "Confirm Purchase" button that initiates the Stripe checkout.
    *   **Generated Reports List (within My Reports view):**
        *   Display user's generated reports in a paginated table or scrollable card view.
        *   Each item should show: Report Title, Date Generated, Credit Cost, and a Download button.
        *   Include a status indicator (e.g., "Generating...", "Completed", "Failed") next to each report.

4.  **Chrome Extension Status Card (Optional, for Dashboard or Integrations view):**
    *   A small card indicating if the SynapseIP Chrome Extension is connected.
    *   Include a button to "Download Extension" or "Re-sync Connection" if disconnected.

**Technical Considerations for Antigravity:**

*   Generate the frontend using React (or similar modern framework).
*   Ensure the UI components are modular and reusable.
*   Integrate placeholder logic for fetching `user_credits` and `reports_list` from a `/api/user/credits` and `/api/user/reports` backend endpoint.
*   Implement client-side routing for the navigation sidebar.
*   For Stripe integration, use the official Stripe React components (e.g., `@stripe/react-stripe-js`).
*   Include basic CSS styling that aligns with a clean, modern, dark-mode friendly design palette.

**Expected Artifacts from Antigravity:**

*   React components for the dashboard, navigation, credit cards, and report list.
*   CSS modules or a global stylesheet for the component styling.
*   Placeholder API calls for user data and Stripe interaction.
*   Instructions on how to integrate Stripe API keys securely.

```

---

## 10. Global Accessibility & LLM Abstraction ('Shanghai-Proofing')

# 10. Global Accessibility & LLM Abstraction ('Shanghai-Proofing')

## 1. Feature Justification & Logic Calculation

This feature ensures SynapseIP remains functional and adaptable for a global user base, especially in regions with internet restrictions, and provides technical resilience against changes in LLM ecosystems.

### 1.1. Why Global Accessibility ('Shanghai-Proofing') is Needed
*   **Problem:** Direct access to Google's Gemini API and `gemini.google.com` is restricted in certain regions (e.g., China) due to internet censorship. Without mitigation, users in these regions cannot access core SynapseIP functionalities.
*   **Calculation/Logic:**
    *   **User's VPN Requirement:** Users initiating brainstorming directly on `gemini.google.com` will still require a VPN to access that specific Google domain.
    *   **SynapseIP Backend as a Reverse Proxy:** SynapseIP's server-side logic (backend) acts as an intermediary. The Chrome Extension sends data to SynapseIP's backend API (hosted in an unrestricted, geographically optimal region like Singapore or Tokyo), which then securely forwards requests to the Gemini API (or other LLMs). This allows users to interact with SynapseIP without needing a VPN for syncing or report generation *after* initial content acquisition.

### 1.2. Why LLM Abstraction is Needed
*   **Problem:** Tightly coupling SynapseIP to a single LLM provider (e.g., Gemini) creates significant risks:
    *   **Vendor Lock-in:** Difficult and costly to switch providers if pricing, performance, or terms of service change.
    *   **Resilience:** An outage or API change by one provider could render SynapseIP inoperable.
    *   **Optimization:** Limits the ability to select the best model for different tasks (e.g., one model for summarization, another for deep expansion) or user tiers.
*   **Calculation/Logic:**
    *   **Interface-Based Design:** Implement a generic `LLMInterface` that defines standard methods (e.g., `generate_content`, `summarize_text`, `embed_text`).
    *   **Provider Implementations:** Create concrete classes (e.g., `GeminiProvider`, `ClaudeProvider`, `OpenAIProvider`) that implement the `LLMInterface`, each encapsulating the specific API calls and request/response formats for that LLM.
    *   **Dynamic Selection:** SynapseIP's core logic interacts solely with the `LLMInterface`, allowing the application to dynamically load and use different LLM providers based on configuration, user preference, or feature requirements without extensive code changes.

---

## 2. Expected Outcomes: Success & Failure

### 2.1. Global Accessibility (Shanghai-Proofing)
*   **Success:**
    *   Users in restricted regions can seamlessly sync their Gemini chat data to SynapseIP via the Chrome Extension (after initial Gemini website access via VPN) and generate reports from the SynapseIP web dashboard without requiring a VPN for these operations.
    *   Network requests from the Chrome Extension to `your-api.com/ingest` and from the SynapseIP backend to `generativelanguage.googleapis.com` (or other LLM APIs) are stable and successful.
    *   The backend's proxy logic includes 'Timeout and Retry' mechanisms to handle transient network instabilities inherent in cross-border connections.
*   **Failure:**
    *   **Initial Brainstorming (External):** Users cannot access `gemini.google.com` to initiate brainstorming without a stable VPN. (This is outside SynapseIP's control).
    *   **Sync/Generation (Internal):**
        *   The Chrome Extension fails to connect to `your-api.com/ingest` (e.g., backend server inaccessible from user's location, custom domain blocked).
        *   The SynapseIP backend fails to connect to the LLM API (e.g., proxy issue, LLM API blocked from hosting region).
        *   Error messages like "SynapseIP: Failed to sync conversation. Please check your network connection," or "Report generation failed: Our AI provider is unreachable."

### 2.2. LLM Abstraction
*   **Success:**
    *   You can switch the underlying LLM model (e.g., from Gemini Pro to Claude 3.5) by changing a simple configuration setting in your backend (e.g., an environment variable or a database entry) and redeploying, with minimal or no changes to the core application logic.
    *   New LLM providers can be integrated by creating a new `Provider` class that implements the `LLMInterface`.
    *   This allows for A/B testing of different models for specific tasks or tailoring models to different report types.
*   **Failure:**
    *   Switching LLM providers requires significant code modifications across multiple parts of the application, leading to increased development time, potential bugs, and a high risk of downtime.
    *   The app becomes entirely dependent on a single LLM provider, making it vulnerable to their service disruptions or unfavorable changes.

---

## 3. User Interaction & UI Component for Layout Changes

To address the "Scraping Fragility" risk inherent in extensions that parse web page content, a user interaction point is crucial.

### 3.1. UI Component: "Layout Change Detected" Notification

*   **Purpose:** To inform users when the Chrome Extension detects that an LLM chat interface (like Gemini's) has changed, potentially breaking the auto-sync functionality, and to solicit user input for quick adaptation.
*   **Location:** A subtle, dismissible toast notification or small modal dialog appearing on the affected LLM chat page (`gemini.google.com`, `chatgpt.com`, etc.) where the scraper failure occurred.

### 3.2. Visual Design & Behavior

*   **Visual Style:** Modern, clean, and integrated with the browser's aesthetic but clearly distinct. Use a professional color palette, e.g., muted grays, whites, with an amber or soft red for the warning icon and primary blue for action buttons.
*   **User Flow:**
    1.  User is on `gemini.google.com` (or other supported LLM chat).
    2.  The SynapseIP Chrome Extension attempts to sync new chat content, but its scraping logic (CSS selectors) fails to find the expected elements due to a UI update on `gemini.google.com`.
    3.  The "Layout Change Detected" notification appears.
    4.  User can either:
        *   Click **"Report Layout Change"**: This triggers a background process in the extension to capture and send anonymized diagnostic data (e.g., current page HTML structure, URL, timestamp, broken selector) to SynapseIP's backend for analysis by developers. The notification then dismisses, potentially with a brief "Thank you for reporting!" message.
        *   Click **"Dismiss"**: The notification disappears without sending data. It might reappear if the user attempts to sync again and the issue persists.

### 3.3. UI Element Details

*   **Notification/Dialog:**
    *   **Header:** "Sync Interrupted" (Prominent, clear)
    *   **Icon:** Warning triangle or broken chain link (visually signifies an issue).
    *   **Body Text:** "It appears [LLM Platform Name] has updated its interface. This may affect automatic syncing."
    *   **Call to Action Text:** "Help us adapt quickly by reporting this change."
    *   **Primary Button:** "Report Layout Change"
    *   **Secondary Button:** "Dismiss"
*   **State Management:**
    *   The notification should appear once per session (or until the issue is resolved) to avoid annoyance.
    *   A loading state (e.g., spinner or "Sending report...") should be shown briefly when the "Report Layout Change" button is clicked.

---

## 4. Antigravity Designer Prompt

```
"Antigravity, design a modern, non-intrusive Chrome Extension UI component for SynapseIP, specifically to handle detected layout changes on third-party AI chat websites.

Component Type: Implement this as a dismissible toast notification.
Placement: The toast should appear in the top-right corner of the active browser tab where an LLM chat page (e.g., gemini.google.com, chatgpt.com) is open.
Styling:
- Use a clean, modern aesthetic with subtle fade-in/fade-out animations.
- Adhere to a professional, accessible color palette. The background should be a light, neutral gray (`#f5f5f5`), text dark gray (`#333333`).
- A subtle border or shadow for definition.
- Use rounded corners for the notification box.

Elements & Content:
- **Icon (Warning):** Integrate a distinct warning icon (e.g., a yellow/amber exclamation mark inside a triangle) to the left of the title.
- **Title (`h3`):** 'Sync Interrupted: Layout Change Detected'
    - Font: 'Inter', `font-weight: 600` (Semi-Bold), `font-size: 16px`, `color: #333333`.
- **Message (`p`):** 'It appears [LLM Platform Name, e.g., Gemini] has updated its interface. This may affect automatic syncing. Please consider reporting this to help us adapt quickly.'
    - Font: 'Inter', `font-weight: 400` (Regular), `font-size: 14px`, `color: #555555`.
- **Primary Action Button (`button`):** 'Report Layout Change'
    - Style: Prominent blue button (`background-color: #1a73e8`, `color: white`, `border-radius: 4px`, `padding: 8px 16px`).
- **Secondary Action Button (`button`):** 'Dismiss'
    - Style: Less prominent, ghost button or text link (`color: #555555`, `background: none`, `border: none`).

Behavioral Flow:
1.  **Appearance:** The notification should fade in gracefully when triggered by a scraper error.
2.  **User Action - 'Report Layout Change' Click:**
    *   The button should momentarily change to a disabled state with text 'Sending Report...' and a small inline spinner.
    *   Upon successful (or failed) report submission, the notification should fade out, replaced briefly by a 'Report Sent! Thanks!' toast or similar.
3.  **User Action - 'Dismiss' Click:** The notification should fade out immediately.
4.  **Auto-Dismissal:** If no action is taken, the notification should automatically fade out after 15 seconds.

Provide the complete HTML, CSS, and skeleton JavaScript (React functional component recommended for integration with Antigravity's frontend capabilities) to implement this toast notification, including event handlers for button clicks and a mechanism to accept dynamic `LLM Platform Name` via props."
```

---

## 11. SynapseIP Meta-Feature: Generic Idea Viability Rubric

# 11. SynapseIP Meta-Feature: Generic Idea Viability Rubric

## 1. Feature Overview and Purpose

This meta-feature transforms SynapseIP into a "Validator-as-a-Service," enabling it to objectively evaluate *any* new app idea submitted by a user. Instead of relying on "gut feeling," users will receive a data-driven "Idea Health Score" (0-100), along with critical analysis.

*   **Why this feature is needed:**
    *   **Aids Founders:** Helps users identify and address weaknesses in their app ideas before committing significant resources.
    *   **Builds Trust:** Positions SynapseIP as a genuine and valuable business intelligence architect, not just a content generator.
    *   **Creates Feedback Loop:** Encourages users to refine their ideas based on SynapseIP's feedback and return for re-evaluation.
    *   **Lead Magnet:** A free version of this validator could attract new users to the SynapseIP platform.

---

## 2. Core Logic and Calculation

SynapseIP will apply a 100-point rubric to the user's submitted idea, based on four key pillars. The AI will analyze the textual description of the app idea to derive scores for each metric.

*   **100-Point Viability Rubric Breakdown:**

| Pillar                      | Weight | What it measures                                                                                                                | Scoring Logic (AI Interpretation)                                                                                                              |
| :-------------------------- | :----- | :---------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Market Gravitational Pull** | 30%    | How strong is the problem being solved? Is the market growing or shrinking?                                             | **Pain Intensity (15 pts):** Critical business blocker (15) ➞ Trivial convenience (0).<br>**Market Growth (15 pts):** Growing industry/niche (15) ➞ Saturated/shrinking (0). |
| **2. The "Moat" Potential**     | 25%    | How easily can a competitor replicate the idea? How hard is it for users to switch?                                     | **Uncopyability (15 pts):** Hard for major players to replicate (15) ➞ Easily copied (0).<br>**Data/Workflow Lock-in (10 pts):** High effort to switch (10) ➞ Easy to switch (0). |
| **3. Economic Scalability**     | 25%    | Is the cost to serve a customer significantly lower than the price? Is it a high-frequency/high-retention tool?         | **Unit Economics (15 pts):** API/hosting cost << price (15) ➞ Cost > price (0).<br>**Frequency/Retention (10 pts):** Daily/weekly use (10) ➞ One-time use (0). |
| **4. Technical Feasibility**    | 20%    | Does it rely on fragile methods (e.g., scraping)? Does it require massive/expensive infrastructure?                    | **Edge Reliability (10 pts):** Stable APIs (10) ➞ Fragile scraping (0).<br>**Complexity (10 pts):** Lean & efficient (10) ➞ Massive/expensive infrastructure (0). |

*   **Output Logic:**
    *   **Idea Health Score:** A numerical score from 0-100, calculated by summing the scores of all metrics.
    *   **The Harsh Truth (Flop Risk):** Identification of the single biggest vulnerability or challenge based on the lowest-scoring rubric pillar/metric.
    *   **The Pivot Path:** A concrete suggestion for a structural change or additional detail that would significantly improve the idea's score (e.g., by 20+ points).
    *   **Verdict:** A clear assessment: 'Green Light (Build)', 'Yellow Light (Refine)', or 'Red Light (Pivot/Abandon)'.

---

## 3. User Interface (UI) Component

A modern, usable, and beautiful UI component within the SynapseIP web application will allow users to input their app idea and instantly view the evaluation.

*   **UI Layout:**
    *   **Input Section:**
        *   A prominent, multi-line text area labeled "Describe Your App Idea" (e.g., a `textarea` element).
        *   A clear instruction: "Provide a detailed overview of your app's purpose, target audience, core features, and monetization strategy."
        *   A "Evaluate Idea" button (e.g., a primary button with a clear call to action).
    *   **Results Display (Dynamic):** This section appears after evaluation.
        *   **Idea Health Score:** A large, visually distinct number (0-100) prominently displayed, possibly with a subtle animation or a radial progress bar.
        *   **Verdict:** A "traffic light" indicator (Green/Yellow/Red circle or banner) with the text 'Green Light (Build)', 'Yellow Light (Refine)', or 'Red Light (Pivot/Abandon)'.
        *   **Pillar Breakdown:** A collapsible section or small cards showing the score for each of the four pillars (Market Gravitational Pull, Moat Potential, Economic Scalability, Technical Feasibility), with a brief explanation of how that score was derived.
        *   **"The Harsh Truth" (Flop Risk):** A dedicated card or section clearly stating the biggest identified risk in a concise, action-oriented manner.
        *   **"The Pivot Path" (Suggestion):** A dedicated card or section offering a specific, actionable recommendation for improving the idea, possibly presented as a question to encourage further brainstorming.

*   **Styling (CSS):**
    *   Utilize SynapseIP's existing design system for consistency.
    *   Use modern, clean typography (e.g., `Inter`, `Roboto`).
    *   Employ subtle shadows and rounded corners for cards and input fields for a premium feel.
    *   Color-code the "Verdict" indicator (Green for Go, Yellow for Refine, Red for Abandon) for instant visual feedback.
    *   Ensure responsiveness across different screen sizes.

---

## 4. Expected Outcomes

### If it works:

*   **Objective Assessment:** Users receive a clear, numerical Idea Health Score and a concise verdict.
*   **Actionable Insights:** Specific "Flop Risks" and "Pivot Paths" are identified, giving users concrete steps to improve their ideas.
*   **Enhanced User Experience:** The UI is intuitive and engaging, making the evaluation process smooth and insightful.
*   **Increased Trust:** Users perceive SynapseIP as an intelligent, helpful partner in their development journey.
*   **Faster Iteration:** Users can quickly validate and refine multiple ideas.

### If it fails:

*   **Generic Feedback:** SynapseIP provides vague or irrelevant assessments that don't help the user.
*   **Inaccurate Scoring:** The "Idea Health Score" does not reflect the true viability of the idea, leading to misleading guidance.
*   **UI Issues:** The interface is clunky, unreadable, or fails to display the results correctly.
*   **"AI Drift":** The AI misinterprets the rubric or the user's input, resulting in an unhelpful or even contradictory evaluation.

---

## 5. Antigravity Build Prompt

```
Antigravity, let's build the 'Generic Idea Viability Rubric' meta-feature for SynapseIP.

1.  **Backend Logic (FastAPI):**
    *   Create a new Python module (e.g., `app/features/idea_validator.py`) that contains a function `evaluate_idea(idea_description: str) -> dict`.
    *   This function should internally house the "100-Point Viability Rubric" logic.
    *   It must prompt the Gemini 1.5 Pro API (using an environment variable `GEMINI_API_KEY`) to analyze the `idea_description` against each metric of the rubric:
        *   Market Gravitational Pull (Pain Intensity, Market Growth)
        *   The "Moat" Potential (Uncopyability, Data/Workflow Lock-in)
        *   Economic Scalability (Unit Economics, Frequency/Retention)
        *   Technical Feasibility (Edge Reliability, Complexity)
    *   The Gemini API prompt should explicitly instruct the model to provide a score (0-15 or 0-10) for each sub-metric, a concise "Flop Risk," a specific "Pivot Path" suggestion, and a final "Verdict" (Green/Yellow/Red Light).
    *   The `evaluate_idea` function will then aggregate these scores to calculate the overall "Idea Health Score" (0-100).
    *   Expose this functionality via a new POST endpoint `/api/evaluate-idea` in `app/main.py`, accepting a JSON payload `{ "idea_description": "..." }` and returning the evaluation `dict`.

2.  **Frontend Component (React):**
    *   Create a new React component `IdeaValidator.jsx` in the frontend (assuming a standard React setup).
    *   This component should include:
        *   A modern, multi-line `textarea` for user input of `idea_description`.
        *   A "Evaluate Idea" button that sends the input to the `/api/evaluate-idea` endpoint.
        *   A dynamic display area for the evaluation results:
            *   Large, bold display of "Idea Health Score".
            *   Clear "Verdict" (Green/Yellow/Red light indicator).
            *   Expandable sections (e.g., accordions or cards) for each of the four rubric pillars, showing their individual scores and the AI's brief rationale.
            *   Dedicated, clearly labeled sections for "Biggest Flop Risk" and "Pivot Path" with the AI's generated text.

3.  **Styling (CSS):**
    *   Create `IdeaValidator.css` to style the `IdeaValidator.jsx` component.
    *   Use a clean, modern aesthetic with ample whitespace, readable fonts (e.g., `font-family: 'Inter', sans-serif;`).
    *   Implement clear visual indicators for the "Verdict" (e.g., a green, yellow, or red background for the verdict section).
    *   Ensure the component is fully responsive for desktop and mobile views.

4.  **Integration:**
    *   Add a new route or navigation link within the existing SynapseIP frontend to access the `IdeaValidator` component.

**Strict Formatting Rules for AI Output (for the *internal* Gemini prompt used by the `evaluate_idea` function):**
*   Use `#` ONLY for the Title of the entire document (e.g., "Idea Viability Assessment").
*   Use `##` for Chapter Titles (e.g., "Market Gravitational Pull").
*   Use `###` for all Sub-headers (e.g., "Pain Intensity").
*   Use `---` (horizontal rules) to separate distinct logic blocks within the output.
*   All data points MUST be in a bulleted list (`*`) or a Markdown table.
*   DO NOT use bolding (`**`) for headers; use the appropriate `#` tag.
*   Ensure the final output always includes `Idea Health Score (0-100)`, `The Harsh Truth:`, `The Pivot Path:`, and `Verdict:`.
```

---

