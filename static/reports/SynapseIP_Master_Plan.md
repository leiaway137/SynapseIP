# BlockChainInterview - Master Blueprint

**Designer:** Albert Vincent Lei

**Target Platform:** Generic AI Agent

**Version:** 1.0.0

**Date:** 2026-05-14

---

## Executive Purpose
Create a way to verify interviews between individuals using dual phones with biometric verification and Monad blockchain for transcript authentication to combat AI deepfakes

---

## 🧭 How to Use This Blueprint

> [!IMPORTANT]
> **The Backend-First Approach:** Because this application requires a robust data foundation, this blueprint is designed 'Backend-First'. This is different from a typical 'UI-First' vibe coding approach where you start with a visual mockup.
> 
> **What to expect:** For the first half of this blueprint, you are building the 'engine'—database schemas, APIs, and background pipelines. **You will not see a visual user interface during these steps.** Once the engine is secure, the later steps will guide you to build the frontend UI that connects to it.

### 💡 Copy-Paste Workflow
Every step in this document contains **Copy & Paste blocks** for your IDE's AI (like Cursor, Windsurf, or OpenClaw).
1. Copy the **Phase 1: Planning** block and paste it into your AI chat.
2. Wait for the AI to generate an `implementation_plan.md` and review it.
3. Once approved, copy the **Phase 2: Execution** block to instruct the AI to write the actual code.

---

## Table of Contents

