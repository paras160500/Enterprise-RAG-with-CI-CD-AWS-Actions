<div align="center">

# 🧠 Enterprise RAG with CI/CD on AWS

### Secure, tenant-aware Retrieval-Augmented Generation — from document upload to production deployment

![Architecture Diagram](diagram.png)

*Document ingestion • Tenant-isolated vector search • Guardrails • Human-in-the-loop approvals • Audit trail • Observability • Docker • GitHub Actions → ECR → EC2*

<br/>

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white&style=for-the-badge)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white&style=for-the-badge)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Workflow-1C3C3C?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![AWS Bedrock](https://img.shields.io/badge/Amazon%20Bedrock-FF9900?logo=amazon-aws&logoColor=white&style=for-the-badge)](https://aws.amazon.com/bedrock/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-000000?style=for-the-badge)](https://www.pinecone.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white&style=for-the-badge)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white&style=for-the-badge)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?logo=githubactions&logoColor=white&style=for-the-badge)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](./LICENSE)

<br/>

[Overview](#-overview) •
[Architecture](#-architecture) •
[Quick Start](#-quick-start) •
[API](#-api-reference) •
[Security](#-security-model) •
[CI/CD](#-cicd-pipeline) •
[Hardening](#-production-hardening-checklist)

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Capabilities](#-key-capabilities)
- [At a Glance](#-at-a-glance)
- [Architecture](#-architecture)
- [Request & RAG Flow](#-request--rag-flow)
- [Document Ingestion Flow](#-document-ingestion-flow)
- [Data Model & Storage](#-data-model--storage)
- [Security Model](#-security-model)
- [Guardrails](#-guardrails)
- [Human-in-the-Loop Approvals](#-human-in-the-loop-approvals)
- [Technology Stack](#-technology-stack)
- [Repository Structure](#-repository-structure)
- [Quick Start](#-quick-start)
- [Docker Usage](#-docker-usage)
- [API Reference](#-api-reference)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Observability](#-observability)
- [Testing](#-testing)
- [Configuration Reference](#-configuration-reference)
- [Known Limitations](#-known-limitations)
- [Production Hardening Checklist](#-production-hardening-checklist)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 🌟 Overview

This repository is a compact, **production-oriented reference implementation** of an enterprise AI knowledge assistant. It shows how the major building blocks of a real RAG platform fit together, while staying small enough to run and inspect locally.

It combines:

- 📄 **Secure document ingestion** through presigned S3 uploads
- 🔎 **Tenant-aware vector retrieval** with ACL metadata filters
- 💬 **Grounded answers** with source citations (`[1]`, `[2]`)
- 🛡️ **Deterministic guardrails** on both input and output
- ✋ **Human-in-the-loop** approval records for high-impact requests
- 🧾 **Audit events**, feedback, and short-term conversation memory
- 📈 **Optional, content-safe observability** via Rius
- 🚢 **Containerized delivery** with a GitHub Actions → ECR → EC2 pipeline

> [!NOTE]
> This is a **reference implementation**, not a turnkey production platform. See [Known Limitations](#-known-limitations) and the [Production Hardening Checklist](#-production-hardening-checklist) before using it in a real environment.

---

## ✨ Key Capabilities

| | Capability | Description |
|---|---|---|
| 💬 | **RAG chat** | Retrieves authorized passages and generates answers grounded only in that context |
| 📥 | **Document ingestion** | PDF, DOCX, TXT, and Markdown uploads via presigned S3 URLs |
| 🧮 | **Vector search** | Amazon Bedrock Titan embeddings stored and queried in Pinecone |
| 🏢 | **Tenant-aware retrieval** | Pinecone namespaces + metadata filters for tenant, owner, and group access |
| 🧠 | **Conversation memory** | Short-term history persisted in PostgreSQL |
| 🛡️ | **Guardrails** | Blocks prompt-injection / secret-exfiltration patterns; detects sensitive output |
| ✋ | **Human-in-the-loop** | Routes high-impact requests to an approval record instead of executing them |
| 🧾 | **Auditability** | Records document events, guardrail events, approval decisions, and feedback |
| 📈 | **Observability** | Optional Rius tracing, with content capture **off** by default |
| 🐳 | **Containerization** | Non-root Python container image |
| 🚀 | **CI/CD** | Compile check → build & push to ECR → deploy to a self-hosted EC2 runner |

---

## 🔭 At a Glance

```mermaid
mindmap
  root((Enterprise RAG))
    Ingest
      Presigned S3 upload
      PDF / DOCX / TXT / MD
      Overlapping chunks
      Titan embeddings
    Retrieve
      Pinecone namespaces
      ACL metadata filters
      Relevance threshold
    Generate
      Nova Lite on Bedrock
      Grounded answers
      Source citations
    Protect
      Input guardrails
      Output guardrails
      HITL approvals
      Audit events
    Ship
      Docker non-root
      GitHub Actions
      Amazon ECR
      EC2 self-hosted runner
    Observe
      Rius tracing
      Content-safe by default
```

---

## 🏗️ Architecture

### System architecture

```mermaid
flowchart LR
    subgraph Client["🖥️ Client"]
        U[User / Browser]
    end

    subgraph App["⚙️ FastAPI Application"]
        API[API Routes]
        G[🛡️ Input Guardrails]
        HITL{✋ Needs approval?}
        R[LangGraph RAG Workflow]
        OG[🛡️ Output Guardrail]
        W[Ingestion Worker]
    end

    subgraph AWS["☁️ AWS"]
        S3[(Amazon S3)]
        BE[Bedrock Titan Embeddings]
        BC[Bedrock Nova Lite Chat]
    end

    subgraph Data["🗄️ Data Stores"]
        PC[(Pinecone<br/>tenant namespaces)]
        PG[(PostgreSQL<br/>docs · memory · audit · approvals)]
    end

    OBS[📈 Rius Tracing<br/>optional]

    U -->|chat| API --> G --> HITL
    HITL -- yes --> PG
    HITL -- no --> R
    R --> BE --> PC
    PC -->|ACL-filtered context| R
    R --> BC --> OG --> U

    U -->|presigned PUT| S3
    API -->|complete| W
    W --> S3
    W --> BE
    W --> PC
    W --> PG
    API --> PG
    API -.-> OBS
```

### Deployment architecture

```mermaid
flowchart TB
    DEV[👩‍💻 Developer] -->|git push main| GH[GitHub Repository]
    GH --> GA[GitHub Actions]

    subgraph CI["CI / CD"]
        GA --> CHK[✅ Compile check]
        CHK --> BLD[🐳 Docker build]
        BLD --> ECR[(Amazon ECR<br/>image tag = commit SHA)]
    end

    ECR -->|pull| RUN

    subgraph EC2["🖥️ EC2 — self-hosted runner"]
        RUN[Deploy job] --> CTR[atlas-enterprise-ai container<br/>:8000]
    end

    CTR --> BEDROCK[Amazon Bedrock]
    CTR --> S3[(Amazon S3)]
    CTR --> PINE[(Pinecone)]
    CTR --> PGDB[(PostgreSQL)]
```

---

## 🔄 Request & RAG Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant API as FastAPI
    participant GR as Guardrails
    participant DB as PostgreSQL
    participant BE as Bedrock Titan
    participant PC as Pinecone
    participant LLM as Bedrock Nova Lite

    User->>API: POST /api/chat
    API->>API: Resolve principal & tenant
    API->>GR: Input guardrails
    alt Blocked pattern
        GR-->>User: Refusal + guardrail event
    end
    API->>API: HITL check (delete / export / send to / update policy)
    alt Approval required
        API->>DB: Create approval record
        API-->>User: status = pending_approval
    end
    API->>DB: Load recent history
    API->>API: Merge follow-up with prior user question
    API->>BE: Embed query
    BE-->>API: Vector
    API->>PC: Query tenant namespace + ACL filter
    PC-->>API: Candidate passages
    API->>API: Drop results below MIN_RELEVANCE
    alt No authorized evidence
        API-->>User: No-evidence response
    else Evidence found
        API->>LLM: Answer ONLY from retrieved passages
        LLM-->>API: Draft answer with [1] [2] citations
        API->>GR: Output sensitive-data check
        API->>DB: Save conversation turn
        API-->>User: Answer + source references
    end
```

<details>
<summary><b>📋 Step-by-step breakdown</b></summary>

1. Resolve the current demo principal and tenant context.
2. Run deterministic input guardrails.
3. Check whether the request requires human approval.
4. Load recent conversation history from PostgreSQL.
5. Combine the latest question with a recent user question for short follow-ups.
6. Generate an embedding with Amazon Bedrock.
7. Search the tenant's Pinecone namespace using ACL metadata filters.
8. Discard results below the configured relevance threshold.
9. Return a no-evidence response when no authorized context is found.
10. Otherwise, ask the Bedrock chat model to answer only from the retrieved passages.
11. Run the output sensitive-data guardrail.
12. Save the conversation turn and return the answer with source references.

</details>

### LangGraph workflow

```mermaid
stateDiagram-v2
    [*] --> InputGuard
    InputGuard --> Blocked: pattern matched
    InputGuard --> ApprovalCheck: clean
    ApprovalCheck --> PendingApproval: HITL_ENABLED and high-impact term
    ApprovalCheck --> Retrieve: normal request
    Retrieve --> NoEvidence: nothing above MIN_RELEVANCE
    Retrieve --> Generate: authorized context found
    Generate --> OutputGuard
    OutputGuard --> Respond: safe
    OutputGuard --> Blocked: sensitive data detected
    Respond --> [*]
    NoEvidence --> [*]
    Blocked --> [*]
    PendingApproval --> [*]
```

> [!TIP]
> The node names above describe the logical stages of the workflow. See `app/graph.py` for the exact implementation.

---

## 📥 Document Ingestion Flow

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant API as FastAPI
    participant DB as PostgreSQL
    participant S3 as Amazon S3
    participant W as Ingestion Worker
    participant BE as Bedrock Titan
    participant PC as Pinecone

    Client->>API: POST /api/documents/uploads (filename)
    API->>DB: Insert document (status = pending)
    API-->>Client: Presigned S3 PUT URL
    Client->>S3: Upload file directly
    Client->>API: POST /api/documents/complete
    API->>W: Start ingestion
    W->>S3: Download object
    W->>W: Validate size · parse · chunk (overlapping)
    loop each chunk
        W->>BE: Embed chunk
        BE-->>W: Vector
    end
    W->>PC: Upsert vectors + ACL metadata (tenant namespace)
    W->>DB: status = ready + audit event
    API-->>Client: Ingestion result
```

### Document lifecycle

```mermaid
stateDiagram-v2
    [*] --> pending: upload URL issued
    pending --> ready: parsed, embedded, upserted
    pending --> failed: too large / parse error / needs OCR
    ready --> [*]
    failed --> [*]
```

| Rule | Behavior |
|---|---|
| ✅ Supported types | `.pdf` `.docx` `.txt` `.md` |
| 📏 Size limit | Files above `MAX_UPLOAD_BYTES` are rejected |
| 🔍 Scanned PDFs | Reported as **requiring OCR** (OCR is not implemented) |
| ✂️ Chunking | Overlapping chunks to preserve context across boundaries |
| 🏷️ Metadata | Tenant, owner, and group ACL attached to every vector |

---

## 🗄️ Data Model & Storage

Each store has a single, clear responsibility.

```mermaid
flowchart LR
    subgraph PG["🐘 PostgreSQL"]
        T1[documents]
        T2[chat messages]
        T3[audit events]
        T4[approvals]
        T5[feedback]
    end

    subgraph PN["🌲 Pinecone"]
        NS1["namespace: tenant-A"]
        NS2["namespace: tenant-B"]
    end

    subgraph S3["🪣 Amazon S3"]
        OBJ[Raw uploaded files]
    end
```

| Store | Holds | Isolation |
|---|---|---|
| 🐘 **PostgreSQL** | Document metadata, memory, audit events, approvals, feedback | Queries constrained by **tenant ID** |
| 🌲 **Pinecone** | Chunk vectors + ACL metadata | Namespace `tenant-<tenant_id>` + metadata filters |
| 🪣 **Amazon S3** | Original uploaded files | Presigned URLs; direct browser upload |

`infra/schema.sql` creates five tables for documents, feedback, audit events, approvals, and chat messages. `scripts/init_db.py` is safe to re-run (`CREATE TABLE IF NOT EXISTS`) and verifies that all five tables exist.

---

## 🔐 Security Model

### Defense in depth

```mermaid
flowchart TB
    A[🌐 Request] --> B[1️⃣ Identity — Principal<br/>tenant · groups · admin]
    B --> C[2️⃣ Input guardrails<br/>injection & secret-exfiltration patterns]
    C --> D[3️⃣ HITL gate<br/>high-impact actions → approval]
    D --> E[4️⃣ Tenant namespace<br/>tenant-&lt;tenant_id&gt;]
    E --> F[5️⃣ ACL metadata filter<br/>owner or allowed group]
    F --> G[6️⃣ Grounded generation<br/>answer only from context]
    G --> H[7️⃣ Output guardrail<br/>credential-like patterns]
    H --> I[✅ Response + citations]
```

### Retrieval isolation

- 🏷️ Pinecone namespaces in the form `tenant-<tenant_id>`
- 🔑 Metadata filters allow a document when the user belongs to an allowed group **or** owns the document
- 🗃️ PostgreSQL queries constrained by tenant ID
- 👮 Admin routes checked against the principal's admin flag

### Demo principal

```yaml
subject: demo-operator
tenant:  demo-workspace
groups:  workspace
admin:   true
```

> [!WARNING]
> The demo `Principal` is **not** authentication or authorization. Before production, replace it with a validated identity from your OIDC provider, JWT, API gateway, or enterprise identity platform. **Never trust tenant, group, or admin values supplied by the browser.**

---

## 🛡️ Guardrails

| Direction | Category | Examples blocked / detected |
|---|---|---|
| ⬇️ **Input** | Instruction override | Requests to ignore system instructions |
| ⬇️ **Input** | Prompt disclosure | Requests to reveal system or developer prompts |
| ⬇️ **Input** | Secret exfiltration | Requests for API keys, passwords, credentials, secrets, access tokens |
| ⬇️ **Input** | Control bypass | Requests to disable security controls |
| ⬇️ **Input** | Impersonation | Attempts to pose as a system, developer, or administrator |
| ⬆️ **Output** | Credential leakage | Private keys, AWS access keys, database URLs, API-key assignments, other credential-like values |

> [!IMPORTANT]
> Guardrails are a **defense-in-depth demo** of deterministic pattern checks. They can miss or over-block cases and are not a replacement for IAM, authentication, authorization, network controls, secret management, or provider-level safety controls.

---

## ✋ Human-in-the-Loop Approvals

When `HITL_ENABLED=true`, questions containing high-impact terms — `delete`, `export`, `send to`, `update policy` — create an approval record instead of being answered.

```mermaid
stateDiagram-v2
    [*] --> Requested: chat contains high-impact term
    Requested --> Pending: approval record created
    Pending --> Approved: admin approves
    Pending --> Rejected: admin rejects
    Approved --> [*]: decision recorded only
    Rejected --> [*]
```

**Chat response while waiting:**

```json
{
  "status": "pending_approval",
  "approval_id": "..."
}
```

> [!NOTE]
> Approval decisions are **recorded only**. The current implementation does not automatically execute the underlying action after approval.

---

## 🧰 Technology Stack

| Layer | Technology | Role |
|---|---|---|
| 🐍 Runtime | **Python 3.11 / 3.12** | Application and worker runtime |
| ⚡ API | **FastAPI** + **Uvicorn** | HTTP API, web UI, ASGI server |
| 🕸️ Orchestration | **LangGraph** | RAG workflow graph |
| 🤖 LLM & Embeddings | **Amazon Bedrock** | Titan Text Embeddings V2 · Nova Lite chat |
| 🪣 Object storage | **Amazon S3** | Document storage & presigned uploads |
| 📦 Registry | **Amazon ECR** | Docker image registry |
| 🌲 Vector DB | **Pinecone** (serverless) | Similarity search |
| 🐘 Relational DB | **PostgreSQL** | Metadata, audit, approvals, feedback, memory |
| 🐳 Packaging | **Docker** | Reproducible, non-root images |
| 🚀 Delivery | **GitHub Actions** | CI/CD |
| 📈 Observability | **Rius** (optional) | Content-safe tracing |

---

## 🗂️ Repository Structure

```
Enterprise-RAG-with-CI-CD-AWS-Actions/
├── 📄 .env.example                 # Environment variable template
├── 🚀 .github/workflows/cicd.yaml  # CI/CD pipeline
├── 🐳 Dockerfile                   # Production-style API image
├── 📜 LICENSE                      # MIT License
├── 📘 README.md                    # Project documentation
├── 📦 requirements.txt             # Python dependencies
├── app/
│   ├── aws.py                      # Bedrock and S3 clients
│   ├── config.py                   # Pydantic settings
│   ├── db.py                       # PostgreSQL connections and audit helper
│   ├── demo_context.py             # Demo principal and tenant context
│   ├── graph.py                    # LangGraph RAG workflow
│   ├── guardrails.py               # Input/output safety checks
│   ├── main.py                     # FastAPI application and routes
│   ├── memory.py                   # Conversation history persistence
│   ├── observability.py            # Optional Rius instrumentation
│   ├── rag.py                      # RAG entry point
│   ├── vector.py                   # Pinecone index and ACL-aware search
│   ├── static/                     # Frontend CSS and JavaScript
│   └── templates/index.html        # Web UI
├── docs/SETUP.md                   # Additional setup placeholder
├── infra/schema.sql                # PostgreSQL schema
├── scripts/init_db.py              # Database initialization utility
├── test/                           # Bedrock integration test script
└── worker/ingest.py                # S3 document ingestion pipeline
```

---

## ⚡ Quick Start

### ✅ Prerequisites

| Requirement | Notes |
|---|---|
| 🐍 Python 3.11+ | 3.11 recommended for local development |
| 🐳 Docker | For container builds |
| ☁️ AWS account | Access to Bedrock, S3, and ECR |
| 🤖 Bedrock model access | Embedding and chat models enabled in your region |
| 🌲 Pinecone account | API key required |
| 🐘 PostgreSQL | Any reachable instance |
| 🚀 GitHub secrets + EC2 runner | Only needed for the deployment workflow |

### 1️⃣ Clone

```bash
git clone https://github.com/paras160500/Enterprise-RAG-with-CI-CD-AWS-Actions.git
cd Enterprise-RAG-with-CI-CD-AWS-Actions
```

### 2️⃣ Create a virtual environment

<details open>
<summary><b>🍎 macOS / 🐧 Linux</b></summary>

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

</details>

<details>
<summary><b>🪟 Windows PowerShell</b></summary>

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

</details>

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure environment

```bash
cp .env.example .env
```

Replace every placeholder with your own values:

```ini
# --- AWS ---
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY_ID=your_secret_key
AWS_REGION=us-east-1

# --- Bedrock ---
BEDROCK_EMBED_MODEL=amazon.titan-embed-text-v2:0
BEDROCK_CHAT_MODEL=amazon.nova-lite-v1:0
EMBED_DIM=1024

# --- S3 ---
S3_BUCKET=your-s3-bucket

# --- Pinecone ---
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=your-pinecone-index
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_READY_TIMEOUT=180

# --- PostgreSQL ---
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# --- Observability (optional) ---
RIUS_API_KEY=
RIUS_SERVICE_NAME=enterprise-rag
RIUS_DISABLED=true
RIUS_CAPTURE_CONTENT=false

# --- Behavior ---
HITL_ENABLED=true
MEMORY_TURNS=6
```

> [!CAUTION]
> Never commit `.env`. Prefer IAM roles, workload identity, or a secret manager over long-lived AWS access keys whenever possible.

### 5️⃣ Initialize PostgreSQL

```bash
python scripts/init_db.py
```

Idempotent — safe to re-run. It verifies all five expected tables exist.

### 6️⃣ Run the app

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| 🔗 Resource | URL |
|---|---|
| 🖥️ Web app | http://localhost:8000 |
| 📚 API docs | http://localhost:8000/api/docs |
| 💚 Liveness | `GET /health/live` |
| 🩺 Readiness | `GET /health/ready` |

---

## 🐳 Docker Usage

**Build**

```bash
docker build -t enterprise-rag:local .
```

**Run**

```bash
docker run --rm \
  --name enterprise-rag \
  --env-file .env \
  -p 8000:8000 \
  enterprise-rag:local
```

| Property | Value |
|---|---|
| Base | Python 3.12 |
| User | non-root `atlas` |
| Port | `8000` |
| Copies | `app` and `worker` packages |
| Entrypoint | `uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers` |

---

## 📡 API Reference

> Interactive docs: `http://localhost:8000/api/docs`

### 🩺 Application & health

| Method | Endpoint | Purpose |
|:---:|---|---|
| `GET` | `/` | Serves the web interface |
| `GET` | `/health/live` | Liveness check |
| `GET` | `/health/ready` | Checks PostgreSQL availability |

### 📄 Documents

| Method | Endpoint | Purpose |
|:---:|---|---|
| `POST` | `/api/documents/uploads` | Creates document metadata and returns a presigned S3 upload URL |
| `POST` | `/api/documents/complete` | Starts ingestion for a completed S3 upload |
| `GET` | `/api/documents` | Lists documents available to the current tenant and groups |

### 💬 Chat & memory

| Method | Endpoint | Purpose |
|:---:|---|---|
| `POST` | `/api/chat` | Runs the guarded RAG workflow |
| `GET` | `/api/conversations/{conversation_id}/messages` | Returns conversation messages for the current tenant |
| `POST` | `/api/feedback` | Saves a rating and optional note |

### 🛠️ Administration & approvals 🔒 *admin only*

| Method | Endpoint | Purpose |
|:---:|---|---|
| `GET` | `/api/admin/metrics` | Document-status and feedback counts for the tenant |
| `GET` | `/api/admin/guardrails` | Guardrail event counts |
| `GET` | `/api/approvals` | Pending and historical approvals |
| `POST` | `/api/approvals/{approval_id}/decision` | Approves or rejects an approval record |

---

## 🚀 CI/CD Pipeline

Workflow file: `.github/workflows/cicd.yaml`

**Triggers:** push to `main` (except changes that only modify `README.md`) and manual `workflow_dispatch`.

```mermaid
flowchart LR
    T([⚡ Push to main<br/>or manual dispatch]) --> CI

    subgraph CI["1️⃣ Continuous Integration"]
        A1[Checkout] --> A2[Python 3.11]
        A2 --> A3["compileall<br/>app worker scripts"]
    end

    CI --> CD

    subgraph CD["2️⃣ Continuous Delivery"]
        B1[Configure AWS creds] --> B2[Login to ECR]
        B2 --> B3[Docker build]
        B3 --> B4[Tag with commit SHA]
        B4 --> B5[Push to ECR]
    end

    CD --> DEP

    subgraph DEP["3️⃣ Continuous Deployment — self-hosted EC2 runner"]
        C1[Auth AWS + ECR] --> C2[Build image URI]
        C2 --> C3[Pull image]
        C3 --> C4[Validate secrets]
        C4 --> C5[Remove old container]
        C5 --> C6[Start new container :8000]
        C6 --> C7{Health check<br/>127.0.0.1:8000}
        C7 -- ✅ ok --> C8[Prune unused images]
        C7 -- ❌ fail --> X([Deployment fails])
    end
```

| Stage | Job | Key steps |
|---|---|---|
| **CI** | Compile-check | Checkout → Python 3.11 → `python -m compileall -q app worker scripts` |
| **CD (delivery)** | Build & push | AWS creds → ECR login → build → tag with commit SHA → push |
| **CD (deployment)** | Deploy on EC2 | Pull image → validate secrets → replace `atlas-enterprise-ai` container → health check → prune images |

**Runner labels:** `self-hosted, linux, x64, atlas-ec2`

### 🔑 GitHub Actions secrets

Configure these as **production environment** secrets:

<details>
<summary><b>Show all required secret names</b></summary>

| Group | Secrets |
|---|---|
| ☁️ AWS | `AWS_ACCESS_KEY_ID` · `AWS_SECRET_ACCESS_KEY` · `AWS_REGION` · `ECR_REPOSITORY_NAME` · `S3_BUCKET` |
| 🤖 Bedrock | `BEDROCK_EMBED_MODEL` · `BEDROCK_CHAT_MODEL` · `EMBED_DIM` |
| 🌲 Pinecone | `PINECONE_API_KEY` · `PINECONE_INDEX_NAME` · `PINECONE_CLOUD` · `PINECONE_REGION` · `PINECONE_READY_TIMEOUT` |
| 🐘 Database | `DATABASE_URL` |
| 📈 Observability | `RIUS_API_KEY` · `RIUS_SERVICE_NAME` · `RIUS_DISABLED` · `RIUS_CAPTURE_CONTENT` |
| ⚙️ App | `HITL_ENABLED` · `MEMORY_TURNS` |

</details>

> [!TIP]
> Use **GitHub Environments** with protected deployment rules for production. Prefer short-lived credentials and an IAM role for the EC2 runner instead of long-lived access keys.

---

## 📈 Observability

If `RIUS_API_KEY` is set and `RIUS_DISABLED` is not enabled, Rius tracing is initialized.

| Instrumented area | Examples |
|---|---|
| 🧮 Embeddings | Titan embedding calls |
| 🤖 Generation | Bedrock answer generation |
| 🌲 Vector store | Pinecone search & upsert |
| 📥 Ingestion | Document ingestion pipeline |
| 🛡️ Safety | Guardrail checks |
| 🕸️ Workflow | RAG graph nodes |
| 💬 API | Chat requests |

> [!IMPORTANT]
> Input/output **content capture is disabled by default**. Keep it off unless you have an explicit privacy, retention, and access-control policy.

---

## 🧪 Testing

A Bedrock integration smoke test is included:

```bash
python test/test.py
```

| Check | Verifies |
|---|---|
| 🧮 Embeddings | Titan embedding generation and vector dimension |
| 💬 Chat | Nova Lite chat completion |

Requires valid AWS credentials, Bedrock model access, and the matching environment variables.

> [!NOTE]
> CI currently performs **syntax compilation only**. For production, add isolated tests for configuration, authorization filters, ingestion parsing, guardrails, API routes, and RAG behavior.

---

## ⚙️ Configuration Reference

| Variable | Purpose |
|---|---|
| `AWS_REGION` | AWS region for Bedrock and S3 |
| `AWS_ACCESS_KEY_ID` | Optional explicit AWS access key (local development) |
| `AWS_SECRET_ACCESS_KEY_ID` | Optional explicit AWS secret key (local development) |
| `S3_BUCKET` | S3 bucket for uploaded documents |
| `BEDROCK_EMBED_MODEL` | Bedrock embedding model ID |
| `BEDROCK_CHAT_MODEL` | Bedrock chat model ID |
| `EMBED_DIM` | Vector dimension expected by Pinecone |
| `PINECONE_API_KEY` | Pinecone API key |
| `PINECONE_INDEX_NAME` | Pinecone index name |
| `PINECONE_CLOUD` | Pinecone serverless cloud |
| `PINECONE_REGION` | Pinecone serverless region |
| `PINECONE_READY_TIMEOUT` | Max seconds to wait for the index to be ready |
| `DATABASE_URL` | PostgreSQL connection string |
| `MIN_RELEVANCE` | Minimum similarity score for retrieved passages |
| `MAX_UPLOAD_BYTES` | Maximum accepted document size |
| `HITL_ENABLED` | Enables approval records for selected requests |
| `MEMORY_TURNS` | Number of recent conversation turns to retain |
| `RIUS_API_KEY` | Optional Rius observability key |
| `RIUS_SERVICE_NAME` | Rius service name |
| `RIUS_DISABLED` | Disables observability when true |
| `RIUS_CAPTURE_CONTENT` | Content-capture setting; keep disabled for privacy |

---

## ⚠️ Known Limitations

| Area | Limitation |
|---|---|
| 🔑 Identity | Hard-coded demo principal instead of a real identity provider |
| 🔄 Ingestion | Synchronous after upload completion; no durable queue-based worker |
| 📷 OCR | Scanned PDFs are detected but OCR is not implemented |
| 🛡️ Guardrails | Pattern-based; can miss or over-block cases |
| 🧪 Testing | CI compiles Python but has no comprehensive automated test suite |
| ✋ Approvals | Decisions are recorded but approved actions are not executed |
| 🔐 Secrets | Must be supplied via a secure secret manager or CI environment |
| 🏗️ Infra | Pinecone, Bedrock, S3, and PostgreSQL must be provisioned separately |

---

## ✅ Production Hardening Checklist

<details open>
<summary><b>🔐 Identity & secrets</b></summary>

- [ ] Replace the demo principal with a verified identity and authorization system
- [ ] Use IAM roles or workload identity instead of long-lived AWS keys
- [ ] Store secrets in AWS Secrets Manager, SSM Parameter Store, or equivalent
- [ ] Rotate any credentials that may have been exposed in repo history or examples
- [ ] Add authentication and authorization tests for every tenant and group boundary

</details>

<details open>
<summary><b>📥 Ingestion & data</b></summary>

- [ ] Durable asynchronous ingestion with retries, idempotency, and dead-letter handling
- [ ] Validate file type, size, and content; add malware scanning before ingestion
- [ ] Add OCR for scanned documents where required
- [ ] Add document versioning and deletion propagation to Pinecone

</details>

<details open>
<summary><b>🛡️ Platform & safety</b></summary>

- [ ] Add rate limits, request limits, and abuse protection
- [ ] Configure TLS, private networking, logging, backups, and disaster recovery
- [ ] Pin dependency versions and scan images for vulnerabilities

</details>

<details open>
<summary><b>🧪 Quality & operations</b></summary>

- [ ] Add unit, integration, security, and deployment smoke tests
- [ ] Monitor retrieval quality, hallucination rate, guardrail events, latency, cost, and token usage

</details>

---

## 🗺️ Roadmap

```mermaid
flowchart LR
    subgraph P1["Phase 1 · Foundations ✅"]
        direction TB
        a1[RAG chat]
        a2[Presigned ingestion]
        a3[Guardrails + HITL]
        a4[CI/CD to EC2]
    end

    subgraph P2["Phase 2 · Trust & Quality"]
        direction TB
        b1[OIDC / JWT identity]
        b2[Automated test suite]
        b3[Eval harness for retrieval]
    end

    subgraph P3["Phase 3 · Scale"]
        direction TB
        c1[Queue-based ingestion + DLQ]
        c2[OCR + malware scanning]
        c3[Document versioning + deletion sync]
    end

    subgraph P4["Phase 4 · Enterprise"]
        direction TB
        d1[Secrets Manager + IAM roles]
        d2[Rate limiting + WAF]
        d3[Action execution after approval]
    end

    P1 --> P2 --> P3 --> P4
```

> The roadmap is a suggested direction derived from the [Known Limitations](#-known-limitations), not a committed schedule.

---

## 📜 License

Released under the [MIT License](./LICENSE).

<div align="center">

**Copyright © 2026 Paras Patel**

⭐ If this project helped you, consider giving it a star!

</div>
