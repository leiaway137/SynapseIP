# SynapseIP - Master Blueprint

**Designer:** Albert Vincent Lei

**Target Platform:** Antigravity

**Version:** 1.0.0

**Date:** 2026-04-18

---

## Executive Purpose
speed up my process of vibe coding, by creating an extension that syncs responses from Gemini conversations to the app, which then processes these notes to develop an implementation plan with step-by-step prompt instructions for developing a minimum viable product in the user's preferred IDE for vibe coding.

---

## Table of Contents

1. [1. UI/UX Exploration & Frontend Scaffolding](#1-ui/ux-exploration-&-frontend-scaffolding)
2. [2. Backend "Librarian" Development (FastAPI & Database)](#2-backend-"librarian"-development-(fastapi-&-database))
3. [3. Chrome Extension "Messenger" Development (Gemini-specific)](#3-chrome-extension-"messenger"-development-(gemini-specific))
4. [4. Core "Architect" Logic (Report Generation)](#4-core-"architect"-logic-(report-generation))
5. [5. Initial Deployment & Testing](#5-initial-deployment-&-testing)
6. [6. UI for Report Interaction & Display](#6-ui-for-report-interaction-&-display)

---

## 1. UI/UX Exploration & Frontend Scaffolding

# 1. UI/UX Exploration & Frontend Scaffolding

This document outlines the systematic steps for building the initial user interface (UI) and user experience (UX) scaffolding for SynapseIP, utilizing Antigravity. This phase focuses on creating the visual and interactive foundation for the application and its companion browser extension.

---

## 1.1 Feature Purpose & Logic

This feature is the cornerstone of SynapseIP, providing the direct interface through which users interact with the application. Its purpose is multifaceted:

*   **User Engagement:** To offer an intuitive and visually appealing platform for managing Gemini conversations and generating comprehensive reports.
*   **Data Ingestion Entry Point:** To provide a seamless, low-friction method (via a browser extension) for users to sync their Gemini conversations to the SynapseIP backend without manual copy-pasting.
*   **Content Visualization:** To consistently and beautifully render processed Gemini notes and the generated multi-page implementation plans or business reports, ensuring readability and professionalism.
*   **Workflow Orchestration:** To allow users to trigger complex backend processes (like report generation) through clear UI controls, while providing feedback on progress.

**Calculation/Logic:**
The frontend's logic will involve:

*   **Routing:** Navigating between different views (e.g., "My Notes," "Generate Report," "Settings").
*   **Component Rendering:** Dynamically displaying data fetched from the backend API (once implemented). This includes using a Markdown parsing library (e.g., `react-markdown`) to transform raw Markdown content into styled HTML based on predefined CSS.
*   **Event Handling:** Capturing user interactions (e.g., button clicks, form submissions) and translating them into API requests to the SynapseIP backend.
*   **State Management:** Managing the application's current data and UI state (e.g., loading indicators, form inputs, selected notes).
*   **Extension-to-App Communication:** The browser extension will scrape content from Gemini and send it via a `POST` request to the SynapseIP backend API endpoint (e.g., `/ingest`).

---

## 1.2 Success & Failure Criteria

### Success
*   The SynapseIP web application loads successfully in the user's preferred IDE environment.
*   Basic navigation elements (sidebar, main content area) are present and functional.
*   The custom "Sync to SynapseIP" button appears correctly positioned next to Gemini conversation bubbles.
*   Clicking the extension button or the in-app "Generate Report" button provides immediate visual feedback (e.g., a momentary spinner, toast notification).
*   Placeholder data (or initial synced data) is rendered on the dashboard and in the report viewer with consistent, modern styling (headers, lists, code blocks, blockquotes, tables).

### Failure
*   The web application fails to compile or run, resulting in a blank screen or error messages.
*   UI components (buttons, forms, navigation) are missing, broken, or unresponsive.
*   The browser extension fails to load, or the "Sync to SynapseIP" button does not appear on Gemini pages.
*   Content rendered within the application (e.g., mock reports or synced notes) displays inconsistent formatting, incorrect Markdown parsing, or no styling.
*   No visual feedback is provided for user interactions with the app or extension.

---

## 1.3 UI Components for User Interaction

The initial UI/UX exploration will focus on creating core components that are beautiful, usable, and adhere to a modern design aesthetic, ensuring a seamless experience for vibe coding workflows.

### 1.3.1 SynapseIP Web Application Dashboard

*   **Overall Layout & Navigation:**
    *   A clean, single-page application structure built with React.
    *   A fixed **left-hand sidebar** for primary navigation: "My Notes," "Generate Report," "Settings," "Account/Billing" (if applicable). Icons should be modern and minimalist.
    *   A **main content area** that dynamically renders views based on navigation selection.
    *   A **top header bar** displaying the "SynapseIP" logo/name and possibly a user avatar/status.
    *   Utilize a dark theme or offer a toggle for dark/light mode, aligning with a "vibe coding" environment.

*   **"My Notes" Section:**
    *   Displays a list of previously synced Gemini conversations (source material).
    *   Each item in the list should be a distinct card or row showing:
        *   A concise **title** automatically generated from the conversation's first few lines.
        *   The **timestamp** of sync.
        *   A short **snippet** of the conversation content.
        *   An **icon** indicating the source (e.g., Gemini logo).
        *   Hover effects for more options (e.g., "View," "Add to Project," "Delete").
    *   A prominent **search bar** at the top for filtering notes by keywords.
    *   A mechanism to create "Project Buckets" – visual tags or drag-and-drop functionality to group related notes for report generation.

*   **"Generate Report" Interface:**
    *   A clear, multi-step form or wizard to guide the user through report creation.
    *   **Step 1: Select Source Material:** A component to pick notes from "My Notes" or "Project Buckets." Drag-and-drop or checkbox selection.
    *   **Step 2: Define Report Parameters:**
        *   Input fields for "Report Type" (dropdown: "Business Plan," "Technical Implementation," "Whitepaper").
        *   "Desired Length" (slider or input field, e.g., "10-20 pages," "50-100 pages").
        *   "Preferred IDE" for step-by-step instructions (dropdown: VS Code, IntelliJ, etc.).
        *   A large text area for "Additional Instructions/Context."
    *   **Step 3: Preview & Generate:**
        *   A summary of selected inputs.
        *   A prominent, action-oriented "Generate Comprehensive Plan" button.
        *   A progress bar or status area displaying real-time updates during report generation (e.g., "Outlining Chapters," "Drafting Section 1," "Auditing for Consistency").

*   **Report Viewer Component (`<ReportViewer />`):**
    *   This is the central component for displaying generated reports and even individual synced notes. It will be built upon a Markdown rendering library (e.g., `react-markdown`).
    *   **Styling (Based on Gemini Theme & Professional Report Standards):**
        *   **Headers:**
            *   `#` (Document Title): Large, bold, centered, dark gray (e.g., `#1A1A1A`).
            *   `##` (Chapter Titles): Prominent, bold, dark blue (e.g., `#1a73e8`), with a subtle bottom border (`2px solid #e0e0e0`) and `margin-top: 40px;` for clear separation. Each `##` should imply a new "page" in print view.
            *   `###` (Sub-headers): Bold, dark gray, slightly smaller than `##`.
            *   `####` (Sub-points): Standard font weight, dark gray.
        *   **Paragraphs:** `p` tags with comfortable `line-height: 1.6;` and a standard readable text color (e.g., `#3c4043`).
        *   **Horizontal Rules:** `---` rendered as a thin, light gray line across the width to separate logic blocks.
        *   **Lists:** `*` for bulleted lists, `1.` for numbered lists, with appropriate indentation.
        *   **Tables:** Markdown tables should render with clear borders, distinct header rows, and possibly subtle alternating row backgrounds for readability. Max 5 columns for print compatibility.
        *   **Blockquotes:** `>` rendered with a light-gray background, a strong left vertical border (e.g., 4px solid #D1E5F8), and slightly italicized text, used for Executive Summaries and Key Takeaways.
        *   **Code Blocks:** `pre` blocks should have a dark background (e.g., `#282C34`), rounded corners, and syntax highlighting for readability.
        *   **Boldness:** `**Text**` for strong emphasis, *not* for headers.
    *   **Action Buttons:** Prominent "Download PDF," "Download DOCX," and "Share" (if applicable) buttons.
    *   **Print Mode CSS:** Implement `@media print` rules to ensure proper page breaks before `h2` elements, and tables (`table { page-break-inside: avoid; }`) are not split across pages for professional printing.

*   **User Account / Credit Management (for public SaaS):**
    *   A dedicated view under "Settings" or "Account" showing the user's "Available Credits."
    *   A clear "Buy More Credits" button/link that integrates with Stripe for purchasing credit packs.
    *   A history of credit usage and purchases.

### 1.3.2 SynapseIP Browser Extension

*   **"Sync to SynapseIP" Button:**
    *   A small, elegant button injected dynamically next to each AI response bubble on `gemini.google.com` (and eventually other AI chat platforms like ChatGPT, Claude, Doubao).
    *   The button should feature a recognizable SynapseIP icon (e.g., a stylized "sync" or "upload" cloud) and the text "Sync to SynapseIP."
    *   It should maintain a consistent, modern appearance across different AI chat platforms for brand recognition, rather than trying to perfectly blend into each platform's native style.
    *   Upon click, a brief, non-intrusive animation (e.g., a spinner within the button) confirms data is being sent.

*   **Browser Toolbar Icon:**
    *   A small SynapseIP logo visible in the browser's extension toolbar.
    *   Clicking this icon should offer a minimalist popup with an option to "Sync Entire Conversation" or quickly access the main SynapseIP web dashboard.

---

## 1.4 Antigravity Build Prompt

This prompt guides Antigravity to scaffold the necessary frontend components and initial UI structure for the SynapseIP application and its browser extension.

```
"Antigravity, let's initiate the 'UI/UX Exploration & Frontend Scaffolding' for SynapseIP.

**Phase 1: SynapseIP Web Application (React Frontend)**

1.  **Project Initialization:** Create a new React project in a subfolder named `/frontend` using a modern boilerplate (e.g., Vite or Create React App) and set up basic routing with React Router DOM for the following paths:
    *   `/` (Dashboard - My Notes view)
    *   `/generate-report`
    *   `/report/:reportId` (for viewing individual reports)
    *   `/settings`
    *   `/account` (for user/billing if applicable)

2.  **Core Layout:** Design a minimalist layout with a fixed left sidebar (for navigation links to the routes above) and a main content area. Use a dark theme by default, or provide a theme toggle. Include a placeholder logo/app name in a top bar.

3.  **Report Viewer Component (`src/components/ReportViewer.jsx`):**
    *   Create a reusable React component `<ReportViewer />` that accepts `markdownContent` as a prop.
    *   Integrate the `react-markdown` library to parse and render this content.
    *   Create an associated CSS file (`src/styles/ReportViewer.module.css`) and apply the following styles to match a professional, Gemini-like theme, ensuring print-readiness:
        *   `h1, h2, h3` to be bold and dark gray/blue, using a sans-serif font (e.g., 'Inter').
        *   `pre` (code blocks) to have a dark background, rounded corners, and appropriate padding.
        *   `blockquote` to have a light-gray background and a prominent left vertical border.
        *   `---` (horizontal rules) to be rendered as subtle separators.
        *   `ul` and `ol` (lists) to have standard styling.
        *   `table` elements to have clear borders, distinct header rows, and to prevent page breaks within tables during printing (`@media print`).
        *   Implement `@media print` styles for `h2` to ensure each chapter starts on a new page.
    *   Include a placeholder "Download PDF" button in this component.

4.  **Placeholder Views:** Create basic placeholder components for each route (e.g., `DashboardPage.jsx`, `GenerateReportPage.jsx`) to demonstrate routing.

**Phase 2: SynapseIP Browser Extension (Chrome Manifest V3)**

1.  **Extension Initialization:** Create a Manifest V3 Chrome Extension in a subfolder named `/extension`.

2.  **Content Script (`content.js`):**
    *   Configure the content script to run on `https://gemini.google.com/*`.
    *   Write logic to identify Gemini's AI response bubbles (e.g., by CSS class `markdown-main-panel`) and inject a small, visually distinct "Sync to SynapseIP" button next to each response.
    *   The button should feature a cloud/sync icon and the text "Sync to SynapseIP". Style it for modern aesthetics and brand consistency.

3.  **Service Worker (`background.js`):**
    *   Implement the Service Worker to handle messages from the content script.
    *   When the "Sync to SynapseIP" button is clicked, the content script should send the extracted Markdown text of the response to the Service Worker.
    *   The Service Worker should then perform a `fetch` `POST` request to `http://localhost:8000/ingest` (assuming the backend API is running locally). This indirect communication avoids 'Mixed Content' blocks.

4.  **Browser Action Popup (`popup.html`, `popup.js`, `popup.css`):**
    *   Create a simple popup for the browser toolbar icon.
    *   Include a button "Sync Entire Conversation" and a link "Open SynapseIP Dashboard."

**Provide detailed instructions for loading and testing both the React app locally and the Chrome Extension as an 'unpacked' extension in Chrome Developer Mode.**"
```

---

## 2. Backend "Librarian" Development (FastAPI & Database)

# SynapseIP: Backend "Librarian" Development (FastAPI & Database)

## Feature Overview

The "Librarian" backend is the core data ingestion and storage component of SynapseIP. It acts as the central repository for all Gemini conversation data synced from the browser extension, preparing it for subsequent long-form report generation by the "Architect" component. This feature focuses on building the foundational FastAPI service and its associated database.

---

### 1. Why this Feature is Needed and its Logic

The Backend "Librarian" is essential for SynapseIP to:

*   **Provide Data Persistence:** Gemini conversations within the browser are ephemeral. The backend ensures that all valuable brainstorming notes and discussions are saved permanently, preventing loss of context or information.
*   **Establish a Centralized Source Material Repository:** It creates a single, organized storage location for all ingested Gemini discussions, eliminating the need for manual copy-pasting and making data readily available for further processing. This centralized "mailbox" for chat data is crucial for efficiently building comprehensive reports.
*   **Form the Foundation for Long-Form Expansion:** The stored and structured data is a prerequisite for the "Architect" component (the report generation engine) to retrieve information efficiently and generate extensive, multi-page reports without hallucinating or losing track of the initial context.
*   **Decouple System Components:** It separates the responsibility of data ingestion (handled by the Chrome Extension) from the complex, token-intensive document generation logic (handled by Gemini API calls). This modular design enhances system robustness and scalability.

---

### 2. Calculation/Logic

The core logic for the "Librarian" backend involves:

*   **API Endpoint Creation:** A `POST` endpoint, typically `/ingest`, is exposed using FastAPI. This endpoint is specifically designed to receive incoming JSON payloads from the Chrome Extension.
*   **Data Structure Definition:** A database schema (`GeminiSource`) is defined using SQLAlchemy. This schema outlines the structure for storing each ingested conversation, including fields for a `title`, the `content` (raw Markdown text), a `timestamp`, and the `source_url` of the Gemini conversation.
*   **Database Interaction:** SQLAlchemy acts as an Object Relational Mapper (ORM) to facilitate interaction with a local SQLite database (`database.db`). It handles the insertion of new `GeminiSource` records and retrieval for status checks.
*   **CORS (Cross-Origin Resource Sharing) Configuration:** Proper CORS settings must be enabled on the FastAPI application. This is critical to allow the Chrome Extension, which operates from a different browser origin (e.g., `https://gemini.google.com`), to securely send `POST` requests to the local backend server.
*   **Status Endpoint:** A root `GET` endpoint (`/`) provides a simple health check and reports the current number of stored "Gemini Sources," offering immediate feedback on the backend's operational status and data volume.

---

### 3. What to Expect if it Works or Fails

*   **If it Works (Success):**
    *   The FastAPI server will successfully launch and become accessible on your local machine, typically at `http://127.0.0.1:8000`.
    *   Accessing `http://127.0.0.1:8000/` in a web browser will display a simple JSON status page confirming the API is running and showing the current count of stored Gemini sources (initially "0 items in database").
    *   When the Chrome Extension sends a Gemini conversation via a `POST` request to `http://127.0.0.1:8000/ingest`, the server will process the data, save it to the `database.db` SQLite file, and return a success response to the extension.
    *   Refreshing `http://127.0.0.1:8000/` will show an incremented count of stored items, reflecting the successful ingestion.

*   **If it Fails (Failure):**
    *   The Antigravity terminal will display clear error messages if the FastAPI server fails to start (e.g., `Port 8000 is already in use`, `ModuleNotFoundError` for missing dependencies, or syntax errors in the Python code).
    *   The Chrome Extension attempting to send data will encounter network errors (e.g., `CORS policy blocked request`, `Failed to fetch`, or `Connection refused`). This indicates the backend is not running, is inaccessible, or its CORS configuration is incorrect.
    *   If data is sent but not persisted, the `/` status page will not update, or the `database.db` file will remain empty. This points to an issue within the FastAPI logic for handling the `POST /ingest` request, such as incorrect SQLAlchemy model usage or database transaction failures.

---

### 4. User Interaction and UI Component

The "Librarian" backend operates primarily on the server-side and does not have a direct user-facing interface. However, its successful operation is visually represented and managed through a dedicated **"Source Material Dashboard"** within the SynapseIP application's frontend. This UI component allows users to interact with the data stored by the backend.

*   **UI Component:** Source Material Dashboard
*   **Purpose:** To provide a beautiful, usable, modern interface for users to confirm that their Gemini conversations have been successfully ingested by the "Librarian" backend and are available as source material for report generation.
*   **Design and Functionality Instructions:**
    *   **Visual Style:** Employ a clean, minimalist design with modern typography (e.g., Google Fonts like Inter or Roboto), a harmonious color palette (perhaps muted blues, grays, and whites), and subtle use of shadows or borders to define distinct elements.
    *   **Layout:** Display ingested Gemini conversations as individual, easily digestible cards or list items within a scrollable container. The layout should be responsive and adapt seamlessly across different screen sizes.
    *   **Information per Entry:**
        *   **Title:** Prominently display the `title` of the Gemini conversation, acting as a primary identifier.
        *   **Content Snippet:** Show a truncated preview (e.g., the first 50-100 words) of the `content` to give a quick overview.
        *   **Timestamp:** Clearly indicate the `timestamp` of when the conversation was synced, helping with organization.
        *   **Source Icon/Link:** An unobtrusive icon (e.g., a link icon) that, when clicked, navigates to the `source_url` of the original Gemini conversation.
    *   **Interaction Elements:**
        *   **"View Details" Button:** A clear, modern button or interactive card area that, when clicked, expands to show the full Markdown `content` of the conversation in a modal dialog or a dedicated detail view. The content should be rendered using the app's consistent Markdown styling (as per the "AI Report Formatting Manifest" and custom CSS).
        *   **Global Status Indicator:** A persistent element (e.g., in a sidebar or header) displaying the total count of "Gemini Sources" currently stored (e.g., "52 Notes in Library"). This directly reflects the data provided by the backend's `/` endpoint.
    *   **Aesthetic Details:** Ensure smooth transitions and hover states for interactive elements. Use icons consistently from a modern icon library (e.g., Material Symbols or Font Awesome).

---

### 5. Antigravity Prompt for Backend "Librarian" Development

```
Initialize a Python FastAPI project for SynapseIP. I need a backend that runs locally on port 8000.

1.  **Database Setup:**
    *   Create a SQLite database using SQLAlchemy. The database file should be named `database.db`.
    *   Define a SQLAlchemy model for `GeminiSource` with the following schema:
        *   `id`: Primary key, integer.
        *   `title`: String, non-nullable (e.g., extracted from the first user prompt or a generated summary).
        *   `content`: Text (long string), non-nullable, stores the full Markdown content of the Gemini conversation.
        *   `timestamp`: DateTime, non-nullable, defaults to the current UTC time.
        *   `source_url`: String, nullable (URL of the original Gemini conversation).

2.  **API Endpoints:**
    *   **`POST /ingest` endpoint:**
        *   Accepts a JSON payload with `title`, `content`, `timestamp` (optional), and `source_url` (optional).
        *   Validates incoming data using Pydantic models.
        *   Saves the `title`, `content`, `timestamp`, and `source_url` into the `GeminiSource` table in the SQLite database.
        *   Returns a success message with the ID of the newly created entry.
    *   **`GET /` root endpoint:**
        *   Returns a simple JSON response indicating the API status (e.g., `{"status": "SynapseIP Backend is running"} `) and the current count of `GeminiSource` entries in the database (e.g., `{"total_sources": 0}`).

3.  **CORS Configuration:**
    *   Enable CORS for the FastAPI application to allow requests from any origin (`*`) during local development.

4.  **Local Execution:**
    *   Provide clear instructions in a `README.md` on how to install dependencies (`pip install -r requirements.txt`) and run the FastAPI server locally (`uvicorn main:app --host 0.0.0.0 --port 8000`).
    *   Ensure the project structure is clean and follows best practices for FastAPI applications.

5.  **Test Plan:**
    *   Include a basic `test_main.py` using `pytest` to test the `/` and `/ingest` endpoints. This should include tests for successful ingestion and proper data storage.
```

---

## 3. Chrome Extension "Messenger" Development (Gemini-specific)

# 3. Chrome Extension "Messenger" Development (Gemini-specific)

## 1. Feature Justification and Logic

This Chrome Extension serves as the crucial "Messenger" component for SynapseIP, automating the transfer of valuable Gemini conversations directly to the application. It acts as a bridge, eliminating manual data entry and ensuring a seamless flow of brainstorming notes into your robust document generation engine.

---

### Calculation/Logic

*   **Frictionless Data Ingestion:** The primary goal is to bypass the cumbersome copy-paste process for Gemini conversations, which is prone to errors and breaks the user's flow state.
*   **Targeted Scraping:** The extension specifically targets the `gemini.google.com` domain. It intelligently identifies and extracts the Markdown content from individual chat response bubbles.
*   **API Communication:** Once the relevant text is captured, the extension constructs a `POST` request containing this data. This request is then sent to a designated `/ingest` endpoint on your SynapseIP backend API (initially `http://localhost:8000/ingest`).
*   **Metadata Preservation:** Beyond just the raw text, the extension has the capability to extract and send valuable metadata, such as the conversation's timestamp, specific prompts, and originating URL, enriching the source material in SynapseIP.
*   **Security Bypass (Service Worker):** To operate efficiently during local development, the extension utilizes a Chrome Service Worker (background script). This is essential to circumvent "Mixed Content" security restrictions, allowing a secure HTTPS web page (Gemini) to communicate with your local HTTP API endpoint.

---

## 2. Expected Outcomes

### If it Works

*   **UI Integration:** A visually distinct "Sync to SynapseIP" or "Send to My App" button will appear directly next to each Gemini response bubble within the `gemini.google.com` interface.
*   **Successful Data Transfer:** Clicking this button will trigger the automatic scraping and transmission of the corresponding Gemini response to your SynapseIP backend.
*   **Backend Confirmation:** The logs of your running FastAPI server (`http://localhost:8000`) will display records of incoming `POST` requests to the `/ingest` endpoint. The server's status page (e.g., `/`) should reflect an increment in the number of stored "Gemini Sources."
*   **Extension Loading:** The Chrome Extension will load successfully in the `chrome://extensions` page without errors when "Developer Mode" is enabled and the `/extension` folder is loaded.

### If it Fails

*   **Missing UI:** The "Sync to SynapseIP" button will not appear on the Gemini chat page.
*   **Console Errors:** Attempting to click a non-existent button or if the script encounters issues will result in errors in the browser's developer console (e.g., "Mixed Content" warnings, network request failures, JavaScript execution errors).
*   **No Backend Activity:** Your SynapseIP backend logs will show no new incoming requests, and the database will remain unchanged, indicating a failure in data transmission.
*   **Extension Load Errors:** The extension may fail to load in `chrome://extensions`, displaying error messages related to `manifest.json` issues, script errors in `content.js` or `background.js`, or missing files.

---

## 3. User Interface (UI) Component for the Messenger

The Chrome Extension requires a beautiful, usable, and modern UI component to facilitate user interaction within the Gemini conversation interface.

### UI Component: "Sync to SynapseIP" Button

*   **Placement:** This button will be strategically injected next to *every* Gemini response bubble, close to existing interactive elements (e.g., Gemini's native "Copy" button) for intuitive discoverability.
*   **Visual Design:**
    *   **Icon:** A small, recognizable icon that denotes syncing or sending data (e.g., a cloud upload icon, an arrow pointing towards a document/database). This icon should be a modern SVG or high-resolution PNG for crispness.
    *   **Label:** Accompanying the icon, a concise text label: "Sync to SynapseIP" or "Send to My App." The text should use a sans-serif font, similar to Gemini's aesthetic, ensuring visual harmony.
    *   **Color Scheme:** The button's background and text colors should be subtle but visible against Gemini's theme (e.g., a light gray background with dark text, or a subtle brand accent color that doesn't clash with Google's UI).
    *   **Hover State:** A clear hover effect (e.g., slight background darkening, subtle icon animation) to indicate interactivity.
    *   **Active State:** A brief visual confirmation upon click (e.g., button briefly changes to a green checkmark or text changes to "Sent!") to provide immediate feedback to the user.
*   **Interactivity:** Clicking the button will instantly trigger the data scraping and API call, with a brief visual indicator of success or pending action.

---

## 4. Antigravity Build Prompt

To initiate the development of the Chrome Extension Messenger, use the following detailed prompt directly in your Antigravity Agent Manager:

```
"Antigravity, let's develop the Chrome Extension 'Messenger' for SynapseIP.

Here are the requirements:

1.  **Project Structure:** Create a Manifest V3 Chrome Extension within a new subfolder named `/extension`.
2.  **Target Domain:** The extension's content script should ONLY inject and run on `https://gemini.google.com/*`.
3.  **User Interface (UI):**
    *   Inject a small, elegant 'Sync to SynapseIP' button next to every Gemini AI response bubble.
    *   The button should be styled subtly to blend with Gemini's existing UI but clearly indicate its purpose. Use a cloud-upload icon and the text label 'Sync to SynapseIP'.
    *   Upon click, the button should provide immediate visual feedback (e.g., briefly change to a green checkmark or 'Sent!') to confirm the action.
4.  **Scraping Logic (Content Script):**
    *   The `content.js` script must identify the latest Gemini AI response bubble.
    *   Extract the full Markdown text content from this message bubble.
5.  **API Communication (Service Worker):**
    *   Utilize a `Service Worker` (background script) to handle the actual `fetch` request.
    *   This is crucial to bypass "Mixed Content" security blocks when sending data from `https://gemini.google.com` to my local API endpoint at `http://localhost:8000/ingest`.
    *   The `POST` request to `http://localhost:8000/ingest` should include the extracted chat text, along with any available metadata (e.g., timestamp, potentially the prompt text if accessible).
6.  **Deliverables:**
    *   Provide the `manifest.json`, `content.js`, and `background.js` files.
    *   Include clear instructions on how to 'Load Unpacked Extension' in Chrome Developer Mode for testing.
    *   Show me how to monitor the local FastAPI server logs to confirm successful data ingestion."
```

---

## 4. Core "Architect" Logic (Report Generation)

# SynapseIP: Core "Architect" Logic (Report Generation)

## 1. Feature Overview and Core Logic

The 'Core "Architect" Logic' is the central engine of SynapseIP, responsible for transforming raw, unstructured Gemini conversation notes into comprehensive, multi-page implementation plans or business reports. This feature moves beyond simple summarization, focusing on large-scale expansion, structured formatting, and intelligent content orchestration.

*   **Why it's Needed:**
    *   **Overcoming Limitations:** NotebookLM and similar tools have output length and style restrictions. SynapseIP specifically aims to generate unrestricted, long-form documents (upwards of 100+ pages) that are professionally formatted and logically coherent.
    *   **Strategic Expansion:** Gemini conversations, while excellent for brainstorming, lack the structure and detail required for a robust implementation plan or business report. This feature expands these core ideas into actionable, detailed documents.
    *   **Contextual Coherence:** Ensures that as the document grows, the AI maintains a consistent narrative and doesn't "forget" earlier sections, which is crucial for very long reports.

*   **Calculation/Logic:**
    *   **Multi-Agent Orchestration:** Antigravity agents are dispatched to specialized tasks in parallel:
        *   One agent: Generates a high-level outline (e.g., 20 chapters).
        *   Another agent: Drafts individual sections, performing "Deep Dives" to expand content based on source material.
        *   A third agent: Audits generated sections for business logic, factual accuracy, and cross-document consistency.
    *   **Retrieval-Augmented Generation (RAG) + Agentic Expansion:**
        *   **Vector Store:** Ingested Gemini notes are stored in a vector database, allowing the AI to efficiently retrieve only the most relevant information for each specific subsection it is currently generating, reducing token waste and improving accuracy.
        *   **Sectional Drafting ("Leaf" Generation):** The AI generates content one small, manageable "leaf" (subsection) at a time, ensuring detailed focus without exceeding context windows.
    *   **Recursive Expansion Loop:** Automates the sequential generation of chapters/sections. After one section is drafted, the process loops for the next, feeding in prior context and ensuring the report builds progressively.
    *   **Global Context Agent:** A "Super-Agent" continuously tracks the overall narrative flow and thematic consistency across the entire document, guiding individual drafting agents to prevent "AI drift" and maintain a unified tone.
    *   **Strict Formatting Manifest:** Imposes a mandatory Markdown structure (`##` for chapters, `###` for sections, etc.), table usage, list formatting, and tone guidelines to guarantee consistent visual and logical hierarchy throughout the report.
    *   **Document Stitching:** Python libraries (`python-docx` or `reportlab`) are used to combine the iteratively generated and validated Markdown sections into a single, cohesive `.docx` or `.pdf` file.

---

## 2. Step-by-Step Implementation Guide

### 2.1. Establish the Report Generation Endpoint

This step creates the primary entry point for triggering the report generation process within the SynapseIP application.

*   **Logic:**
    *   A new endpoint in the FastAPI backend will serve as the trigger for report generation.
    *   This endpoint will fetch all relevant "Gemini Sources" from the database.
    *   It will initiate the multi-agent workflow for outline creation and iterative content drafting.
    *   The endpoint will handle API key injection for Gemini from a secure `.env` file.
    *   It will ultimately return a download link for the final generated document.

*   **Antigravity Prompt:**
    ```
    "Add a new feature to the FastAPI backend.

    1.  Create a GET endpoint at `/generate-report`.
    2.  This endpoint should fetch ALL entries from the SQLite database that belong to a specific 'Project Bucket' (initially, assume all entries are part of one bucket).
    3.  Configure the endpoint to securely access the Gemini 1.5 Pro API using an API key from a `.env` file.
    4.  The initial output should be a placeholder JSON response indicating 'Report generation initiated, check back in 5 minutes for a download link.'
    5.  Ensure CORS is configured to allow requests from the React frontend."
    ```

*   **Expected Outcome:**
    *   **Works:** You will be able to access `http://localhost:8000/generate-report` (or your deployed URL), and it will return a message like `{"status": "Report generation initiated, check back in 5 minutes for a download link."}`. The FastAPI server logs should show the endpoint being hit.
    *   **Fails:** You might receive a `404 Not Found` error if the endpoint isn't correctly registered, or a `500 Internal Server Error` if there are issues with database connection or `.env` file access. CORS errors will appear in your browser console if not correctly configured.

---

### 2.2. Implement Iterative Content Generation

This is the core "Architect" logic that builds the extensive document section by section, maintaining quality and context.

*   **Logic:**
    *   The `/generate-report` endpoint logic will be expanded to orchestrate a multi-step workflow.
    *   **Step 1: Outline Generation:** An initial Gemini API call creates a detailed 20-chapter outline based on *all* ingested notes. This outline will be stored as an intermediate artifact.
    *   **Step 2: Iterative Chapter/Section Expansion:** A loop will iterate through the generated outline. For each chapter/section:
        *   Relevant notes are retrieved from the vector store (if implemented, otherwise from the main database).
        *   A focused Gemini API call is made, specifically prompted to expand *only* that chapter/section into 4-5 pages of content.
        *   A "Global Context Agent" (can be a persistent prompt or an initial summary fed into each subsequent call) is used to maintain overarching narrative consistency.
        *   An auditing step (simple verification or a separate agent) might cross-reference generated content with previous sections to prevent contradictions.
    *   **Constraint:** Crucially, the AI is instructed *not* to attempt to generate the entire 100+ page document in a single API call to prevent timeouts, token limits, and "AI drift."

*   **Antigravity Prompt:**
    ```
    "Modify the FastAPI `/generate-report` endpoint.

    1.  First, use the Gemini 1.5 Pro API to generate a 20-chapter outline for a comprehensive implementation plan/business report based on all 'Gemini Sources' in the database. Store this outline as a temporary JSON artifact.
    2.  Implement an 'Iterative Loop': For each chapter in the generated outline:
        a.  Fetch relevant 'Gemini Sources' for that chapter.
        b.  Call the Gemini 1.5 Pro API to expand that specific chapter into 4-5 pages of professional content.
        c.  Crucially, inject previous chapter summaries (or a 'Global Narrative' summary) into the prompt for the current chapter to maintain consistency.
        d.  Store each expanded chapter's raw Markdown content as a separate temporary artifact.
    3.  Include the 'GrandDraft Formatting Manifest' (provided below) as part of the system instructions for *every* Gemini API call during content generation to ensure strict adherence.

    GrandDraft Formatting Manifest:
    Strict Formatting Rules:
    1.  Use `#` ONLY for the Title of the entire document.
    2.  Use `##` for Chapter Titles.
    3.  Use `###` for all Sub-headers.
    4.  Use `---` (horizontal rules) to separate distinct logic blocks.
    5.  All data points MUST be in a bulleted list (`*`) or a Markdown table.
    6.  DO NOT use bolding (`**`) for headers; use the appropriate `#` tag.
    "
    ```

*   **Expected Outcome:**
    *   **Works:** The backend logs will show multiple, sequential Gemini API calls. Intermediate files/artifacts (e.g., outline JSON, individual Markdown chapter files) will be created. The final output, though unstitched, will be several Markdown files each containing 4-5 pages of content. No API timeouts or large token limit errors.
    *   **Fails:** Frequent API timeouts or `429 Too Many Requests` errors if the iterative loop is too aggressive or not properly rate-limited. Inconsistent formatting between chapters, or "AI talk" (e.g., "Here is Chapter X") will indicate the formatting manifest wasn't strictly enforced. Logical contradictions between chapters will suggest the "Global Context Agent" or auditing step is insufficient.

---

### 2.3. Enforce Document Formatting Consistency

Ensures the generated report adheres to a predefined professional style and structure.

*   **Logic:**
    *   The "GrandDraft Formatting Manifest" (detailed below) is embedded directly into the system instructions for every Gemini API call during content generation. This forces the AI to produce Markdown that is structurally predictable.
    *   **App-Controlled Headers:** Instead of relying on the AI to place primary headers, the application code (Python backend) will programmatically insert the `## Chapter Title` and `---` (horizontal rule for page break) before handing off to the AI to fill in the *body* content of that section. This guarantees consistent hierarchy.
    *   **Markdown to HTML to CSS:** The generated Markdown from the AI will be processed by a Markdown parser in the frontend, converting it into standard HTML elements (`h1`, `h2`, `p`, `ul`, `table`). A dedicated CSS file then styles these HTML elements to achieve a consistent, modern visual appearance.

*   **Antigravity Prompt (This is part of the previous prompt, but here's how to emphasize it for consistency):**
    ```
    "Refine the iterative content generation in the `/generate-report` endpoint.

    1.  Ensure the 'GrandDraft Formatting Manifest' is explicitly included as system instructions for *every* Gemini API call that generates content (not just outlines).
    2.  Modify the logic so that the FastAPI backend ITSELF (not Gemini) prefixes each generated chapter's content with its `## Chapter Title` and a `---` horizontal rule, before sending the content to the Gemini API for expansion. This prevents AI drift on main headers.
    3.  Verify that Gemini strictly uses `###` for sub-headers, `####` for sub-points, bulleted lists (`*`), and Markdown tables for data.
    4.  Ensure Gemini avoids "AI Talk" and uses `**Bold**` only for key terms, not entire sentences.
    5.  For any mathematical or technical formulas, instruct Gemini to wrap them in `$math$` for LaTeX compatibility."
    ```
    **GrandDraft Formatting Manifest (to be included in prompt as System Instructions):**
    *   **Document Hierarchy (The Skeleton):**
        *   L1 - Document Title (`#`): Used exactly **once** at the very beginning of the entire report.
        *   L2 - Chapter Titles (`##`): Used for the 20+ main chapters. Each Chapter Title must be preceded by a Horizontal Rule (`---`) to trigger a page break in your PDF generator.
        *   L3 - Section Headers (`###`): Used for thematic breaks within a chapter.
        *   L4 - Sub-points (`####`): Used only for specific data groupings or "Deep Dive" callouts.
    *   **Standardized Components:**
        *   Tables: Any comparison, financial projection, or timeline **must** be formatted in a Markdown table.
            *   Constraint: No more than 5 columns to ensure it fits on a standard A4 PDF page.
        *   Blockquotes (`>`): Used exclusively for **Executive Summaries** at the start of each chapter and **Key Takeaways** at the end.
        *   Lists: Use bullet points (`*`) for non-sequential items and numbered lists (`1.`) for step-by-step instructions or priorities.
    *   **Typography & Tone:**
        *   Boldness: Use `**Bold**` only for key terms or the first mention of a technical concept. Do not bold entire sentences.
        *   No "AI Talk": Prohibit phrases like "Sure, here is chapter 5" or "In conclusion." The output must be the **raw content** only.
        *   LaTeX for Math: All financial formulas or technical metrics must be wrapped in `$math$` for professional rendering.

*   **Expected Outcome:**
    *   **Works:** All generated Markdown chapters will consistently use `##`, `###`, `####`, `---`, bullet points, and tables as defined. There will be no instances of AI-generated top-level headers or conversational filler. The structure will be predictable and clean.
    *   **Fails:** Inconsistent use of header levels (`##` vs `###`), improper table or list formatting, unexpected bolding patterns, or inclusion of "AI talk" will indicate a failure to adhere to the manifest. This will require further prompt engineering to reinforce the rules.

---

### 2.4. Final Document Assembly and Export

This step combines all generated content and presents it to the user.

*   **Logic:**
    *   After all iterative content generation is complete, the backend collects all individual Markdown chapter artifacts.
    *   These Markdown files are concatenated into a single, master Markdown document.
    *   A document generation library (`python-docx` for Word or `reportlab` for PDF) is used to convert this master Markdown into a professionally formatted output file (`.docx` or `.pdf`).
    *   The `---` (horizontal rule) markdown element, strategically placed between chapters, will trigger page breaks in the PDF/DOCX generation process.
    *   The generated file is saved temporarily on the server or uploaded to Vercel Blob storage (if deployed to Vercel).
    *   A secure, temporary download link for the final document is generated and returned to the user.

*   **Antigravity Prompt:**
    ```
    "Finalize the `/generate-report` endpoint.

    1.  After all chapters are generated, combine all individual Markdown chapter files into a single master Markdown document.
    2.  Use `python-docx` to convert this master Markdown document into a single, professionally formatted `.docx` file. Ensure that the `---` horizontal rules in the Markdown are interpreted as page breaks in the Word document.
    3.  Implement a mechanism to save the final `.docx` file to a temporary location on the server (or Vercel Blob storage if available).
    4.  Generate a secure, temporary, and expiring download link for this `.docx` file.
    5.  Return this download link in the final JSON response of the `/generate-report` endpoint."
    ```

*   **Expected Outcome:**
    *   **Works:** The API call to `/generate-report` will eventually return a JSON object containing a `download_link` field. Clicking this link will initiate the download of a multi-page (e.g., 100+ pages) `.docx` or `.pdf` document that is correctly formatted, with each chapter starting on a new page.
    *   **Fails:** The API call may time out if document assembly is too slow (especially on serverless functions like Vercel with strict timeout limits, e.g., 300s). The download link might be invalid or expire prematurely. The downloaded document might be unformatted, corrupted, or not contain all generated content if the stitching process fails.

---

## 3. User Interface (UI) Component for Report Generation

A beautiful, usable, and modern UI is critical for triggering the complex "Architect" logic and presenting its powerful output.

*   **Why UI is Needed:**
    *   **Initiation:** Provides a clear, intuitive way for the user to start the intensive report generation process.
    *   **Feedback & Transparency:** Long-form generation takes time. The UI needs to show progress and intermediate "artifacts" (like the generated outline) to keep the user informed and engaged, allowing for potential course correction.
    *   **Accessibility of Output:** Presents the final, valuable report in an easily accessible and manageable format, with direct download options.

*   **UI Component Description:**

    1.  **Report Generation Card/Panel:**
        *   **Appearance:** A clean, minimalist card or panel on the SynapseIP dashboard, prominently featuring the report generation function. It should use modern design principles (e.g., Material Design, Fluent UI) with subtle shadows, rounded corners, and a clear call to action.
        *   **Elements:**
            *   **Report Title Input:** A clear text input field for the user to name their report (e.g., "MVP Implementation Plan for SynapseIP").
            *   **Project Bucket Selector (Optional MVP extension):** A dropdown or selection component if the user has multiple collections of Gemini notes, allowing them to choose which "Project Bucket" to use as source material. For MVP, this might just be "All synced notes."
            *   **"Generate Report" Button:** A prominent, styled button (e.g., `primary` color, animated on click) that triggers the `/generate-report` API endpoint.

    2.  **Report Generation Progress Modal/Drawer:**
        *   **Appearance:** Upon clicking "Generate Report," a non-blocking modal or a sliding drawer should appear, providing real-time feedback. It should have a professional, calm aesthetic.
        *   **Elements:**
            *   **Status Indicator:** A clear message (e.g., "Generating Outline...", "Drafting Chapter 3: Backend Architecture...") updated dynamically.
            *   **Progress Bar:** A smooth, animated progress bar (linear or circular) indicating the overall completion percentage of the report generation.
            *   **Intermediate Artifact Display (Artifact-Driven Development):**
                *   Once the outline is generated (Step 2.2), it could be displayed within this modal/drawer as a collapsible list (e.g., "Outline Ready for Review"). The user could potentially click to expand and review the outline. For MVP, this could be a static display; future iterations could allow comments or edits.
                *   As chapters are drafted, optional "Live Preview" snippets (or just chapter titles being marked as "Complete") could appear.
            *   **Cancel Button:** A clearly visible "Cancel" button to stop the generation process if needed.

    3.  **Generated Report Viewer & Download:**
        *   **Appearance:** Once generation is complete, the progress modal transitions to a success state, or a new section on the dashboard becomes active. This area should provide options to interact with the finished report.
        *   **Elements:**
            *   **Success Message:** "Your 100-page SynapseIP Implementation Plan is Ready!"
            *   **"View Report" Button:** Opens an in-app viewer (a simple iframe displaying the PDF, or a Markdown renderer for the docx converted to HTML) for quick review.
            *   **"Download Report (.docx)" Button:** A prominent button linked directly to the generated download URL, allowing the user to save the document.
            *   **"Download Report (.pdf)" Button (Optional/Future):** If PDF generation is also implemented.

*   **Antigravity Prompt for UI:**
    ```
    "For the SynapseIP React frontend, create a modern and usable UI component for the 'Report Generation' feature.

    1.  Design a 'Report Generation Card' on the main dashboard with:
        a.  A `Report Title` input field (modern text input).
        b.  A prominent `Generate Report` button (primary color, with a subtle hover effect).
    2.  Upon clicking 'Generate Report', open a full-screen `Report Progress Modal` that includes:
        a.  A dynamic `Status Message` (e.g., "Generating outline...", "Drafting Chapter X...").
        b.  A smooth, animated `Linear Progress Bar` indicating overall progress.
        c.  A collapsible section to display the `Generated Outline` (as a bulleted list).
        d.  A `Cancel Generation` button.
    3.  Once the report is complete, the modal should update to a `Report Complete` state, showing:
        a.  A clear `Success Message`.
        b.  A `Download Report (.docx)` button, linked to the API's provided download URL.

    Ensure all components are visually appealing, using clean typography, modern icons, and a consistent color palette, optimized for a vibe coding environment."
    ```

---

## 4. Expected Outcomes: Success and Failure

### 4.1. What to Expect if it Works

Upon successful execution of the 'Core "Architect" Logic (Report Generation)' feature:

*   **Backend & System Side:**
    *   The `/generate-report` endpoint will respond with a `200 OK` status and a JSON payload containing a secure, time-limited download URL for the generated document.
    *   Backend logs will show a sequence of Gemini API calls for outline generation, iterative chapter drafting, and content auditing, without errors or timeouts.
    *   Temporary intermediate files (e.g., chapter Markdown files) will be created and properly cleaned up or moved to durable storage (e.g., Vercel Blob) after final assembly.
    *   The backend will successfully integrate with `python-docx` (or `reportlab`) to stitch the Markdown content into a single, cohesive `.docx` (or `.pdf`) file.

*   **User Interface (UI) Side:**
    *   The user will click the "Generate Report" button.
    *   A "Report Progress Modal" will appear, displaying live status updates (e.g., "Generating Outline," "Drafting Chapter 1 of 20," "Auditing content...").
    *   The progress bar will smoothly advance from 0% to 100%.
    *   Upon completion, the modal will transform to a "Report Complete" state, displaying a clear success message.
    *   A prominent "Download Report (.docx)" button will be active, allowing the user to retrieve their document.
    *   The downloaded document will be a multi-page (e.g., 100+ pages) `.docx` file, opening correctly in standard word processors.
    *   **Document Content & Formatting:**
        *   The report will feature a consistent hierarchy (`#` for main title, `##` for chapters, `###` for sections, `####` for sub-points) and structured data (bulleted lists, tables).
        *   Each chapter will correctly start on a new page, thanks to the `---` horizontal rule interpretation.
        *   The content will be rich, detailed, and directly expanded from the ingested Gemini notes, providing a comprehensive implementation plan.
        *   The tone will be professional and devoid of conversational AI phrasing.
        *   Factual accuracy will be high, with minimal to no hallucination, reflecting successful RAG and auditing.

### 4.2. What to Expect if it Fails

If the 'Core "Architect" Logic' encounters issues during generation:

*   **Backend & System Side:**
    *   **API Timeouts:** The `/generate-report` endpoint might return a `504 Gateway Timeout` (especially on serverless platforms like Vercel with execution limits) if a single generation step or the overall process takes too long.
    *   **Gemini API Errors:** `429 Too Many Requests` if rate limits are hit, or `500 Internal Server Error` if the Gemini API itself fails or returns malformed responses.
    *   **Document Generation Library Errors:** The `python-docx` or `reportlab` library might fail to process the concatenated Markdown, resulting in a corrupted or empty file, or a `500 Internal Server Error` from the backend.
    *   **Database/Storage Issues:** Failure to read source notes from the database, or failure to write the final document to temporary storage/Vercel Blob.

*   **User Interface (UI) Side:**
    *   The "Report Progress Modal" might freeze, display an "Error" status, or unexpectedly close.
    *   The progress bar might get stuck or reset.
    *   The "Download Report" button might remain disabled, or if active, clicking it leads to a corrupted, empty, or non-existent file download.
    *   **Document Content & Formatting:**
        *   **"AI Drift":** Inconsistent formatting (e.g., headers switching between `##` and `**bold**`), varying levels of detail between chapters, or repetitive content, indicating a failure to enforce the formatting manifest or maintain global context.
        *   **Hallucinations/Inaccuracies:** The generated report contains information not present in the source notes or presents logically contradictory statements, suggesting a breakdown in the RAG or auditing process.
        *   **Incomplete Report:** The generated document is significantly shorter than expected or abruptly cuts off mid-chapter, indicating a failure in the iterative loop.
        *   **"AI Talk":** The report includes conversational AI filler (e.g., "Here is the introduction to chapter 1..."), signifying the prompt constraints were not strict enough.

---

## 5. Initial Deployment & Testing

# 5. Initial Deployment & Testing

## Feature Purpose & Logic

This phase is critical for validating the core components of SynapseIP: the communication bridge between the Gemini conversation extension and the backend API, and the initial functionality of the document generation engine.

*   **Why it's needed:** Before investing further development into complex features like multi-agent orchestration or advanced formatting, it's essential to confirm that the fundamental data flow—from Gemini chat to your app's database, and from the database to an initial generated report—is stable and operational. This prevents cascading errors and streamlines debugging.
*   **Calculation/Logic:**
    *   The Chrome Extension scrapes Gemini chat content and sends it via an HTTP `POST` request to a designated `/ingest` endpoint on the SynapseIP backend.
    *   The backend API receives this data, stores it in a local database, and provides a status endpoint for verification.
    *   A separate backend endpoint triggers the Gemini API to process stored notes and generate a preliminary report.

---

## Step-by-Step Logic Guide

### 1. Backend Local Deployment (The "Librarian")

This step deploys your FastAPI backend locally, creating a "mailbox" ready to receive Gemini chat data.

*   **Action:**
    1.  Open your Antigravity Agent Manager and select your SynapseIP project.
    2.  Provide Antigravity with the prompt below to initialize and run the FastAPI backend locally.
*   **Antigravity Prompt:**
    ```
    "Initialize a Python FastAPI project. I need a backend that runs locally on port 8000.
    1. Create a SQLite database using SQLAlchemy to store 'Gemini Sources'.
    2. The schema should include: `id`, `title`, `content` (long text), `timestamp`, and `source_url`.
    3. Create a POST endpoint at `/ingest` that accepts JSON and saves it to the DB.
    4. Ensure CORS is enabled so a Chrome Extension can talk to it from a different origin.
    5. Provide a simple 'Status' page at the root `/` that shows how many items are currently in the database."
    ```
*   **Expectation if it works:**
    *   Antigravity will generate project files (`app/main.py`, `requirements.txt`).
    *   It will automatically attempt to install dependencies and start the FastAPI server, usually accessible at `http://127.0.0.1:8000`.
    *   Navigating to `http://127.0.0.1:8000/` in your browser should show a "Status" page with a count of 0 items in the database.
*   **Expectation if it fails:**
    *   Antigravity will report errors during dependency installation or server startup. Check for port conflicts or Python environment issues.
    *   The `http://127.0.0.1:8000/` URL will be unreachable or show a connection error.

---

### 2. Chrome Extension Local Deployment (The "Messenger" UI)

This step deploys your Chrome Extension locally, allowing it to interact with the Gemini web interface and send data to your backend.

*   **Action:**
    1.  Provide Antigravity with the prompt below to create the extension code.
    2.  Follow Antigravity's instructions (or the steps below) to load the unpacked extension in Chrome.
*   **Antigravity Prompt:**
    ```
    "Create a Manifest V3 Chrome Extension in a subfolder called `/extension`.
    1. It should only run on `https://gemini.google.com/*`.
    2. Use a **Content Script** to inject a small 'Sync to SynapseIP' button next to every Gemini response bubble.
    3. Use a **Service Worker (Background Script)** to handle the actual `fetch` request to `http://localhost:8000/ingest`. This is important to avoid 'Mixed Content' security blocks.
    4. When the button is clicked, it should grab the Markdown text from the message bubble and send it to the backend."
    ```

#### UI Component Design: "Sync to SynapseIP" Button

*   **Component Type:** Inline action button within the Gemini chat interface.
*   **Placement:** Positioned next to or below each individual Gemini AI response bubble, ideally near existing "Copy" or "Share" options.
*   **Visual Style:**
    *   **Button Text:** "Sync to SynapseIP"
    *   **Icon:** A small, modern sync/refresh icon or a distinctive SynapseIP logo (if available).
    *   **Aesthetics:** Should subtly blend with the Gemini UI's clean, minimalist design, using a neutral background (e.g., light gray, white) with a soft blue or purple accent color for hover/active states, mirroring Gemini's brand palette. Rounded corners, subtle shadow on hover.
    *   **Usability:** Clearly visible on hover. Provides immediate feedback upon click (e.g., a temporary "Synced!" message or a spinner).
*   **Interaction:** Clicking the button extracts the Markdown content of the *specific* Gemini response it's attached to and sends it to the running local API.

*   **Loading the Extension:**
    1.  Open your Chrome Browser and navigate to `chrome://extensions`.
    2.  Toggle "Developer mode" ON (usually in the top right corner).
    3.  Click the "Load unpacked" button.
    4.  Navigate to and select the `/extension` folder that Antigravity created.
    5.  Refresh any open Gemini tabs (or open `https://gemini.google.com`).
*   **Expectation if it works:**
    *   The extension icon will appear in your browser's toolbar.
    *   On `gemini.google.com`, a "Sync to SynapseIP" button will appear next to each AI response.
*   **Expectation if it fails:**
    *   Chrome will show an error message during "Load unpacked" (e.g., `Manifest file is missing or unreadable`).
    *   The button will not appear on Gemini pages.

---

### 3. Testing the "Bridge" (Extension to Backend)

This step verifies that your Chrome Extension can successfully send data to your local FastAPI backend.

*   **Action:**
    1.  Ensure your FastAPI server is running (from Step 1).
    2.  Ensure your Chrome Extension is loaded (from Step 2) and you are on `gemini.google.com`.
    3.  Click the "Sync to SynapseIP" button next to a Gemini AI response.
    4.  **Prompt Antigravity to check server logs:**
        ```
        "Help me test the connection. Open the logs for the FastAPI server and tell me if you see any incoming data when I click the sync button on Gemini. Also, check the `/` status page."
        ```
*   **Expectation if it works:**
    *   Antigravity's output will show server logs indicating a successful `POST` request to `/ingest` with the Gemini chat content.
    *   The status page at `http://127.0.0.1:8000/` will show the item count incrementing (e.g., from 0 to 1).
*   **Expectation if it fails:**
    *   Antigravity will show connection errors in the server logs (e.g., `CORS policy blocked request`, `Connection refused`).
    *   The status page will remain at 0 items.
    *   Check Chrome's Developer Tools console for the extension or Gemini page for JavaScript errors (`F12` -> Console tab).

---

### 4. Initial Report Generation & Output Testing

This step performs a basic test of your backend's ability to trigger Gemini and generate a document from the synced notes.

*   **Action:**
    1.  Ensure you have synced at least one Gemini conversation using the extension.
    2.  Provide Antigravity with the prompt below to add and test the report generation endpoint.
*   **Antigravity Prompt:**
    ```
    "Add a new feature to the FastAPI backend.
    1. Create a GET endpoint at `/generate-report`.
    2. This endpoint should fetch ALL entries from the SQLite database.
    3. Use the **Gemini 1.5 Pro API** (I will provide my API key in a `.env` file) to:
       a. Create a coherent 20-chapter outline based on the gathered notes.
       b. For each chapter, perform a 'Deep Dive' expansion to generate 4-5 pages of professional business content.
    4. Use the `python-docx` or `reportlab` library to stitch these into one long document.
    5. Provide a download link for the final `.docx` or `.pdf` file.
    6. When generating the report, use an **Iterative Loop**. Do not try to write the whole 100 pages in one API call. Instead, have the agent write one chapter at a time, verify the quality, save it, and then move to the next chapter. This ensures the 100th page is as good as the 1st.
    7. **MANDATORY FORMATTING:**
       *   Use `#` ONLY for the Title of the entire document.
       *   Use `##` for Chapter Titles.
       *   Use `###` for all Sub-headers.
       *   Use `---` (horizontal rules) to separate distinct logic blocks.
       *   All data points MUST be in a bulleted list (`*`) or a Markdown table.
       *   DO NOT use bolding (`**`) for headers; use the appropriate `#` tag."
    ```
*   **Expectation if it works:**
    *   Antigravity will modify your backend code to include the `/generate-report` endpoint.
    *   Calling this endpoint (e.g., via a browser or `curl`) will trigger the report generation process.
    *   After a processing period, the API will return a download link for the generated `.docx` or `.pdf` file.
    *   The downloaded document will reflect the content from your synced Gemini notes, adhering to the specified formatting rules for headers, lists, and tables.
*   **Expectation if it fails:**
    *   The API call to `/generate-report` will return an error (e.g., `Gemini API key missing`, `Timeout`, `Database error`, `Document generation library error`).
    *   The generated document will be empty, corrupted, or not adhere to the formatting rules, indicating issues with the API integration or prompt engineering.

---

## 6. UI for Report Interaction & Display

# 6. UI for Report Interaction & Display

### 1. Feature Necessity & Logic

This feature is critical for SynapseIP as it provides the user interface to interact with, view, and ultimately consume the generated long-form reports. Without a robust UI for display, the core value proposition of transforming brainstorming notes into comprehensive documents remains inaccessible.

**Necessity:**
*   Users need a dedicated area within the SynapseIP application to view their generated reports.
*   A consistent, professional display ensures readability and reinforces the value of the AI-generated content.
*   Clear interactive elements are required for initiating report generation and downloading the final document.
*   The UI must clearly differentiate between available report options (e.g., 5-page summaries vs. 100+ page whitepapers), potentially tied to monetization tiers.

**Calculation/Logic:**
1.  **Report Generation Trigger:** The UI initiates a call to the backend FastAPI `/generate-report` endpoint, potentially passing parameters like desired length or template.
2.  **Markdown Ingestion & Parsing:** The backend returns the report content as raw Markdown text, adhering to the predefined "GrandDraft Formatting Manifest." The frontend (built with React) uses a Markdown parsing library (e.g., `react-markdown`) to convert this raw Markdown into structured HTML.
3.  **Dynamic Styling with CSS:** A dedicated CSS stylesheet (`ReportDisplay.css` or `ChatResponse.css`) is applied to the parsed HTML. This CSS ensures consistent visual presentation of all elements (headers, paragraphs, lists, tables, blockquotes) according to the app's design language, mimicking a "Gemini Theme" or a "Professional Business Plan" aesthetic.
4.  **Print & Export Optimization:** Media queries within the CSS (`@media print`) are used to define specific styles for printing or PDF conversion, enforcing page breaks before new chapters and preventing tables from splitting across pages.
5.  **Download Mechanism:** Upon successful generation, the UI displays a secure download link for the `.docx` or `.pdf` file (which is stored on Vercel Blob or a similar cloud storage), rather than directly receiving the large file to avoid frontend payload limits.
6.  **User State & Actions:** The UI must display the user's "Saved Gemini Chats" (source material) and provide clear buttons to initiate report generation. It should also indicate the user's credit balance or subscription tier, gating access to certain report lengths or types.

---

### 2. Expected Outcomes

*   **Success Criteria:**
    *   The user navigates to a "Reports Dashboard" within SynapseIP.
    *   They can view a list of their previously generated reports and synced Gemini chats.
    *   Clicking a report or selecting chats allows them to trigger generation (e.g., via an "Expand to 100-Page Plan" button) or view an existing report.
    *   Generated reports are displayed within a dedicated "Report Viewer" area, featuring consistent typography, spacing, and element styling (e.g., bold dark gray headers, styled code blocks, bordered blockquotes).
    *   Horizontal rules (`---`) visibly delineate major sections or chapters within the displayed report, correctly triggering page breaks in printed/downloaded versions.
    *   A prominent "Download Report" button or link appears, providing the user with a `.docx` or `.pdf` file of the fully formatted report, which includes proper pagination, table integrity, and consistent styling.
    *   The UI clearly communicates the cost in "credits" for generating reports of different lengths/types.

*   **Failure States:**
    *   **Inconsistent Formatting:** Reports display with varying header sizes, font styles, or inconsistent use of bolding, indicating that the AI did not adhere to the "Formatting Manifest" or the CSS styling is insufficient.
    *   **Poor Readability:** Text overflows containers, tables are unaligned, or code blocks are unstyled, making the report difficult to read.
    *   **Broken Downloads:** Clicking "Download Report" results in an error, a corrupted file, or a file that lacks the expected formatting due to backend issues (e.g., Vercel payload limits, incorrect `python-docx` usage).
    *   **Structural Drift:** Chapters or sections do not start on new pages, or hierarchical headings are incorrectly nested, making the report appear unstructured.
    *   **Missing Data:** Synced Gemini chats are not visible, or the "Generate Report" button is missing or unresponsive, preventing user interaction.

---

### 3. UI Component Instructions: The SynapseIP Report Dashboard & Viewer

The primary UI component for this feature is a **Report Dashboard** combined with an integrated **Report Viewer**. This needs to be a modern, intuitive, and responsive interface built within the React frontend of SynapseIP.

**Component: `ReportDashboard`**

*   **Purpose:** To serve as the central hub for managing synced Gemini conversations and generated reports.
*   **Layout:**
    *   A clean, two-column layout:
        *   **Left Column (`SavedChatsList`):** Displays a scrollable list of all synced Gemini conversations. Each item should show the chat's title, a brief snippet, and the sync timestamp. A checkbox or selection mechanism allows users to select one or multiple chats as source material for a new report.
        *   **Right Column (`ReportActions & Viewer`):**
            *   **Header Area:** "Generate New Report" or "View Report Details".
            *   **Call to Action:** A prominent, visually distinct button: "Generate [X-Page] Report" or "Expand to 100-Page Plan" (dynamically updating based on selected chats and user tier/credits).
            *   **Credit/Tier Display:** A small, persistent display showing the user's current credit balance or subscription tier, located near the generate button.
            *   **`ReportViewer` Area:** This is where the generated or selected existing report content will be displayed. It should occupy the majority of the right column below the action buttons.
            *   **`DownloadReport` Button:** A clear button (e.g., "Download PDF" / "Download DOCX") appearing after a report has been generated or selected.

**Component: `ReportViewer`** (nested within `ReportDashboard`)

*   **Purpose:** To render the Markdown content of reports into beautiful, consistent HTML.
*   **Technology:** Utilize the `react-markdown` library for parsing.
*   **Styling (`ReportDisplay.css` / `ChatResponse.css`):**
    *   **Typography:** Use a professional, readable sans-serif font (e.g., 'Inter', 'Roboto').
    *   **Headers (`h1`, `h2`, `h3`, `h4`):**
        *   `h1`: Document Title, large, bold, centered, perhaps with a subtle accent color.
        *   `h2`: Chapter Titles, bold, dark gray/blue, slightly smaller than h1, with a thin bottom border.
        *   `h3`: Section Headers, bold, dark gray, smaller than h2.
        *   `h4`: Sub-points, bold, slightly smaller, also dark gray.
    *   **Paragraphs (`p`):** Clear line-height (e.g., 1.6), legible text color (#3c4043).
    *   **Lists (`ul`, `ol`):** Standard bullet/numbered styling, with appropriate indentation.
    *   **Tables:** Full-width, clean borders (`1px solid #ccc`), alternating row colors for readability.
    *   **Blockquotes (`blockquote`):** Indented, with a light-gray background and a distinct vertical border on the left side (e.g., 4px solid #e0e0e0) for highlighting executive summaries or key takeaways.
    *   **Code Blocks (`pre`):** Dark background, rounded corners, monospaced font, light text color.
    *   **Horizontal Rules (`hr`):** Thin, subtle line (`---`) to visually separate logic blocks and trigger page breaks in print view.
    *   **Responsive Design:** The layout must adapt gracefully to different screen sizes (desktop, tablet, mobile).

---

### 4. Antigravity Designer Prompt

```
Antigravity, I need to build the 'UI for Report Interaction & Display' feature for the SynapseIP React frontend. This involves a central dashboard where users can manage their raw Gemini chats and view/generate comprehensive reports.

Here are the step-by-step instructions for the UI components and their logic:

1.  **Create a `ReportDashboard` React Component:**
    *   Implement a two-column layout.
    *   **Left Column (`SavedChatsList.jsx`):**
        *   Display a scrollable list of "Saved Gemini Chats" fetched from the FastAPI backend (e.g., `/api/chats`).
        *   Each list item should show `chat.title`, `chat.timestamp`, and a small snippet of `chat.content`.
        *   Include a mechanism (checkboxes or radio buttons) for users to select one or multiple chats as source material.
        *   Design it to be visually appealing, clean, and modern.
    *   **Right Column (`ReportActions & Viewer`):**
        *   Include a dynamic header, e.g., "Generate New Report" or "Viewing: [Report Title]".
        *   Create a prominent button `GenerateReportButton.jsx` that, when clicked, triggers a POST request to `/api/generate-report` with the IDs of selected chats and desired report parameters (e.g., `length: '100-pages'`). This button should visually differentiate between report types (e.g., "Generate 5-page Summary", "Generate 100-page Whitepaper").
        *   Add a small display component `CreditBalance.jsx` showing the user's available "credits" or current "tier" (mock data for now).
        *   Integrate a nested `ReportViewer` component (see below) to display the generated report content or a selected historical report.
        *   Add a `DownloadReportButton.jsx` that appears when a report is displayed in the `ReportViewer`. This button should initiate a download from a provided URL (e.g., `/api/reports/{report_id}/download`).

2.  **Create a `ReportViewer` React Component (`ReportViewer.jsx`):**
    *   This component will receive Markdown content as a prop.
    *   Integrate the `react-markdown` library to parse the incoming Markdown into HTML.
    *   Apply a dedicated CSS stylesheet (`ReportViewer.css`) to this component, ensuring it styles the generated HTML (h1, h2, h3, h4, p, ul, ol, table, blockquote, pre, hr) according to a professional "Gemini-inspired" theme:
        *   `h1, h2, h3, h4`: Bold, dark gray (#3c4043) for titles. `h2` should have a subtle blue accent and a thin bottom border.
        *   `p`: Line-height 1.6, color #3c4043.
        *   `pre` (code blocks): Dark background, rounded corners, monospaced font.
        *   `blockquote`: Light-gray background, left vertical border (4px solid #e0e0e0), italic text.
        *   `table`: Full width, subtle borders, easily readable.
        *   `hr` (horizontal rule): A thin, light gray line.

3.  **Implement Strict Formatting Adherence (within `ReportViewer.jsx` context):**
    *   Ensure that the `react-markdown` renderer is configured to correctly interpret the strict Markdown rules:
        *   `#` for the entire document title (used once).
        *   `##` for Chapter Titles (preceded by `---` for page breaks).
        *   `###` for Section Headers.
        *   `####` for Sub-points.
        *   `---` for horizontal rules.
        *   All data points rendered either as bulleted lists (`*`) or Markdown tables.
        *   No bolding (`**`) for headers; only `#` tags.

4.  **Add Print-Specific CSS:**
    *   Include `@media print` rules in `ReportViewer.css` to ensure optimal PDF/print output:
        *   `h2`: `page-break-before: always;` (to ensure each chapter starts on a new page).
        *   `table`: `page-break-inside: avoid;` (to prevent tables from splitting across pages).
        *   Adjust font sizes and margins for print if necessary (e.g., `font-size: 12pt` for body text).

5.  **Develop Backend Endpoint for Report Content (`/api/reports/{report_id}`):**
    *   Create a FastAPI GET endpoint that retrieves a specific report's Markdown content from the database and returns it.

**Visual Aesthetic Guidelines for the Designer:**
*   **Modern & Clean:** Use ample whitespace, subtle shadows, and soft gradients.
*   **Intuitive Interaction:** Buttons should be clearly labeled and provide immediate feedback.
*   **SynapseIP Branding:** Incorporate a palette of professional blues, grays, and whites (similar to Google's Material Design or Gemini's interface) to ensure a familiar and trustworthy feel.
*   **Focus on Content:** The design should highlight the generated report content, making it the primary visual focus.

**Expected Artifacts:**
*   `src/components/ReportDashboard.jsx`
*   `src/components/SavedChatsList.jsx`
*   `src/components/GenerateReportButton.jsx`
*   `src/components/CreditBalance.jsx`
*   `src/components/ReportViewer.jsx`
*   `src/components/DownloadReportButton.jsx`
*   `src/styles/ReportViewer.css` (or `ChatResponse.css`)
*   Updated `src/api/main.py` with `/api/reports/{report_id}` endpoint.
*   Instructions on how to test the UI for displaying a sample report.

```

---