- [ ] [Step 0: Initialize Project Rules](#step-0-initialize-project-rules)
- [ ] [Step 1: Chapter 1: Create Agent Memory Rules File](#step-1-chapter-1-create-agent-memory-rules-file)
- [ ] [Step 2: Chapter 2: Set Up Project Folder Structure](#step-2-chapter-2-set-up-project-folder-structure)
- [ ] [Step 3: Chapter 3: Define Environment Variables List](#step-3-chapter-3-define-environment-variables-list)
- [ ] [Step 4: Chapter 4: Choose Free Tier Hosting Platform](#step-4-chapter-4-choose-free-tier-hosting-platform)
- [ ] [Step 5: Chapter 5: Initialize Next.js Project](#step-5-chapter-5-initialize-nextjs-project)
- [ ] [Step 6: Chapter 6: Define Database Tables and Columns](#step-6-chapter-6-define-database-tables-and-columns)
- [ ] [Step 7: Chapter 7: Create User Account Table Schema](#step-7-chapter-7-create-user-account-table-schema)
- [ ] [Step 8: Chapter 8: Create Interview Session Table Schema](#step-8-chapter-8-create-interview-session-table-schema)
- [ ] [Step 9: Chapter 9: Create Blockchain Record Table Schema](#step-9-chapter-9-create-blockchain-record-table-schema)
- [ ] [Step 10: Chapter 10: Define API Endpoint List](#step-10-chapter-10-define-api-endpoint-list)
- [ ] [Step 11: Chapter 11: Document Login Request Format](#step-11-chapter-11-document-login-request-format)
- [ ] [Step 12: Chapter 12: Document Interview Start Request Format](#step-12-chapter-12-document-interview-start-request-format)
- [ ] [Step 13: Chapter 13: Document Transcript Upload Request Format](#step-13-chapter-13-document-transcript-upload-request-format)
- [ ] [Step 14: Chapter 14: Document Verification Response Format](#step-14-chapter-14-document-verification-response-format)
- [ ] [Step 15: Chapter 15: Set Up Local Database Connection](#step-15-chapter-15-set-up-local-database-connection)
- [ ] [Step 16: Chapter 16: Build User Registration Screen](#step-16-chapter-16-build-user-registration-screen)
- [ ] [Step 17: Chapter 17: Build User Login Screen](#step-17-chapter-17-build-user-login-screen)
- [ ] [Step 18: Chapter 18: Build Biometric Verification Screen](#step-18-chapter-18-build-biometric-verification-screen)
- [ ] [Step 19: Chapter 19: Build Interview Start Screen](#step-19-chapter-19-build-interview-start-screen)
- [ ] [Step 20: Chapter 20: Build QR Code Generator Screen](#step-20-chapter-20-build-qr-code-generator-screen)
- [ ] [Step 21: Chapter 21: Build Dual Phone Sync Screen](#step-21-chapter-21-build-dual-phone-sync-screen)
- [ ] [Step 22: Chapter 22: Build Audio Recording Screen](#step-22-chapter-22-build-audio-recording-screen)
- [ ] [Step 23: Chapter 23: Implement Speech-to-Text Generation](#step-23-chapter-23-implement-speech-to-text-generation)
- [ ] [Step 24: Chapter 24: Implement Speech-to-Text Quality Check](#step-24-chapter-24-implement-speech-to-text-quality-check)
- [ ] [Step 25: Chapter 25: Build Transcript Display Screen](#step-25-chapter-25-build-transcript-display-screen)
- [ ] [Step 26: Chapter 26: Build Blockchain Hash Signing Screen](#step-26-chapter-26-build-blockchain-hash-signing-screen)
- [ ] [Step 27: Chapter 27: Build Transaction Broadcast Screen](#step-27-chapter-27-build-transaction-broadcast-screen)
- [ ] [Step 28: Chapter 28: Build Record Verification Screen](#step-28-chapter-28-build-record-verification-screen)
- [ ] [Step 29: Chapter 29: Build Admin Dashboard Screen](#step-29-chapter-29-build-admin-dashboard-screen)
- [ ] [Step 30: Chapter 30: Create Implementation Plan Document](#step-30-chapter-30-create-implementation-plan-document)
- [ ] [Step 31: Chapter 31: Run Pre-Flight Impact Analysis](#step-31-chapter-31-run-pre-flight-impact-analysis)
- [ ] [Step 32: Chapter 32: Test Database Schema Migrations](#step-32-chapter-32-test-database-schema-migrations)
- [ ] [Step 33: Chapter 33: Test API Contract Compliance](#step-33-chapter-33-test-api-contract-compliance)
- [ ] [Step 34: Chapter 34: Test Biometric Authentication Flow](#step-34-chapter-34-test-biometric-authentication-flow)
- [ ] [Step 35: Chapter 35: Test Dual Phone Sync Connection](#step-35-chapter-35-test-dual-phone-sync-connection)
- [ ] [Step 36: Chapter 36: Test Blockchain Transaction Signing](#step-36-chapter-36-test-blockchain-transaction-signing)
- [ ] [Step 37: Chapter 37: Test Transcript Hash Verification](#step-37-chapter-37-test-transcript-hash-verification)
- [ ] [Step 38: Chapter 38: Test End-to-End Interview Flow](#step-38-chapter-38-test-end-to-end-interview-flow)
- [ ] [Step 39: Chapter 39: Document Deployment Instructions](#step-39-chapter-39-document-deployment-instructions)
- [ ] [Step 40: Chapter 40: Create User Onboarding Guide](#step-40-chapter-40-create-user-onboarding-guide)

---

## Multi-Agent Parallel Execution Strategy

To prevent merge conflicts and maximize velocity, steps are grouped into **Phases**. Agents assigned to different **Lanes** within a Phase work on isolated file systems (e.g., Frontend vs. Backend). Agents in the same Lane must work sequentially.

### Phase 1: Initialization & Planning (Sequential)
*Constraint: No parallel execution. Foundation must be established before agents are spawned.*

| Order | Agent | Steps | File Context |
| :--- | :--- | :--- | :--- |
| 1 | **Orchestrator** | Ch 1, Ch 2, Ch 3, Ch 4, Ch 5 | Config files, `.env`, `package.json`, Project Root |
| 2 | **Orchestrator** | Ch 30 | `PLAN.md` (Implementation Plan) |

### Phase 2: Architecture & Contracts (Parallel Lanes)
*Constraint: Database Schema and API Contracts are separate files. Safe to parallelize.*

| Lane | Agent | Steps | File Context | Isolation Check |
| :--- | :--- | :--- | :--- | :--- |
| **A** | **Data Agent** | Ch 6, Ch 7, Ch 8, Ch 9, Ch 15 | `schema.prisma`, `migrations/`, `db/connect.ts` | Read-only on API routes |
| **B** | **API Agent** | Ch 10, Ch 11, Ch 12, Ch 13, Ch 14 | `docs/api.md`, `types/api.ts` | Read-only on DB schema |

### Phase 3: Feature Implementation (Parallel Lanes)
*Constraint: Frontend components are split by domain to avoid shared UI file conflicts.*

| Lane | Agent | Steps | File Context | Isolation Check |
| :--- | :--- | :--- | :--- | :--- |
| **A** | **Backend Agent** | Ch 23, Ch 24 + API Logic | `lib/stt.ts`, `api/` routes | No UI components |
| **B** | **Frontend A** | Ch 16, Ch 17, Ch 18, Ch 19, Ch 20 | `pages/auth/`, `pages/interview/start` | No Blockchain/QR logic |
| **C** | **Frontend B** | Ch 21, Ch 22, Ch 25, Ch 26, Ch 27, Ch 28, Ch 29 | `pages/blockchain/`, `pages/admin/` | No Auth logic |

### Phase 4: Testing & Validation (Parallel Lanes)
*Constraint: Test suites target specific code blocks. E2E tests run last within this phase.*

| Lane | Agent | Steps | File Context | Isolation Check |
| :--- | :--- | :--- | :--- | :--- |
| **A** | **QA Agent 1** | Ch 32, Ch 33, Ch 37 | `tests/db/`, `tests/api/` | No UI interaction |
| **B** | **QA Agent 2** | Ch 34, Ch 35, Ch 36 | `tests/features/` | No DB migration logic |
| **C** | **QA Agent 3** | Ch 31, Ch 38 | `tests/e2e/`, `pre-flight/` | Read-only on codebase |

### Phase 5: Deployment & Handover (Sequential)
*Constraint: Deployment scripts depend on successful testing. Documentation is final.*

| Order | Agent | Steps | File Context |
| :--- | :--- | :--- | :--- |
| 1 | **DevOps Agent** | Ch 39 | `deploy/`, `ci-cd/` |
| 2 | **Technical Writer** | Ch 40 | `docs/user-guide/` |

### Critical Guardrails for Agents
1.  **Shared Components:** Agents B and C (Frontend) must not modify `layout.tsx` or `api-client.ts` simultaneously. Use a locking mechanism for shared files.
2.  **Schema Changes:** If Phase 3 reveals a DB change, Data Agent (Lane 2A) must update Schema before Backend Agent (Lane 3A) proceeds.
3.  **Environment:** All Agents must pull the latest `.env` template before writing code.

---

<a id='step-1-chapter-1-create-agent-memory-rules-file'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='0'> Step 1: Chapter 1: Create Agent Memory Rules File</label>

**Purpose (Why we are building this):**
This step defines the configuration rules for the AI agent to ensure interview context is stored consistently for blockchain hashing. Without these rules, memory retrieval will fail during authentication and deepfake verification.

**User Experience (UX) Flow:**
This feature connects to the `InterviewSetupPage` and `AgentDashboard` where users view memory status. Users expect to see a green indicator when memory rules are active and valid.

**Expected Outcomes:**
If successful, the agent loads rules and validates data against the schema. If failed, the agent rejects memory updates with a 400 Bad Request error.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 1: Create Agent Memory Rules File** feature.

#### 1. UX & Logic Description
This feature establishes the configuration file that dictates how the AI agent stores and retrieves interview context. It connects directly to the `InterviewSetupPage` to initialize memory and the `AgentDashboard` to display health status. The user sees a status indicator confirming the rules are loaded.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Define strict JSON Schema using Zod for `src/agents/memory/rules.ts`. All fields must be required with max character lengths of 255 for text inputs.
* **API/Database:** Use serverless API routes at `/api/agents/memory`. Reference `interview_sessions` table for storage. Handle 400 Bad Request for validation failures and 404 for missing rules.
* **Testing Requirements:** Test schema validation, API response codes, and edge cases like invalid JSON. Verify separation of Generate and Evaluate operations.
* **Global State:** Verify packages against `PROJECT_RULES.md` Tech Matrix before implementation.
* **Infrastructure:** Use standard serverless API routes for simple tasks.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
4. Explicitly define how edge cases are handled (e.g., 400 Bad Request for validation failure).
5. Ensure distinct Generate and Evaluate operations are separated.
6. Define strict JSON Schema (e.g., using Zod) and pass it directly into the AI provider's SDK.
7. Verify paths match `src/agents/memory/rules.ts` and `src/schema/memory-schema.ts`.
8. Ensure API endpoints match `/api/agents/memory`.
9. Ensure table references match `interview_sessions` and `memory_rules`.
10. Confirm no manual actions outside IDE are required.
```

---

<a id='step-2-chapter-2-set-up-project-folder-structure'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='1'> Step 2: Chapter 2: Set Up Project Folder Structure</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure the root directory is initialized with `npm init -y` before running AI generation commands.</li>
    <li>Verify `package.json` dependencies match Chapter 1 (Zod, TypeScript, Next.js) before proceeding.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step establishes the foundational directory layout to ensure modular scaling and consistency with Chapter 1's memory rules. It prevents architectural drift by enforcing a standardized structure for all future API, schema, and agent files.

**User Experience (UX) Flow:**
This feature is backend infrastructure that supports the `/interview` and `/dashboard` pages. It ensures developers can locate configuration and logic files quickly without breaking existing integrations.

*   **Expected Success:** Directory tree matches Chapter 1 specs (`src/agents`, `src/schema`) and no import errors occur.
*   **Expected Failure:** Missing folders cause 404 errors on API routes or build failures due to missing imports.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 2: Set Up Project Folder Structure** feature.

#### 1. UX & Logic Description
Create the root directory structure ensuring `src/agents/memory/rules.ts` and `src/schema/memory-schema.ts` exist as per Chapter 1.
This structure connects directly to the `/interview` page for session handling and `/dashboard` for audit logs.

#### 2. Technical Guardrails & Constraints
*   **Data Validation:** All schema files must use Zod with max 255 char lengths and required fields enforced.
*   **API/Database:** Place API routes under `src/api` matching `/api/agents/memory` endpoint and reference `interview_sessions` table.
*   **Testing Requirements:** Verify folder existence and import paths resolve correctly without circular dependencies.
*   **Constraints:** Do not introduce packages outside the Chapter 1 Tech Matrix (Zod, TS, Node).
*   **Infrastructure:** Use serverless API routes for all simple tasks; do not use queues yet.
*   **AI Separation:** Ensure Generate and Evaluate operations are distinct in the code structure.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional

---

<a id='step-3-chapter-3-define-environment-variables-list'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='2'> Step 3: Chapter 3: Define Environment Variables List</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Create a `.env.example` file at the project root listing all required variables (e.g., `MONAD_RPC_URL`, `DB_CONNECTION_STRING`).</li>
    <li>Copy `.env.example` to `.env` and populate with actual credentials before running any serverless functions.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This feature secures sensitive configuration like blockchain RPC URLs and database credentials by preventing hardcoding. It ensures the application initializes safely with validated environment variables before connecting to the Monad blockchain or database.

**User Experience (UX) Flow:**
This is a backend configuration step that connects to the system initialization for all pages, specifically supporting the `/api/agents/memory` endpoint. No direct user page exists, but failures here will block access to the Interview Verification and Biometric Authentication pages.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 3: Define Environment Variables List** feature.

#### 1. UX & Logic Description
This feature involves creating a configuration schema and environment file to securely manage API keys and database strings. It connects to the system startup logic that initializes the `/api/agents/memory` endpoint and database connections for `interview_sessions`.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** All environment variables must be validated using Zod schemas in `src/config/env.ts` (e.g., `MONAD_RPC_URL` must be a valid URL, `DB_CONNECTION_STRING` is required).
* **API/Database:** Ensure variables support the `/api/agents/memory` endpoint and connect to `interview_sessions` and `memory_rules` tables.
* **Testing Requirements:** Test that the app crashes gracefully with clear error logs if `.env` is missing or if variables fail Zod validation.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-4-chapter-4-choose-free-tier-hosting-platform'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='3'> Step 4: Chapter 4: Choose Free Tier Hosting Platform</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Create an account on a free-tier serverless provider (e.g., Vercel, Render, Railway) compatible with Node.js environments.</li>
    <li>Generate a new project repository link to be used for deployment configuration.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step configures the infrastructure required to host the serverless API routes defined in previous chapters. It ensures the application can accept interview data and store blockchain transcripts securely.

**User Experience (UX) Flow:**
This feature connects to the Deployment Pipeline and Environment Configuration pages within the developer console. It does not directly impact the end-user interview interface but enables the backend functionality.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 4: Choose Free Tier Hosting Platform** feature.

#### 1. UX & Logic Description
Configure the deployment environment on a selected free-tier provider to host the Next.js serverless functions. This connects directly to the `src/config/env.ts` configuration for environment variable injection. Ensure the hosting platform supports the `DB_CONNECTION_STRING` and `MONAD_RPC_URL` required by Chapter 3.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Environment variables must strictly match keys in `src/config/env.ts` (e.g., `MONAD_RPC_URL`, `DB_CONNECTION_STRING`).
* **API/Database:** Ensure `/api/agents/memory` endpoint is accessible via the deployed URL using the `interview_sessions` and `memory_rules` tables.
* **Testing Requirements:** Verify the deployed URL returns a 200 OK on the memory endpoint and rejects requests with missing auth headers (401).

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-5-chapter-5-initialize-nextjs-project'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='4'> Step 5: Chapter 5: Initialize Next.js Project</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Run `npx create-next-app@latest block-chain-interview --typescript --tailwind --eslint` in your terminal.</li>
    <li>Run `npm install zod` to install validation libraries.</li>
    <li>Manually create `.env` and `.env.example` files in the root directory.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step establishes the Next.js framework to host the interview verification UI and API. It ensures the environment supports serverless functions and database connections defined in Chapters 3 and 4.

**User Experience (UX) Flow:**
This feature initializes the Root Landing Page (`src/app/page.tsx`).
Users will land here before being redirected to the Interview Dashboard (`/dashboard`) upon authentication.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 5: Initialize Next.js Project** feature.

#### 1. UX & Logic Description
The AI will scaffold the Next.js application structure using the established file paths.
This includes configuring `src/config/env.ts` to validate environment variables and creating `src/app/page.tsx` as the entry point.
The project must connect to the future Interview Dashboard and support the `/api/agents/memory` endpoint structure.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** `src/config/env.ts` must use Zod to validate `MONAD_RPC_URL` and `DB_CONNECTION_STRING` (required, string, max 255 chars).
* **API/Database:** Reserve paths for `/api/agents/memory` and ensure `src/config/env.ts` references `interview_sessions` and `memory_rules` tables for future connection.
* **Testing Requirements:** Test that `.env` loads correctly, `src/config/env.ts` throws errors on missing variables, and `src/app/page.tsx` renders without console errors.
* **Package Restrictions:** Use ONLY packages listed in the Tech Matrix (Next.js, Zod, standard Node libs). No external AI grading packages.
* **Infrastructure:** Use standard serverless API routes for all future tasks; do not implement queues yet.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md` and Tech Matrix constraints.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
4. Verify `src/config/env.ts` strictly validates `MONAD_RPC_URL` and `DB_CONNECTION_STRING`.
5. Confirm `src/app/page.tsx` links correctly to future `/dashboard` routes.
```

**Expected Outcome:**
If successful, the Next.js app runs locally with valid environment variable validation.
If it fails, the server throws 400 errors on missing env vars or the build fails due to dependency conflicts.

---

<a id='step-6-chapter-6-define-database-tables-and-columns'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='5'> Step 6: Chapter 6: Define Database Tables and Columns</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure your database provider (e.g., Supabase, Neon, PlanetScale) is provisioned and the `DB_CONNECTION_STRING` is active in your `.env` file before running migrations.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step formalizes the data structure required to store biometric verification hashes and interview transcripts securely. It ensures data integrity before blockchain anchoring and prevents schema drift during development.

**User Experience (UX) Flow:**
This backend schema directly supports the `src/app/page.tsx` (Interview Start) and the Memory Rules configuration flow. Users will not see these tables, but their data persistence relies on this definition for session tracking.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 6: Define Database Tables and Columns** feature.

#### 1. UX & Logic Description
This step defines the underlying data model for the BlockChainInterview app. 
It connects to the `src/app/page.tsx` session initialization and the `/api/agents/memory` endpoint.
The schema must support `interview_sessions` for tracking and `memory_rules` for AI constraints.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Use Zod for all schema definitions. Max character length 255 for text fields. All ID fields required.
* **API/Database:** 
    *   Table: `interview_sessions` (Columns: `id`, `user_id`, `biometric_hash`, `transcript_ref`, `monad_tx_hash`, `created_at`).
    *   Table: `memory_rules` (Columns: `id`, `rule_key`, `rule_value`, `created_at`).
    *   File: `src/schema/memory-schema.ts` (Extend for DB models).
    *   File: `src/schema/interview-schema.ts` (Create new for interview logic).
    *   Endpoint: `/api/agents/memory` (Reads/Writes these tables).
* **Testing Requirements:** Test schema migration success. Test Zod validation failure (400 Bad Request). Test missing record retrieval (404 Not Found).

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-7-chapter-7-create-user-account-table-schema'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='6'> Step 7: Chapter 7: Create User Account Table Schema</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure the `DB_CONNECTION_STRING` environment variable is active and accessible in your local development environment before defining the schema.</li>
    <li>Verify that the database migration tool (e.g., Prisma or Drizzle) is installed and configured in `package.json` before running schema updates.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step defines the `users` table schema to link interview sessions to specific human identities via foreign keys. It is necessary to enable biometric verification and blockchain authentication for each unique user account.

**User Experience (UX) Flow:**
*   **Connected Pages:** Registration Page (`/register`), Login Page (`/login`), and Interview Dashboard (`/dashboard`).
*   **Visual Expectations:** Users input credentials during sign-up; the system validates against this schema before creating a `user_id` for future interview sessions.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 7: Create User Account Table Schema** feature.

#### 1. UX & Logic Description
This feature creates the database schema for user accounts, which connects to the Registration and Login pages.
It ensures every interview session in the `interview_sessions` table is linked to a valid `user_id` from this new `users` table.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Use Zod for all schema definitions.
    *   `email`: Required, max 255 characters, valid email format.
    *   `id`: Primary key, UUID or Integer (consistent with `interview_sessions`).
    *   `created_at`: Timestamp, required.
* **API/Database:** 
    *   Table Name: `users`.
    *   File Path: `src/schema/user-schema.ts`.
    *   Constraint: Must match the `user_id` type in `interview_sessions` (Chapter 6).
* **Testing Requirements:** 
    *   Test schema validation for missing fields and invalid email formats.
    *   Test foreign key integrity between `users` and `interview_sessions`.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-8-chapter-8-create-interview-session-table-schema'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='7'> Step 8: Chapter 8: Create Interview Session Table Schema</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure `DB_CONNECTION_STRING` is populated in your `.env` file before running migrations.</li>
    <li>Verify `MONAD_RPC_URL` is set in `.env` for blockchain transaction logging.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step finalizes the data structure for storing interview metadata, linking users to their blockchain transcripts. It ensures data integrity and prepares the database for session creation APIs.

**User Experience (UX) Flow:**
Users interact with this schema during the "Interview Dashboard" when creating a new session. It connects to "User Profile" for identity verification and "Interview History" for viewing past records.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 8: Create Interview Session Table Schema** feature.

#### 1. UX & Logic Description
The schema enables the "Interview Dashboard" to save session metadata securely. It links a `user_id` from the `users` table to a new `interview_sessions` record. This ensures every interview is traceable to a verified identity and blockchain hash.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Use Zod for `src/schema/interview-schema.ts`. `biometric_hash` max 255 chars, `monad_tx_hash` max 255 chars, `user_id` required.
* **API/Database:** Reference `interview_sessions` and `users` tables. Support `/api/agents/memory` pattern for future session endpoints.
* **Testing Requirements:** Test schema validation (happy path), FK constraint violations (edge case), and null checks.
* **Infrastructure Physics:** Use Serverless API routes for schema validation logic.
* **Global State Registry:** Use only Zod, Next.js, and ORM (Prisma/Drizzle) as per Chapter 1-7.
* **Separation of AI Concerns:** Ensure schema generation is distinct from evaluation logic.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-9-chapter-9-create-blockchain-record-table-schema'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='8'> Step 9: Chapter 9: Create Blockchain Record Table Schema</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure your database migration tool (e.g., Drizzle/Prisma) is configured in `src/config/env.ts` before generating schema files.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step creates a dedicated table to store immutable blockchain transaction proofs linked to interview sessions, ensuring audit integrity separate from session metadata. It prevents data tampering by anchoring interview records to the Monad blockchain.

**User Experience (UX) Flow:**
This feature connects to the `src/app/interview/[id]/page.tsx` to display verification status (e.g., "Verified on Blockchain"). Users see a read-only badge indicating the transaction hash and block confirmation status.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 9: Create Blockchain Record Table Schema** feature.

#### 1. UX & Logic Description
This schema defines the `blockchain_records` table to store immutable on-chain verification data. It links directly to the `interview_sessions` table via a foreign key to ensure data integrity. The frontend will read this table to display verification badges on the Interview Session Page.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Use Zod for all schemas. `tx_hash` must be 255 chars max, `block_number` must be a positive integer. `status` must be enum ['pending', 'confirmed', 'failed'].
* **API/Database:** Create file `src/schema/blockchain-record-schema.ts`. Table name `blockchain_records`. Columns: `id` (uuid), `interview_session_id` (uuid, FK), `tx_hash` (string), `block_number` (int), `status` (enum), `created_at` (timestamp).
* **Testing Requirements:** Test schema validation for invalid hashes. Test Foreign Key constraint enforcement between `blockchain_records` and `interview_sessions`. Test edge cases like duplicate transaction hashes.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md` and previous architectural decisions (Zod, Serverless, Next.js).
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
4. Verify that `src/schema/blockchain-record-schema.ts` aligns with `src/schema/interview-schema.ts` for FK consistency.
```

---

<a id='step-10-chapter-10-define-api-endpoint-list'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='9'> Step 10: Chapter 10: Define API Endpoint List</label>

**Purpose (Why we are building this):**
This step defines the communication contracts between the frontend interview interface and the backend blockchain verification logic. It prevents integration drift between the dual-phone biometric capture and the Monad ledger recording.

**User Experience (UX) Flow:**
Users interact with this via `src/app/interview/[id]/page.tsx` to initiate sessions and `src/app/page.tsx` for landing. The API list ensures seamless data flow from session creation to blockchain verification.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 10: Define API Endpoint List** feature.

#### 1. UX & Logic Description
The API list connects `src/app/interview/[id]/page.tsx` to backend routes for session creation and blockchain verification. It enables users to upload biometric hashes and retrieve verification status via the Monad network.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Use Zod for all payloads (max 255 chars, required IDs).
* **API/Database:** Use `src/app/api/.../route.ts` (Serverless) and tables `interview_sessions`, `block

---

<a id='step-11-chapter-11-document-login-request-format'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='10'> Step 11: Chapter 11: Document Login Request Format</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Set the `JWT_SECRET` environment variable in your `.env` file for session signing.</li>
    <li>Ensure `DB_CONNECTION_STRING` is active to access the `users` table.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This feature establishes the authentication gateway for users to access interview sessions securely. It prevents unauthorized access to biometric and blockchain-verified data.

**User Experience (UX) Flow:**
*   Users land on `src/app/login/page.tsx` to enter credentials.
*   Successful login redirects to `src/app/dashboard/page.tsx`.
*   Failed login displays a specific error message on the same page.

**Expected Outcomes:**
*   If successful, the user receives a session token and sees the dashboard.
*   If failed, the system returns a 401 error with a clear invalid credential message.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 11: Document Login Request Format** feature.

#### 1. UX & Logic Description
The user interacts with the Login Page (`src/app/login/page.tsx`) to submit credentials.
Upon validation, the system creates a session and redirects to the Dashboard (`src/app/dashboard/page.tsx`).
If validation fails, the page remains open with an error state.

#### 2. Technical Guardrails & Constraints
*   **Data Validation:** Use Zod in `src/schema/auth-schema.ts`. Email must be valid format. Password min 8 chars.
*   **API/Database:** Endpoint `/api/auth/login`. Use `users` table (id, email, password_hash). Return 400 for validation, 401 for auth fail.
*   **Testing Requirements:** Test happy path (valid creds), edge case (wrong password), and edge case (non-existent user).

####

---

<a id='step-12-chapter-12-document-interview-start-request-format'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='11'> Step 12: Chapter 12: Document Interview Start Request Format</label>

**Purpose (Why we are building this):**
*   This feature defines the API payload and logic to initiate a new interview session securely.
*   It ensures every interview is linked to a verified user and prepared for blockchain recording.

**User Experience (UX) Flow:**
*   User clicks "Start Interview" on `src/app/dashboard/page.tsx`.
*   System navigates to `src/app/interview/[id]/page.tsx` with a new session ID.
*   API call `POST /api/interviews/start` creates the record in `interview_sessions` table.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 12: Document Interview Start Request Format** feature.

#### 1. UX & Logic Description
*   **Entry Point:** User triggers start action from `src/app/dashboard/page.tsx`.
*   **Navigation:** Redirects to `src/app/interview/[id]/page.tsx` using the new session ID.
*   **Logic:** Client sends user credentials; Server validates and inserts into `interview_sessions` table.

#### 2. Technical Guardrails & Constraints
*   **Data Validation:** Use Zod in `src/schema/interview-schema.ts`. Max 255 chars for hashes. Required `user_id`.
*   **API/Database:** Endpoint `POST /api/interviews/start`. Insert into `interview_sessions` (columns: `id`, `user_id`, `biometric_hash`, `transcript_ref`, `monad_tx_hash`, `created_at`).
*   **Testing Requirements:** Test happy path (200 OK) and validation failures (400 Bad Request).
*   **Infrastructure:** Use serverless API routes (`src/app/api/interviews/start/route.ts`). No queues.
*   **Global Registry:** Adhere strictly to packages in PROJECT_RULES.md Tech Matrix.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-13-chapter-13-document-transcript-upload-request-format'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='12'> Step 13: Chapter 13: Document Transcript Upload Request Format</label>

**Purpose (Why we are building this):**
This feature captures the interview transcript file to be hashed and anchored on the Monad blockchain for immutable verification. It ensures the text data matches the verified biometric session to combat AI deepfakes.

**User Experience (UX) Flow:**
*   **Primary Page:** `src/app/interview/[id]/page.tsx` (Interview Session Dashboard).
*   **Interaction:** User selects a file via a drag-and-drop zone or file picker.
*   **Feedback:** A success toast appears upon upload; errors display inline if validation fails.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 13: Document Transcript Upload Request Format** feature.

#### 1. UX & Logic Description
The user interacts with `src/app/interview/[id]/page.tsx` to upload a transcript file (PDF/Text) linked to their active session. The frontend sends a POST request to the API which validates the file, stores it, and updates the `interview_sessions` table with the reference path.

#### 2. Technical Guardrails & Constraints
*   **Data Validation:** Use Zod in `src/schema/transcript-schema.ts`. Max file size 5MB, allowed types `.pdf`, `.txt`, `.docx`. `interview_id` must be a valid UUID.
*   **API/Database:** Endpoint `POST /api/interviews/[id]/transcript`. Updates `interview_sessions` table column `transcript_ref`. Return 400 for validation, 404 for missing session, 500 for storage failure.
*   **Testing Requirements:** Test valid file upload (200 OK), invalid extension (400), and missing interview ID (404). Verify `transcript_ref` updates in DB.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
4. Verify that the Zod schema strictly matches the API payload requirements.
5. Confirm that the `interview_sessions` table update logic handles transaction rollbacks correctly.
```

---

<a id='step-14-chapter-14-document-verification-response-format'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='13'> Step 14: Chapter 14: Document Verification Response Format</label>

**Purpose (Why we are building this):**
*   This feature defines the standardized JSON structure returned when a transcript is verified against the Monad blockchain and biometric data.
*   It ensures the frontend can reliably display verification status, preventing UI inconsistencies and data misinterpretation.

**User Experience (UX) Flow:**
*   **Pages:** Connects directly to `src/app/interview/[id]/page.tsx` (Interview Detail) and `src/app/dashboard/page.tsx` (Status Overview).
*   **Interaction:** User uploads transcript (Ch 13), system processes, and this response format confirms validity or flags discrepancies.
*   **Visuals:** Verification badge updates based on the `status` field in the response payload.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 14: Document Verification Response Format** feature.

#### 1. UX & Logic Description
The system must return a standardized JSON object confirming transcript verification status after upload. This response connects to `src/app/interview/[id]/page.tsx` to update the UI with a verification badge. The logic checks the `monad_tx_hash` in `interview_sessions` against the blockchain to validate authenticity.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Use Zod at `src/schema/verification-schema.ts`. Enforce `status` as an enum ('verified', 'pending', 'failed'). Limit `tx_hash` to 255 characters.
* **API/Database:** Implement `GET /api/interviews/[id]/verification` at `src/app/api/interviews/[id]/verification/route.ts`. Query `interview_sessions` and `blockchain_records` tables. Return 200 OK on success, 404 if session missing.
* **Testing Requirements:** Test happy path (valid hash returns 'verified'). Test edge cases (invalid hash returns 'failed', missing ID returns 404).
* **AI Concerns:** Define strict JSON Schema for the response. Do not allow AI to self-grade the schema; separate Generate (schema creation) and Evaluate (schema validation) logic.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-15-chapter-15-set-up-local-database-connection'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='14'> Step 15: Chapter 15: Set Up Local Database Connection</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure a local PostgreSQL database instance is running (via Docker or local install)</li>
    <li>Verify `DB_CONNECTION_STRING` is configured in your local `.env` file matching the format in `.env.example`</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step establishes the local database connection required for all subsequent interview session, user, and blockchain record operations. Without a working database connection, no data can be persisted or retrieved for biometric verification and transcript authentication.

**User Experience (UX) Flow:**
This feature has no direct user-facing UI. It enables the backend functionality that supports the `src/app/dashboard/page.tsx` (interview start), `src/app/interview/[id]/page.tsx` (transcript upload), and `src/app/interview/[id]/verification/page.tsx` (verification badge display) pages.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 15: Set Up Local Database Connection** feature.

#### 1. UX & Logic Description
This feature establishes the database connection layer that all API routes depend on. It connects the Next.js application to the local PostgreSQL database where `users`, `interview_sessions`, `memory_rules`, and `blockchain_records` tables reside. No direct user interaction occurs; this enables all data persistence for the interview verification flow.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Connection string must be validated via Zod in `src/config/env.ts` (max 255 chars, required field)
* **API/Database:** Use `DB_CONNECTION_STRING` environment variable; connect to tables: `users`, `interview_sessions`, `memory_rules`, `blockchain_records`
* **Testing Requirements:** Test connection on app startup, verify 400 error on invalid connection string, test 200 OK on successful connection
* **Infrastructure:** Use serverless API routes (Next.js App Router pattern)
* **Global State:** Do not introduce new packages outside Tech Matrix in PROJECT_RULES.md
* **Schema Consistency:** Must reference existing schemas: `src/schema/user-schema.ts`, `src/schema/interview-schema.ts`, `src/schema/memory-schema.ts`, `src/schema/blockchain-record-schema.ts`

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

**Testing Requirements:**
* **Connection Test:** Verify database connection succeeds on app startup
* **Validation Test:** Confirm 400 Bad Request returns if `DB_CONNECTION_STRING` is missing or malformed
* **Schema Test:** Verify all 4 tables (`users`, `interview_sessions`, `memory_rules`, `blockchain_records`) are accessible
* **Environment Test:** Confirm `.env` file loads correctly in local development
* **Edge Case:** Test connection timeout handling (5-second max)

**Files to Create/Modify:**
* `src/config/db-connection.ts` (new) - Database connection singleton
* `.env` (update) - Add local `DB_CONNECTION_STRING`
* `.env.example` (update) - Add example `DB_CONNECTION_STRING` format

**Expected Results:**
* **Success:** Application starts without database connection errors; API routes can query tables successfully
* **Failure:** Application throws clear error message indicating missing/invalid `DB_CONNECTION_STRING` in `.env`

**Code Review Reminders:**
* Ask your IDE to check for recursive loops in connection pooling logic
* Verify JSON schemas match natural language prompts in validation messages
* Ensure no hardcoded credentials exist in source code
* Confirm all file paths match PROJECT_RULES.md structure exactly

---

<a id='step-16-chapter-16-build-user-registration-screen'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='15'> Step 16: Chapter 16: Build User Registration Screen</label>

**Purpose (Why we are building this):**
This feature enables new users to create accounts to access interview verification tools. Without this, users cannot authenticate to start dual-phone interviews or store blockchain transcripts.

**Expected Outcome:**
If successful, a new user record is created in the `users` table and redirected to the Dashboard. If it fails, the UI displays specific validation errors (e.g., 409 Conflict for duplicate email) without creating a record.

**User Experience (UX) Flow:**
Users access this via the Register link on the Login page (`src/app/login/page.tsx`). Upon success, they redirect to the Dashboard (`src/app/dashboard/page.tsx`). The form includes Email, Password, and Confirm Password fields.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 16: Build User Registration Screen** feature.

#### 1. UX & Logic Description
Create a registration form at `src/app/register/page.tsx` linking back to Login (`src/app/login/page.tsx`). 
On submit, validate inputs client-side then POST to `src/app/api/auth/register/route.ts`. 
Success redirects to `src/app/dashboard/page.tsx`; failure displays error messages inline.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Use Zod in `src/schema/user-schema.ts`. Email: required, max 255 chars. Password: required, min 8 chars. Confirm Password: must match.
* **API/Database:** Endpoint `POST /api/auth/register`. DB Table `users` (columns: `id`, `email`, `password_hash`, `created_at`). 
* **Testing Requirements:** Test happy path (new user), edge case (duplicate email 409), and edge case (weak password 400).
* **Infrastructure:** Use standard Next.js serverless API routes. Do not use queues.
* **Structured Outputs:** Define strict Zod schema for request body before processing.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
4. Verify `src/config/db-connection.ts` is used for DB access and `src/config/env.ts` for validation.
5. Ensure no new packages are added outside the Tech Matrix (Next.js, Zod, Tailwind).
```

---

<a id='step-17-chapter-17-build-user-login-screen'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='16'> Step 17: Chapter 17: Build User Login Screen</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure the `JWT_SECRET` environment variable is defined in both `.env` and `.env.example` files.</li>
    <li>Verify `DB_CONNECTION_STRING` is active and pointing to the local PostgreSQL instance from Chapter 15.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step enables authenticated access to interview sessions and blockchain verification features. It secures user identity before allowing biometric interview initiation.

**User Experience (UX) Flow:**
*   User lands on `src/app/login/page.tsx`, enters credentials, and submits.
*   Success redirects to `src/app/dashboard/page.tsx`; failure displays inline error on the login form.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 17: Build User Login Screen** feature.

#### 1. UX & Logic Description
Create a login form on `src/app/login/page.tsx` collecting email and password. Include a link to `src/app/register/page.tsx` for new users and a submit button that triggers `POST /api/auth/login`. Upon success, redirect to `src/app/dashboard/page.tsx`.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Use Zod in `src/schema/auth-schema.ts`. Email required, max 255 chars. Password required, min 8 chars.
* **API/Database:** Use `src/app/api/auth/login/route.ts` (Serverless). Query `users` table (`id`, `email`, `password_hash`). Return 200 OK with JWT on success. Return 400 Bad Request for validation failure. Return 401 Unauthorized for invalid credentials.
* **Testing Requirements:** Test valid login (redirects), invalid password (401), missing fields (400), and non-existent email (401). Ensure no packages outside Next.js, Zod, Tailwind are used.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-18-chapter-18-build-biometric-verification-screen'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='17'> Step 18: Chapter 18: Build Biometric Verification Screen</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure the deployment environment enforces HTTPS, as biometric camera access requires secure contexts.</li>
    <li>Verify `DB_CONNECTION_STRING` and `JWT_SECRET` are correctly set in `.env` before starting development.</li>
</ul>
</div>

**Purpose (Why we are building this):**
*   This screen captures a live biometric hash to verify human presence and prevent AI deepfakes during interviews.
*   Success results in a stored `biometric_hash` in the `interview_sessions` table; failure blocks session start with a 400/404 error.

**User Experience (UX) Flow:**
*   User navigates to `src/app/interview/[id]/page.tsx` and sees a "Verify Identity" button.
*   Clicking triggers a browser camera prompt; upon capture, a local hash is generated and sent to the API.
*   The screen connects directly to `src/app/dashboard/page.tsx` (previous step) and `src/app/api/interviews/start/route.ts`.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 18: Build Biometric Verification Screen** feature.

#### 1. UX & Logic Description
The UI resides in `src/app/interview/[id]/page.tsx` and includes a video preview and "Capture & Verify" button.
Clicking the button triggers `navigator.mediaDevices.getUserMedia` to access the camera.
A SHA-256 hash of the captured frame is generated client-side using the Web Crypto API.
This hash is submitted to `POST /api/interviews/start` alongside the `user_id`.
The screen connects to `src/app/dashboard/page.tsx` for entry and `src/app/interview/[id]/page.tsx` for processing.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** `biometric_hash` must be max 255 chars (Zod), `user_id` is required.
* **API/Database:** Use `POST /api/interviews/start` endpoint; handle 400 (Validation) and 404 (Not Found) errors.
* **Testing Requirements:** Test camera permission denial, hash generation, and API 200/400 responses.
* **Tech Stack:** Use only Next.js, Zod, Tailwind, and Web Crypto API (No external biometric SDKs).
* **Schema:** Validate input against `src/schema/interview-schema.ts` before API submission.
* **Database:** Update `interview_sessions` table with `biometric_hash` column upon success.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md` and Tech Matrix constraints.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
4. Verify the `biometric_hash` column in `interview_sessions` is populated correctly.
5. Confirm error handling for 400 Bad Request and 404 Not Found is implemented.
6. Ensure no external packages are introduced beyond Next.js, Zod, and Tailwind.
7. Verify HTTPS is enforced for camera access permissions.
8. Check that `src/app/interview/[id]/page.tsx` correctly handles the API response state.
9. Validate that `src/schema/interview-schema.ts` enforces the 255 character limit on hashes.
10. Ensure the `user_id` is correctly passed from the session context to the API payload.
```

---

<a id='step-19-chapter-19-build-interview-start-screen'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='18'> Step 19: Chapter 19: Build Interview Start Screen</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Verify that `DB_CONNECTION_STRING` and `JWT_SECRET` are present in your local `.env` file before proceeding.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This feature allows authenticated users to initiate a new interview session, creating a database record and redirecting to the biometric capture screen. It bridges the Dashboard and the Interview execution phase, ensuring session integrity before biometric verification begins.

**User Experience (UX) Flow:**
*   **Entry Point:** User clicks "Start New Interview" on `src/app/dashboard/page.tsx`.
*   **Intermediate Page:** User lands on `src/app/interview/start/page.tsx` to confirm session details.
*   **Action:** User submits the form, triggering `POST /api/interviews/start`.
*   **Exit Point:** On success, user redirects to `src/app/interview/[id]/page.tsx` for biometric verification.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 19: Build Interview Start Screen** feature.

#### 1. UX & Logic Description
Design a simple confirmation page at `src/app/interview/start/page.tsx` that appears after clicking 'Start Interview' on the dashboard. This page must call the existing API endpoint `POST /api/interviews/start` to create a session record in the `interview_sessions` table. Upon receiving a 200 OK response containing the new `id`, redirect the user immediately to `src/app/interview/[id]/page.tsx` where biometrics are handled.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Use `src/schema/interview-schema.ts` (Zod) to validate `user_id` (required string) on the API side.
* **API/Database:** Use `POST /api/interviews/start` to insert into `interview_sessions` table (columns: `user_id`, `created_at`).
* **Testing Requirements:** Test 200 OK redirect flow, 400 Bad Request for missing user_id, and 401 Unauthorized if token is missing.
* **Infrastructure:** Use standard Next.js Serverless API routes; do not implement queues.
* **Global State:** Do not introduce new packages; rely on Next.js, Zod, and Tailwind as per Tech Matrix.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-20-chapter-20-build-qr-code-generator-screen'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='19'> Step 20: Chapter 20: Build QR Code Generator Screen</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>None. This feature uses existing database tables and serverless infrastructure.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This feature generates a scannable QR code for interview sessions to enable the second phone (interviewer) to link and verify the session securely. It is necessary to combat AI deepfakes by ensuring physical presence and dual-device authentication.

**User Experience (UX) Flow:**
*   User navigates from `src/app/interview/start/page.tsx` to `src/app/interview/[id]/qr/page.tsx`.
*   Screen displays a large QR code representing the interview session ID and a "Copy Link" fallback.
*   Scanning directs the second phone to `src/app/interview/connect/page.tsx` (future feature) to join the session.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 20: Build QR Code Generator Screen** feature.

#### 1. UX & Logic Description
Create a new page `src/app/interview/[id]/qr/page.tsx` that renders a QR code based on the interview session ID passed in the URL params. The UI must connect back to `src/app/interview/start/page.tsx` via a "Back" button. Since we cannot add new packages per Chapter 19 constraints, implement a client-side SVG QR code generator function within the component or use a lightweight CDN import if absolutely necessary, but prioritize pure JS/CSS generation.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Interview ID must be a valid string; max 255 chars for session ID.
* **API/Database:** Fetch session details from `interview_sessions` table (id, user_id, created_at) via `GET /api/interviews/[id]/qr-data`.
* **Testing Requirements:** Verify 200 OK response with session data; verify 404 for invalid IDs; ensure QR renders visually.
* **Constraints:** NO new npm packages (Next.js, Zod, Tailwind only). Use serverless API routes.
* **Structured Output:** Define Zod schema for API response: `{ id: string, url: string, status: 'active' | 'expired' }`.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-21-chapter-21-build-dual-phone-sync-screen'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='20'> Step 21: Chapter 21: Build Dual Phone Sync Screen</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Run database migration to add `session_code` (VARCHAR 255) column to `interview_sessions` table before building.</li>
    <li>Ensure `DB_CONNECTION_STRING` is active in `.env` as per Chapter 15.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This feature enables two devices to link to a single interview session, ensuring both parties are physically present to prevent AI deepfake substitution. It establishes a secure handshake between interviewer and interviewee before biometric verification begins.

**User Experience (UX) Flow:**
*   **Interviewer:** Navigates to `src/app/interview/start/page.tsx` to generate a unique sync code.
*   **Interviewee:** Navigates to `src/app/interview/join/page.tsx` to enter the sync code and validate session ownership.
*   **Sync:** Both phones display a "Connected" status on `src/app/interview/[id]/page.tsx` upon successful validation.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 21: Build Dual Phone Sync Screen** feature.

#### 1. UX & Logic Description
The Interviewer views a unique 6-digit code on `src/app/interview/start/page.tsx` after session creation. The Interviewee enters this code on `src/app/interview/join/page.tsx` to fetch the session ID.
Both devices then poll `src/app/interview/[id]/page.tsx` to confirm the `session_code` matches and status is "active".
This connects the existing Login flow (Ch 17) and Biometric Verification (Ch 18) into a shared session context.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** `session_code` must be 6 digits (numeric), unique per session, max 255 chars.
* **API/Database:** Use `POST /api/interviews/[id]/sync` for joining. Validate against `interview_sessions` table `session_code` column.
* **Testing Requirements:** Test valid code match, invalid code (404), expired session (400), and concurrent joins.
* **Infrastructure:** Use Serverless API routes (`src/app/api/.../route.ts`). No external WebSocket packages (Polling only).
* **Constraints:** Use Zod for schema validation. No new external packages allowed (Next.js, Tailwind, Zod only).

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

**Expected Outcomes:**
*   **Success:** Both devices display "Synced" on `src/app/interview/[id]/page.tsx` within 5 seconds of code entry.
*   **Failure:** Interviewee sees "Invalid Session Code" (404) if code does not match `interview_sessions` table.

**Verification Reminders:**
*   Ask your IDE to check for recursive loops in the polling logic.
*   Ensure JSON schemas in `src/schema/interview-schema.ts` match API payloads exactly.
*   Verify no external packages are introduced that violate the Tech Matrix.

---

<a id='step-22-chapter-22-build-audio-recording-screen'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='21'> Step 22: Chapter 22: Build Audio Recording Screen</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Run database migration to add `audio_ref` column (VARCHAR 255) to the `interview_sessions` table before coding.</li>
    <li>Ensure the local server is running on HTTPS to enable the browser MediaRecorder API.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This feature captures interview audio locally and links it to the session for subsequent blockchain hashing. It ensures raw data integrity before authentication, preventing AI deepfake substitution of voice data.

**User Experience (UX) Flow:**
*   **Page:** `src/app/interview/[id]/page.tsx`
*   **Interaction:** User clicks "Start Recording" (mic icon), sees waveform, then clicks "Stop".
*   **Feedback:** Status changes to "Processing Upload" then "Audio Saved".
*   **Connection:** This screen is embedded within the active interview session flow, directly following the Biometric Verification.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 22: Build Audio Recording Screen** feature.

#### 1. UX & Logic Description
The user interacts with a recording widget on `src/app/interview/[id]/page.tsx`.
Clicking start initializes the MediaRecorder API; clicking stop triggers a blob upload to `POST /api/interviews/[id]/audio`.
The UI must show recording state (red dot), time elapsed, and upload success/error.

#### 2. Technical Guardrails & Constraints
*   **Data Validation:** Audio file size < 50MB, MIME type `audio/webm` or `audio/mp3`, Duration > 1 second.
*   **API/Database:** Use `src/app/api/interviews/[id]/audio/route.ts` (Serverless).
    *   Payload: `{ audio_file: FormData }`.
    *   DB Update: Save `audio_ref` (URL/Path) in `interview_sessions` table.
    *   Errors: 400 (Invalid File), 404 (Session Not Found), 500 (Upload Fail).
*   **Testing Requirements:**
    *   Happy Path: Record > Stop > Upload > DB Update verified.
    *   Edge Case: Large file rejection, Network failure retry, HTTPS requirement check.
*   **Global State:** Do not use new packages; rely on Next.js, Zod, and Tailwind.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md` and Tech Matrix (No new packages).
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
4. Verify that `src/schema/audio-schema.ts` strictly validates the Zod constraints defined.
```

---

<a id='step-23-chapter-23-implement-speech-to-text-generation'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='22'> Step 23: Chapter 23: Implement Speech-to-Text Generation</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Obtain an API Key for a Speech-to-Text provider (e.g., OpenAI Whisper or AssemblyAI).</li>
    <li>Add the key to your `.env` file as `STT_API_KEY` and update `.env.example`.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step converts the recorded audio from Chapter 22 into text for blockchain anchoring and verification. It is necessary to create a human-readable transcript that can be hashed and stored on the Monad network.

**User Experience (UX) Flow:**
Users interact with the `src/app/interview/[id]/page.tsx` page after completing audio recording. They click a "Generate Transcript" button, triggering a loading state, followed by a display of the generated text.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 23: Implement Speech-to-Text Generation** feature.

#### 1. UX & Logic Description
This feature connects directly to the **Interview Recording Page** at `src/app/interview/[id]/page.tsx`.
The UI displays a "Generate Transcript" button that becomes active only after audio recording is confirmed.
Upon clicking, the client sends the `audio_ref` to the backend API, which processes the STT request.
The resulting text is saved to the database and displayed on the same page in a read-only text area.
This flow ensures the transcript is linked to the specific interview session ID and user.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** `transcript_text` must be a required string, max 10,000 characters. `audio_ref` must exist in `interview_sessions`.
* **API/Database:** Use endpoint `POST /api/interviews/[id]/transcribe`. Update `interview_sessions` table with `transcript_text` column.
* **Testing Requirements:** Test successful transcription flow (200 OK). Test missing audio reference (400 Bad Request). Test API failure (500 Internal Server Error).
* **AI Constraints:** Do not allow the AI to grade its own output; treat transcription as a generation step only.
* **Structured Outputs:** Define a strict Zod schema for the API response containing `transcript_text` and `status`.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

**Expected Outcomes:**
If successful, the API returns a 200 status with the transcribed text stored in the `interview_sessions` table.
If it fails, the API returns a 400 error for missing audio or 500 for STT service failure, showing an error message to the user.

**Data & Schema References:**
*   **Database Table:** `interview_sessions`
*   **New Column:** `transcript_text` (VARCHAR 10000)
*   **Existing Column:** `audio_ref` (VARCHAR 255)
*   **File Paths:** `src/app/api/interviews/[id]/transcribe/route.ts`, `src/schema/transcribe-schema.ts`, `src/app/interview/[id]/page.tsx`
*   **API Endpoint:** `POST /api/interviews/[id]/transcribe`
*   **Environment:** `STT_API_KEY` (from `.env`)

**Testing Mandate:**
*   **Happy Path:** Send valid `audio_ref`, verify `transcript_text` is saved and returned.
*   **Edge Case:** Send request without `audio_ref`, verify 400 Bad Request response.
*   **Edge Case:** Simulate STT provider failure, verify 500 Internal Server Error handling.

**Verification Reminders:**
*   Ask your IDE to check the code for errors (e.g., recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
*   Run 10 mock dry runs internally to ensure the code is safe and functional.

---

<a id='step-24-chapter-24-implement-speech-to-text-quality-check'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='23'> Step 24: Chapter 24: Implement Speech-to-Text Quality Check</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure `STT_API_KEY` is set in `.env` from Chapter 23 to retrieve confidence scores.</li>
    <li>Run database migration to add `transcript_quality_score` (INT) and `transcript_status` (ENUM) columns to `interview_sessions` table.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This feature validates the accuracy and completeness of the generated transcript before anchoring it to the blockchain. It prevents low-quality or AI-generated hallucinations from being permanently recorded as verified evidence.

**User Experience (UX) Flow:**
Users view the transcript quality status (Green/Red) on the `src/app/interview/[id]/page.tsx` review screen after recording. A progress indicator shows the quality check running before the "Verify on Blockchain" button becomes active.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 24: Implement Speech-to-Text Quality Check** feature.

#### 1. UX & Logic Description
The user navigates to `src/app/interview/[id]/page.tsx` after recording. The UI displays a "Quality Check" badge. Upon clicking, the system calls the backend to validate the `transcript_text` stored in the `interview_sessions` table. The backend calculates a quality score based on text length and punctuation consistency, then updates the `transcript_status` column. If the score is high, the status becomes 'verified'; otherwise, 'failed'.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** `transcript_quality_score` must be an integer between 0-100. `transcript_status` must be enum: 'pending', 'verified', 'failed'. `transcript_text` must be min 10 chars, max 10000.
* **API/Database:** Use `POST /api/interviews/[id]/transcript/quality` endpoint. Update `interview_sessions` table. Use `src/schema/interview-schema.ts` and new `src/schema/transcript-quality-schema.ts`.
* **Testing Requirements:** Test happy path (valid text returns 'verified'), edge case (empty text returns 'failed'), and DB update verification.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-25-chapter-25-build-transcript-display-screen'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='24'> Step 25: Chapter 25: Build Transcript Display Screen</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure the database migration for Chapter 23/24 (`transcript_text`, `transcript_status`, `transcript_quality_score` columns) has been applied to your local PostgreSQL instance.</li>
    <li>Verify `DB_CONNECTION_STRING` in `.env` is active and points to the correct schema.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This screen allows users to view the finalized interview transcript alongside its blockchain verification status and quality score. If successful, users see readable text with a green verification badge; if failed, they see an error state with no data.

**User Experience (UX) Flow:**
Users navigate from `src/app/interview/[id]/page.tsx` to the transcript section after recording completes. The layout displays the text in a scrollable container with a status badge indicating "Verified", "Pending", or "Failed".

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 25: Build Transcript Display Screen** feature.

#### 1. UX & Logic Description
The user views the `src/app/interview/[id]/page.tsx` screen which fetches transcript data via `GET /api/interviews/[id]/transcript`. The UI renders `transcript_text` in a text block and `transcript_status` as a colored badge (Green=Verified, Yellow=Pending, Red=Failed). It connects directly to the Interview Session page created in Chapter 19.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** `transcript_text` (VARCHAR 10000, required), `transcript_status` (Enum: 'verified' | 'pending' | 'failed'), `monad_tx_hash` (VARCHAR 255).
* **API/Database:** Use `GET /api/interviews/[id]/transcript` endpoint. Read from `interview_sessions` table (columns: `id`, `transcript_text`, `transcript_status`, `monad_tx_hash`). Return 404 if session not found, 400 if validation fails.
* **Testing Requirements:** Test happy path (text renders), edge case (empty transcript shows placeholder), and error path (404 returns error message).

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-26-chapter-26-build-blockchain-hash-signing-screen'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='25'> Step 26: Chapter 26: Build Blockchain Hash Signing Screen</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Verify `MONAD_RPC_URL` is present in your `.env` file with a valid Mainnet or Testnet RPC endpoint.</li>
    <li>Ensure your local database migration has created the `blockchain_records` table as defined in Chapter 9.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This feature anchors the verified interview transcript hash to the Monad blockchain, creating an immutable record that proves the data has not been altered by AI or tampering. It is necessary to fulfill the core product promise of deepfake-resistant interview verification.

**User Experience (UX) Flow:**
The user navigates to the Interview Detail page (`src/app/interview/[id]/page.tsx`) where they see a "Sign to Blockchain" button after transcript generation. Upon clicking, the system signs the hash, displays a loading spinner, and updates the UI with the transaction hash and verification badge upon success.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 26: Build Blockchain Hash Signing Screen** feature.

#### 1. UX & Logic Description
[Provide a highly descriptive, layman explanation of the UI layout, interactions, and user flow. Explicitly state which pages this connects to.]
* **Page:** `src/app/interview/[id]/page.tsx` (Add "Anchor to Blockchain" section).
* **Interaction:** User clicks button -> API Call -> Loading State -> Success/Fail Toast.
* **Cohesion:** Reuses existing `src/app/interview/[id]/page.tsx` layout; does not create new navigation routes.
* **Visual:** Button disabled if `transcript_text` is missing; shows hash on success.

#### 2. Technical Guardrails & Constraints
[Explicitly list specific constraints the AI MUST follow when generating the implementation plan:]
* **Data Validation:** Use `src/schema/blockchain-sign-schema.ts` (Zod) for API payload (`interview_id` required, max 255 chars).
* **API/Database:** Use `POST /api/interviews/[id]/sign` (Serverless); Update `interview_sessions` (`monad_tx_hash`); Insert `blockchain_records`.
* **Testing Requirements:** Test Happy Path (RPC success, DB update); Edge Case (RPC timeout, Duplicate signing, Missing transcript).
* **Global State:** Strictly use Next.js, Zod, Tailwind, and Serverless routes (No external packages per Tech Matrix).
* **Separation of Concerns:** Ensure signing logic is distinct from verification logic (Chapter 14).
* **Structured Outputs:** API response must match Zod schema strictly.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

**Success Expectations:**
The "Sign" button triggers an API call that returns a transaction hash, updating the UI to show a green "Verified" badge and the hash string.
**Failure Expectations:**
If the RPC fails or the interview is already signed, the API returns a 400 or 500 error, and the UI displays a red toast message without updating the database.

**Data Validation Mandate:**
*   **API Payload:** `interview_id` (string, required, max 255 chars).
*   **DB Columns:** `monad_tx_hash` (interview_sessions, varchar 255), `tx_hash` (blockchain_records, varchar 255).
*   **Constraints:** Prevent duplicate signing if `monad_tx_hash` is already populated (Return 409 Conflict).

**Testing Mandate:**
*   **Unit Test:** Validate Zod schema rejects missing `interview_id`.
*   **Integration Test:** Mock `MONAD_RPC_URL` to simulate transaction success and verify `interview_sessions` update.
*   **Edge Case:** Simulate RPC timeout to ensure API returns 503 Service Unavailable gracefully.

**Verification Reminders:**
*   **IDE Check:** Ask your IDE to scan for recursive loops in the signing logic and ensure JSON schemas match API routes.
*   **Dry Runs:** Run 10 internal mock dry runs to ensure the transaction hash generation is deterministic and safe.
*   **Schema Check:** Verify `src/schema/blockchain-sign-schema.ts` aligns exactly with `src/app/api/interviews/[id]/sign/route.ts` input.

---

<a id='step-27-chapter-27-build-transaction-broadcast-screen'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='26'> Step 27: Chapter 27: Build Transaction Broadcast Screen</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure `MONAD_RPC_URL` is set in your `.env` and `.env.example` files as defined in Chapter 3.</li>
    <li>Verify the `interview_sessions` table has the `monad_tx_hash` column and `blockchain_records` table exists per Chapter 8 & 9.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This screen finalizes the blockchain commitment by broadcasting the signed transaction to the Monad network and displaying the immutable proof hash. It ensures the interview transcript is permanently anchored against AI deepfakes.

**User Experience (UX) Flow:**
The user navigates from `src/app/interview/[id]/page.tsx` to `src/app/interview/[id]/broadcast/page.tsx` after signing. They see a loading state for network confirmation, then a success badge with the TX hash upon completion.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 27: Build Transaction Broadcast Screen** feature.

#### 1. UX & Logic Description
The UI displays a real-time status indicator (Pending, Confirmed, Failed) while the server broadcasts the signed hash to Monad. Upon success, it redirects the user back to `src/app/interview/[id]/page.tsx` showing the verified badge. This connects directly from the signing completion state in Chapter 26.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** `monad_tx_hash` must be string, max 255 chars. `status` must be enum ['pending', 'confirmed', 'failed'].
* **API/Database:** Use `POST /api/interviews/[id]/broadcast` route. Update `interview_sessions` (monad_tx_hash) and `blockchain_records` (tx_hash, status).
* **Testing Requirements:** Test happy path (RPC success), edge case (RPC timeout 500), and validation error (missing interview ID 404).
* **Global State:** Use only Next.js, Zod, Tailwind, and existing DB connections. No new packages allowed.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-28-chapter-28-build-record-verification-screen'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='27'> Step 28: Chapter 28: Build Record Verification Screen</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure `MONAD_RPC_URL` is configured in `.env` as defined in Chapter 26.</li>
    <li>Confirm `blockchain_records` table exists with `status` enum (pending, confirmed, failed) per Chapter 27.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This feature allows users to visually confirm the authenticity of an interview transcript against the Monad blockchain. It closes the verification loop by displaying transaction status and hash, proving the data has not been altered.

**User Experience (UX) Flow:**
*   **Entry Points:** Users navigate from `src/app/dashboard/page.tsx` (Interview List) or `src/app/interview/[id]/page.tsx` (Active Interview) to the verification screen.
*   **Visuals:** Display a clear status badge (Verified/Pending/Failed), the Transaction Hash, and a "Refresh Status" button.
*   **Navigation:** Successful verification links back to the Transcript Display Screen (`src/app/interview/[id]/page.tsx`).

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 28: Build Record Verification Screen** feature.

#### 1. UX & Logic Description
Build a Next.js page at `src/app/verify/[id]/page.tsx` that fetches interview verification status via `GET /api/interviews/[id]/verification`. The UI must display a status badge (Verified, Pending, Failed) and the Monad Transaction Hash (`monad_tx_hash`). Users can navigate to this page from the Dashboard or Interview Detail screen. If the interview ID is invalid, redirect to the 404 page.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Enforce Zod schema at `src/schema/verification-schema.ts` (id: required, tx_hash: max 255 chars, status: enum 'verified' | 'pending' | 'failed').
* **API/Database:** Use existing endpoint `GET /api/interviews/[id]/verification`. Query `interview_sessions` and `blockchain_records` tables. Handle 404 (Interview Not Found) and 500 (Server Error) gracefully.
* **Testing Requirements:** Test happy path (Verified status), edge cases (Pending status, Failed status, Missing ID). Verify no new external packages are added (Tech Matrix: Next.js, Zod, Tailwind only).
* **Safety:** Ensure no recursive loops in API calls. Validate JSON response against Zod schema before rendering.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md` and Tech Matrix (No new packages).
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
4. Verify that `src/app/verify/[id]/page.tsx` correctly consumes `src/app/api/interviews/[id]/verification/route.ts`.
5. Confirm `src/schema/verification-schema.ts` matches the API response structure exactly.
```

---

<a id='step-29-chapter-29-build-admin-dashboard-screen'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='28'> Step 29: Chapter 29: Build Admin Dashboard Screen</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure a user with admin privileges exists in the `users` table (e.g., set `role = 'admin'` or note specific email in `.env` as `ADMIN_EMAIL`).</li>
    <li>Verify `DB_CONNECTION_STRING` and `JWT_SECRET` are populated in `.env` before running migrations or starting the server.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This screen provides administrators with a centralized view to monitor interview integrity, blockchain transaction statuses, and user activity. It is necessary to ensure system health and detect potential deepfake or verification failures across the platform.

**User Experience (UX) Flow:**
Admins access this via `/admin/dashboard` after authentication, viewing a table of interview sessions with status indicators (verified/pending/failed). This connects to the Login Screen for auth and the Verification Screen (`/verify/[id]`) for detailed audit trails.

- **Connected Pages:** `/login`, `/admin/dashboard`, `/verify/[id]`
- **Database Tables:** `users`, `interview_sessions`, `blockchain_records`
- **API Endpoints:** `GET /api/admin/dashboard`
- **File Paths:** `src/app/admin/dashboard/page.tsx`, `src/app/api/admin/dashboard/route.ts`
- **Tech Stack:** Next.js, Zod, Tailwind, PostgreSQL (Serverless)
- **Constraints:** Max 255 chars for hashes, Enum status for blockchain records

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 29: Build Admin Dashboard Screen** feature.

#### 1. UX & Logic Description
Build a protected admin page at src/app/admin/dashboard/page.tsx displaying a table of interview sessions.
The table must show user_id, interview status, monad_tx_hash, and blockchain_record status.
Clicking a row navigates to src/app/verify/[id]/page.tsx for deep audit.
The page fetches data from GET /api/admin/dashboard route.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Use Zod for API response (status enum: pending/confirmed/failed, tx_hash max 255 chars).
* **API/Database:** GET /api/admin/dashboard returns JSON; Query users, interview_sessions, and blockchain_records tables.
* **Testing Requirements:** Test auth bypass (401), empty data state (200 OK with empty array), and valid data rendering.
* **Global State:** Use only Next.js, Zod, Tailwind, and PostgreSQL (No new packages).
* **Infrastructure:** Use Serverless API routes for the endpoint.

#### 3. Action Requested
Please review the relevant files and generate an implementation_plan.md for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global PROJECT_RULES.md.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
4. Verify that the Admin Dashboard correctly filters interview_sessions by admin privileges.
5. Ensure blockchain_records status enum matches 'pending', 'confirmed', or 'failed'.
```

**Success Expectations:**
If successful, the admin dashboard loads a secure table showing real-time interview verification statuses. If it fails, the user receives a 401 Unauthorized error or a 500 Server Error due to DB connection issues.

**Testing Mandate:**
- Verify 401 response when accessing `/admin/dashboard` without a valid JWT token.
- Verify 200 response with empty array when no interviews exist in `interview_sessions`.
- Verify `monad_tx_hash` truncation does not break UI layout (max 255 chars).
- Verify navigation to `/verify/[id]` works from table row click.

**Verification Reminders:**
- Ask your IDE to check the code for errors (e.g. recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
- Run 10 mock dry runs internally to ensure the code is safe.
- Ensure Zod schemas in `src/schema/...` match the actual API response structure exactly.

---

<a id='step-30-chapter-30-create-implementation-plan-document'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='29'> Step 30: Chapter 30: Create Implementation Plan Document</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Create the `docs/` directory in the project root if it does not already exist.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step consolidates all architectural decisions from Chapters 1-29 into a single reference document to ensure alignment before production deployment. It is necessary to prevent drift between the codebase and the original design specifications.

**Expected Outcome:**
Success creates a comprehensive `implementation_plan.md` matching all schemas and API definitions. Failure results in a plan missing critical API or DB definitions that break future development.

**User Experience (UX) Flow:**
This feature connects to the `docs/implementation_plan.md` file for developer reference. It does not impact user-facing pages like `src/app/interview/[id]/page.tsx`.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 30: Create Implementation Plan Document** feature.

#### 1. UX & Logic Description
This feature generates a central documentation file at `docs/implementation_plan.md`. It connects to the project root for developer reference, not user-facing pages. The AI must review all previous schema and API files to ensure accuracy.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** The plan must accurately list all Zod schemas (e.g., `src/schema/interview-schema.ts`) and DB columns (e.g., `interview_sessions.monad_tx_hash`).
* **API/Database:** Reference exact endpoints like `/api/interviews/start` and tables like `blockchain_records`.
* **Testing Requirements:** Verify the document lists all 29 previous chapters and matches the Tech Matrix (Next.js, Zod, Tailwind, PostgreSQL).
* **Global State:** Adhere strictly to the Tech Matrix; do not introduce new packages.
* **Structured Outputs:** The document must follow a strict Markdown structure defined in the prompt.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-31-chapter-31-run-pre-flight-impact-analysis'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='30'> Step 31: Chapter 31: Run Pre-Flight Impact Analysis</label>

**Purpose (Why we are building this):**
This feature validates interview session integrity (biometrics, transcript quality) before blockchain commitment to prevent failed transactions. It ensures data readiness, saving costs and maintaining trust in the verification system.

**User Experience (UX) Flow:**
This feature connects to the `src/app/interview/[id]/page.tsx` dashboard. Users trigger a "Run Pre-Flight Check" button which displays a status modal before allowing the "Sign/Broadcast" action.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 31: Run Pre-Flight Impact Analysis** feature.

#### 1. UX & Logic Description
The user clicks a "Run Pre-Flight Check" button on the `src/app/interview/[id]/page.tsx` dashboard.
This triggers an API call to validate the session state before blockchain broadcasting.
The UI displays a loading state, then a success/fail modal with specific reasons (e.g., missing biometric, low quality).
This connects directly to the `src/app/interview/[id]/broadcast/page.tsx` flow.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** `biometric_hash` (required, max 255 chars), `transcript_quality_score` (required, min 80), `status` (enum: pending/ready/failed).
* **API/Database:** Use `POST /api/interviews/[id]/pre-flight`. Read `interview_sessions` table. Response must return a Zod-validated JSON object.
* **Testing Requirements:** Test happy path (all checks pass), edge case (missing biometric hash), and edge case (low transcript quality score).
* **Infrastructure:** Use standard serverless API routes (`src/app/api/.../route.ts`). No queues.
* **Stack:** Strictly Next.js, Zod, Tailwind, PostgreSQL. No new external packages.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
4. Verify that the API response strictly matches the Zod schema defined in `src/schema/pre-flight-schema.ts`.
```

---

<a id='step-32-chapter-32-test-database-schema-migrations'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='31'> Step 32: Chapter 32: Test Database Schema Migrations</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure `DB_CONNECTION_STRING` is correctly set in `.env` and `.env.example` before running migrations.</li>
    <li>Verify the chosen migration tool (Prisma/Drizzle) is initialized in `package.json` as per Chapter 7.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step validates that all database schema definitions from previous chapters apply correctly to the PostgreSQL instance without syntax errors or constraint violations. It prevents runtime failures in authentication and interview flows caused by missing tables or mismatched columns.

**User Experience (UX) Flow:**
This is a backend infrastructure step with no direct user interface; however, successful execution ensures stability for `src/app/dashboard/page.tsx` and `src/app/admin/dashboard/page.tsx`. Failure results in 500 errors on all data-dependent pages like `src/app/interview/[id]/page.tsx`.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 32: Test Database Schema Migrations** feature.

#### 1. UX & Logic Description
This feature is a backend validation process ensuring the database tables match the Zod schemas defined in `src/schema/`. It connects logically to all data-driven pages like `src/app/dashboard/page.tsx` by ensuring the underlying `users` and `interview_sessions` tables exist. The flow involves running migration scripts against the local PostgreSQL instance defined in `src/config/db-connection.ts`.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** All text fields must enforce `VARCHAR 255` (e.g., `email`, `biometric_hash`); Enums like `status` must strictly match `pending`, `confirmed`, `failed`.
* **API/Database:** Migrations must align with `interview_sessions` (columns: `user_id`, `monad_tx_hash`) and `blockchain_records` (columns: `tx_hash`, `status`).
* **Testing Requirements:** Test migration `up` (create tables), `down` (rollback), and constraint violation (e.g., inserting invalid `status` enum).

#### 3. Action Requested
Please review the relevant files in `src/schema/` and `src/config/` and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

**Expected Outcomes:**
*   **Success:** Migration script completes with 200 OK status, tables `users`, `interview_sessions`, `blockchain_records` exist with correct columns.
*   **Failure:** Migration throws 500 error, logs show SQL syntax errors or foreign key constraint violations.

**Data Validation Mandate:**
*   `users.email`: Required, Max 255 chars, Unique.
*   `interview_sessions.biometric_hash`: Required, Max 255 chars.
*   `blockchain_records.status`: Enum ['pending', 'confirmed', 'failed'], Default 'pending'.

**Testing Mandate:**
*   **Happy Path:** Run migration, verify tables exist via `SELECT * FROM users`.
*   **Edge Case:** Attempt insert with invalid `status` enum to verify DB rejects it.
*   **Rollback:** Run migration down command to ensure tables drop cleanly.

**Verification Reminders:**
*   Ask your IDE to check `src/config/db-connection.ts` for recursive connection loops.
*   Ensure `src/schema/*.ts` Zod definitions match the SQL migration columns exactly.
*   Run 10 mock dry runs internally to ensure the code is safe and functional.

---

<a id='step-33-chapter-33-test-api-contract-compliance'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='32'> Step 33: Chapter 33: Test API Contract Compliance</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure the local PostgreSQL database is migrated and seeded with test data for `users`, `interview_sessions`, and `blockchain_records` tables.</li>
    <li>Verify `.env` contains `DB_CONNECTION_STRING`, `MONAD_RPC_URL`, and `JWT_SECRET` before running compliance tests.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step validates that all implemented API endpoints strictly adhere to the Zod schemas and database constraints defined in Chapters 10-29. It prevents runtime failures and security vulnerabilities by ensuring data contracts match frontend expectations before deployment.

**User Experience (UX) Flow:**
This feature impacts all API-dependent pages including `src/app/dashboard/page.tsx`, `src/app/interview/[id]/page.tsx`, and `src/app/verify/[id]/page.tsx`. Successful compliance ensures users see accurate data without loading errors or validation failures during interview sessions.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 33: Test API Contract Compliance** feature.

#### 1. UX & Logic Description
This step involves verifying that serverless API routes return correct status codes and payloads matching their Zod schemas. It connects to the entire application flow, specifically validating data integrity for the `src/app/dashboard/page.tsx` and `src/app/verify/[id]/page.tsx` pages. The AI must simulate requests to critical endpoints and compare responses against `src/schema/*.ts` definitions.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** All string fields (e.g., `biometric_hash`, `monad_tx_hash`) must strictly adhere to max 255 character limits defined in `src/schema/*.ts`.
* **API/Database:** Test endpoints `/api/auth/login`, `/api/interviews/start`, and `/api/interviews/[id]/verification` against `users`, `interview_sessions`, and `blockchain_records` tables.
* **Testing Requirements:** Validate 200 OK for valid payloads, 400 Bad Request for schema violations, and 404 Not Found for missing resources.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-34-chapter-34-test-biometric-authentication-flow'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='33'> Step 34: Chapter 34: Test Biometric Authentication Flow</label>

**Purpose (Why we are building this):**
This step validates that biometric hashes are correctly captured, stored, and retrievable before blockchain anchoring. It ensures the dual-phone authentication flow is functional and prevents deepfake injection by verifying data integrity.

**Expected Outcome:**
Success returns a valid hash status and confirms database storage. Failure returns a 404 or 400 error if the session or hash is missing.

**User Experience (UX) Flow:**
*   **Page:** `src/app/interview/[id]/page.tsx`
*   **Action:** User clicks "Verify Biometric" during the interview session.
*   **Visual:** Loading spinner followed by a green checkmark or red error message.
*   **Connection:** Ties directly to the Biometric Verification Screen (Chapter 18) and Interview Start (Chapter 19).

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 34: Test Biometric Authentication Flow** feature.

#### 1. UX & Logic Description
This feature adds a validation check to `src/app/interview/[id]/page.tsx` to confirm the `biometric_hash` is stored in `interview_sessions`. The UI triggers a GET request to verify the hash exists and matches the session ID. This connects directly to the existing Interview Session page.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** `biometric_hash` must be max 255 chars, required. `interview_id` must be valid UUID.
* **API/Database:** Use GET `/api/interviews/[id]/biometric-verify`. Query `interview_sessions` table.
* **Testing Requirements:** Test happy path (hash exists), 404 (session missing), 400 (invalid hash format).
* **Stack:** Next.js, Zod, Tailwind, PostgreSQL ONLY. No new packages.
* **Infrastructure:** Serverless API route.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md` and Tech Matrix (No new packages).
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
4. Verify `src/schema/biometric-verify-schema.ts` matches `interview_sessions` columns exactly.
```

---

<a id='step-35-chapter-35-test-dual-phone-sync-connection'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='34'> Step 35: Chapter 35: Test Dual Phone Sync Connection</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Ensure the local development server is accessible via LAN IP or a tunnel (e.g., ngrok) to allow a second physical device to connect for sync testing.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step validates that two separate devices can successfully join and synchronize state within the same interview session using a shared `session_code`. It is necessary to confirm the dual-phone workflow functions before proceeding to blockchain anchoring.

**User Experience (UX) Flow:**
Users navigate from `src/app/interview/start/page.tsx` to generate a session code, then to `src/app/interview/join/page.tsx` to input it on a second device. Both devices converge on `src/app/interview/[id]/page.tsx` where they poll for synchronized state updates.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 35: Test Dual Phone Sync Connection** feature.

#### 1. UX & Logic Description
Implement a polling mechanism where two clients connect to `src/app/interview/[id]/page.tsx` using a shared `session_code`. The Host device initiates the session at `src/app/interview/start/page.tsx`, and the Guest joins via `src/app/interview/join/page.tsx`. Both devices must poll the API endpoint `POST /api/interviews/[id]/sync` to verify connection state and synchronize interview status in real-time.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** `session_code` must be VARCHAR 255 (required), `interview_id` must be UUID (required). Use `src/schema/interview-schema.ts` for Zod validation.
* **API/Database:** Use serverless route `src/app/api/interviews/[id]/sync/route.ts`. Update `interview_sessions` table `session_code` column. Return 200 OK on success, 400 Bad Request on validation failure, 404 Not Found if session missing.
* **Testing Requirements:** Test concurrent polling from two devices, invalid session code rejection, and session timeout handling. Ensure no WebSockets are used; rely strictly on HTTP polling.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-36-chapter-36-test-blockchain-transaction-signing'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='35'> Step 36: Chapter 36: Test Blockchain Transaction Signing</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Update the `.env` file to set `MONAD_RPC_URL` to a Testnet endpoint (e.g., Monad Testnet) before testing transaction signing.</li>
    <li>Ensure `DB_CONNECTION_STRING` is configured and accessible by the serverless API routes.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step validates that the interview transcript hash is correctly signed and stored locally before broadcasting to the Monad network. It ensures data integrity and prevents invalid transactions from being submitted to the blockchain.

**User Experience (UX) Flow:**
*   The user interacts with the `src/app/interview/[id]/page.tsx` interface to initiate the signing process.
*   A status indicator updates to reflect the signing state (pending, signed, failed) without leaving the page.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 36: Test Blockchain Transaction Signing** feature.

#### 1. UX & Logic Description
The user triggers a signing action on the Interview Page (`src/app/interview/[id]/page.tsx`).
This connects to the existing API route `POST /api/interviews/[id]/sign` to validate the hash.
The system must update the `interview_sessions` table with `monad_tx_hash` and log to `blockchain_records`.
Display a success or error toast based on the API response status.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Enforce Zod schema in `src/schema/blockchain-sign-schema.ts` (interview_id UUID, hash max 255 chars).
* **API/Database:** Use `POST /api/interviews/[id]/sign` endpoint; return 400 for validation errors, 404 if session missing.
* **Testing Requirements:** Verify 1) Hash generation matches input, 2) DB `monad_tx_hash` updates correctly, 3) 400 error triggers on invalid payload.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
4. Verify that `src/app/api/interviews/[id]/sign/route.ts` uses serverless patterns and handles `MONAD_RPC_URL` from `src/config/env.ts`.
5. Confirm `interview_sessions` and `blockchain_records` tables are updated with correct transaction hashes and status enums.
```

---

<a id='step-37-chapter-37-test-transcript-hash-verification'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='36'> Step 37: Chapter 37: Test Transcript Hash Verification</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Verify `MONAD_RPC_URL` exists in `.env` and `.env.example` to enable blockchain hash verification.</li>
    <li>Ensure `DB_CONNECTION_STRING` is active to access `interview_sessions` and `blockchain_records` tables.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step validates the integrity of the interview transcript by comparing the local hash against the Monad blockchain record. It prevents AI deepfake alteration by cryptographically proving the transcript matches the signed on-chain record.

**User Experience (UX) Flow:**
Users navigate to `src/app/verify/[id]/page.tsx` to see a verification badge (Green/Red). The system fetches the transcript, hashes it, and compares it with the `monad_tx_hash` stored in `interview_sessions`.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 37: Test Transcript Hash Verification** feature.

#### 1. UX & Logic Description
The user visits the verification page (`src/app/verify/[id]/page.tsx`) linked from the dashboard. The frontend calls the API (`GET /api/interviews/[id]/verification`) to check if the local transcript hash matches the `monad_tx_hash` in the database and on-chain. The UI displays a clear 'Verified' or 'Failed' status based on the hash comparison result.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** `tx_hash` (VARCHAR 255, required), `status` (enum: verified/pending/failed). Use Zod at `src/schema/verification-schema.ts`.
* **API/Database:** Use `GET /api/interviews/[id]/verification` endpoint. Query `interview_sessions` (monad_tx_hash, transcript_ref) and `blockchain_records` (tx_hash, status).
* **Testing Requirements:** Test hash match (200 OK, status: verified) and hash mismatch (400 Bad Request, status: failed). Ensure 404 for missing interview IDs.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-38-chapter-38-test-end-to-end-interview-flow'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='37'> Step 38: Chapter 38: Test End-to-End Interview Flow</label>

*   **Purpose (Why we are building this):**
    *   This feature validates the complete integration of authentication, biometrics, and blockchain anchoring.
    *   It ensures data integrity across all previous modules before production.

*   **User Experience (UX) Flow:**
    *   Users navigate `src/app/dashboard/page.tsx` to start, `src/app/interview/[id]/page.tsx` for the session, and `src/app/verify/[id]/page.tsx` for results.
    *   The flow connects dual-phone sync, audio recording, and blockchain verification screens seamlessly.

*   **Expected Outcome:**
    *   Success confirms all API routes return 200 OK with valid data.
    *   Failure indicates disconnects between frontend, database, or blockchain RPC.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 38: Test End-to-End Interview Flow** feature.

#### 1. UX & Logic Description
Provide a highly descriptive, layman explanation of the UI layout, interactions, and user flow. Explicitly state which pages this connects to.
*   **Pages:** `src/app/dashboard/page.tsx`, `src/app/interview/[id]/page.tsx`, `src/app/verify/[id]/page.tsx`.
*   **Flow:** Login -> Start Interview -> Biometric -> Dual Phone Sync -> Record Audio -> Transcribe -> Sign Blockchain -> Verify.
*   **Logic:** Ensure state persists across pages using Next.js App Router server actions or API calls.

#### 2. Technical Guardrails & Constraints
Explicitly list specific constraints the AI MUST follow when generating the implementation plan:
*   **Data Validation:** `interview_sessions` table requires `user_id` (UUID), `biometric_hash` (VARCHAR 255), `monad_tx_hash` (VARCHAR 255). Use Zod in `src/schema/interview-schema.ts`.
*   **API/Database:** Use Serverless API routes (`src/app/api/interviews/[id]/route.ts`). Connect to `interview_sessions` and `blockchain_records` tables.
*   **Testing Requirements:** Test Happy Path (full flow), Edge Cases (sync timeout, blockchain RPC failure).
*   **Infrastructure:** Use standard serverless API routes. Do not use WebSockets.
*   **AI Concerns:** Do not allow an AI to grade its own output; separate Generate and Evaluate operations.
*   **Structured Outputs:** If generating structured data, define a strict JSON Schema using Zod.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-39-chapter-39-document-deployment-instructions'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='38'> Step 39: Chapter 39: Document Deployment Instructions</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Create a hosting account on Vercel, Render, or Railway before writing code.</li>
    <li>Generate database credentials for your production PostgreSQL instance to populate `DB_CONNECTION_STRING`.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This step ensures the application is accessible to end-users via a live URL with secure environment variables. It validates that all serverless routes and database connections function correctly in production.

**User Experience (UX) Flow:**
This feature does not change user-facing pages but enables access to `src/app/dashboard/page.tsx`, `src/app/interview/[id]/page.tsx`, and `src/app/verify/[id]/page.tsx`. It connects the local development environment to the production hosting platform.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 39: Document Deployment Instructions** feature.

#### 1. UX & Logic Description
This feature generates a comprehensive deployment guide connecting local development to production hosting. It explicitly links the configuration in `src/config/env.ts` to the live environment variables required by `src/app/api/auth/login/route.ts` and other serverless routes. The output must be a `DEPLOYMENT.md` file that ensures users can access `src/app/dashboard/page.tsx` and `src/app/verify/[id]/page.tsx` securely.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** Ensure `DB_CONNECTION_STRING` and `MONAD_RPC_URL` are marked as required in `DEPLOYMENT.md` with max 255 char limits per `src/config/env.ts`.
* **API/Database:** Document that `users`, `interview_sessions`, and `blockchain_records` tables must be migrated before deployment.
* **Testing Requirements:** Verify that `/api/auth/login` returns 200 OK and `/api/interviews/start` returns 401 without valid JWT in the live environment.
* **Infrastructure:** Confirm no WebSockets are used; strictly adhere to Serverless API routes as per Chapter 15.
* **Package Constraints:** Do not introduce new packages; rely only on Next.js, Zod, Tailwind, and PostgreSQL.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
```

---

<a id='step-40-chapter-40-create-user-onboarding-guide'></a>
## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='39'> Step 40: Chapter 40: Create User Onboarding Guide</label>

<div class="manual-action-alert">
<h4>⚠️ Manual Developer Action Required</h4>
<ul>
    <li>Run database migration command to add `onboarding_completed` column: `npx prisma migrate dev --name add_onboarding_completed`.</li>
    <li>Ensure `DB_CONNECTION_STRING` in `.env` points to a local or remote PostgreSQL instance accessible by the migration tool.</li>
</ul>
</div>

**Purpose (Why we are building this):**
This feature reduces user drop-off by explaining the dual-phone and biometric verification process before interview start. It ensures users understand security measures, increasing trust and completion rates.

**User Experience (UX) Flow:**
Users access `src/app/onboarding/page.tsx` via links on `src/app/login/page.tsx` and `src/app/register/page.tsx`. It displays step-by-step guides connecting to `src/app/dashboard/page.tsx` upon completion.

### Phase 1: Planning (Copy & Paste to your AI first)
```text
We are building the **Chapter 40: Create User Onboarding Guide** feature.

#### 1. UX & Logic Description
Create a static informational page at `src/app/onboarding/page.tsx` that explains the biometric and blockchain verification steps. Include a "Complete Guide" button that calls the API to update the user's `onboarding_completed` status and redirects to `src/app/dashboard/page.tsx`. Ensure the design uses Tailwind classes consistent with `src/app/login/page.tsx`.

#### 2. Technical Guardrails & Constraints
* **Data Validation:** `onboarding_completed` field must be a Boolean defaulting to `false` in the `users` table. API payload requires `user_id` (UUID) and `onboarding_completed` (Boolean).
* **API/Database:** Use `PATCH /api/users/onboarding-complete` serverless route. Update `users` table column `onboarding_completed`. Use `src/schema/onboarding-schema.ts` for Zod validation.
* **Testing Requirements:** Test happy path (status updates to true), edge case (status update when already true returns 200), and validation failure (missing `user_id` returns 400).
* **Constraints:** Do not introduce new external packages. Use Next.js, Zod, Tailwind, and existing `DB_CONNECTION_STRING`. Ensure separation of Generate and Evaluate operations if AI is used for content.

#### 3. Action Requested
Please review the relevant files and generate an `implementation_plan.md` for this feature. Do not write code until the plan is approved.
```

### Phase 2: Execution & Verification (Copy & Paste after approving the plan)
```text
I have approved the implementation plan. 

Please execute the plan and write the code. 
Before finalizing your work:
1. Check the code for common errors (recursive loops, disconnects between JSON schemas and natural prompts, formatting errors).
2. Ensure you have respected the global `PROJECT_RULES.md`.
3. Run 10 mock dry runs internally to ensure the code is safe and functional.
4. Explicitly verify that the Zod schema in `src/schema/onboarding-schema.ts` matches the API payload requirements exactly.
5. Confirm that `src/app/onboarding/page.tsx` correctly links to `src/app/dashboard/page.tsx` after API success.
```

---



---

## Architect's Final Audit

### Potential Risks & Overlapping Logic
*   **Security Model Contradiction (Blockchain Signing):** Steps 26–27 imply server-side signing (`POST /api/.../sign` updates `monad_tx_hash`). If the server holds the private key to sign transactions, the system centralizes trust, undermining the "individual verification" value proposition. Users should ideally sign client-side, or a secure MPC wallet flow must be defined.
*   **Feature Claim vs. Implementation:** The "Biometric Verification" (Step 18) generates a hash of a camera frame using Web Crypto API. This verifies *camera presence*, not human identity (e.g., FaceID or liveness detection). This does not robustly combat deepfakes as claimed in the Executive Purpose.
*   **Cost vs. Tier Conflict:** Step 4 mandates "Free Tier Hosting," but Step 23 requires a paid STT API Key (`STT_API_KEY`). Free serverless tiers often have execution time limits that may timeout large audio processing tasks, and STT APIs are rarely free at production scale.
*   **Data Redundancy:** The `monad_tx_hash` is stored in both `interview_sessions` (Step 6/8) and `blockchain_records` (Step 9/27). This creates a risk of desynchronization; if one updates and the other fails, audit integrity is compromised.

### Skipped or Incomplete Logic
*   **Wallet Connection Flow:** There is no step defining how the signing key is accessed (Client-side Wallet like MetaMask vs. Server-side Key). Step 26 assumes an API call can sign without detailing the authentication mechanism for the blockchain signer.
*   **QR Code Reliability:** Step 20 suggests generating QR codes via "pure JS/CSS generation" to avoid packages. This is high-risk for reliability and compatibility; a lightweight, proven library is standard practice.
*   **RBAC Middleware:** Step 29 requires Admin access, but no explicit middleware step exists to validate `role='admin'` on API routes before Step 29 execution.

### Strict Advice for Developers
1.  **Resolve Blockchain Key Management:** Decide immediately if signing is Client-Side (Web3.js/Ethers) or Server-Side. If Server-Side, implement a secure Vault/Secrets Manager for the private key; do not hardcode `MONAD_RPC_URL` or keys in `.env` for production.
2.  **Validate STT Cost Model:** Confirm the chosen STT provider has a sustainable free tier or budget allocation before committing to Step 23; otherwise, the "Free Tier" hosting goal is unachievable.
3.  **Consolidate Transaction Records:** Remove the `monad_tx_hash` column from `interview_sessions` and rely solely on the `blockchain_records` table linked via Foreign Key to prevent state desynchronization during transaction broadcasting.