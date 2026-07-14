# Nova — AI Voice Assistant · System Design & Roadmap

> A production-grade, modular AI operating assistant (voice + chat) in the spirit of
> Alexa / Siri / Google Assistant / ChatGPT Voice / Jarvis.
> This document covers: (1) architecture, (2) folder structure, (3) technology
> rationale, and (4) a phased delivery plan. Code is implemented **phase by phase**,
> not all at once.

---

## 0. Guiding principles

- **Clean/Hexagonal architecture** — domain logic is isolated from frameworks and IO.
  Ports (interfaces) in the core; adapters (FastAPI, Postgres, Qdrant, LLM SDKs) at the edges.
- **SOLID + Dependency Injection** — everything the core needs is injected via
  interfaces so providers (OpenAI ↔ Gemini ↔ local) are swappable and testable.
- **Async-first** — FastAPI + async DB drivers + streaming everywhere (SSE/WebSocket).
- **Provider-agnostic** — LLM, STT, TTS, and vector store are behind abstractions.
- **Safety by default** — any action that touches money, files (destructive),
  purchases, or bookings requires **explicit confirmation**. No silent side effects.
- **Observable** — structured logging, request tracing, cost/usage metering from day one.
- **Incremental** — a working vertical slice each phase; the app is always runnable.

---

## 1. High-level architecture

```
                         ┌──────────────────────────────────────────┐
                         │              Frontend (Next.js)            │
                         │  React · TS · Tailwind · Framer Motion     │
                         │  Orb · Waveform · Chat · Dashboard         │
                         └───────────────┬───────────────┬───────────┘
                                         │ REST/JSON      │ WebSocket (voice/stream)
                                         ▼                ▼
                         ┌──────────────────────────────────────────┐
                         │              API Gateway (FastAPI)         │
                         │  Auth · Rate limit · Routing · OpenAPI     │
                         └───┬───────────┬───────────┬───────────┬───┘
                             │           │           │           │
                     ┌───────▼───┐ ┌─────▼─────┐ ┌───▼──────┐ ┌──▼─────────┐
                     │  Auth svc │ │ Conversation│ │  Voice   │ │  Agent      │
                     │ JWT/OAuth │ │  + Memory   │ │ STT/TTS  │ │ Orchestrator│
                     └─────┬─────┘ └──────┬──────┘ └────┬─────┘ └──────┬──────┘
                           │              │             │              │
                           │              │             │      ┌───────▼────────┐
                           │              │             │      │ LangGraph multi │
                           │              │             │      │ -agent runtime  │
                           │              │             │      │ + Tools + MCP   │
                           │              │             │      └───────┬────────┘
                           ▼              ▼             ▼              ▼
        ┌───────────────────────────────────────────────────────────────────────┐
        │  Infrastructure adapters                                               │
        │  Postgres (users, convos)  ·  Redis (sessions, cache, queues)          │
        │  Qdrant (RAG vectors)      ·  Object store (uploads/audio)             │
        │  LLM providers (OpenAI/Gemini/Anthropic/local)  ·  STT/TTS providers   │
        └───────────────────────────────────────────────────────────────────────┘
```

### Request lifecycles

**Voice turn (streaming):**
`mic → WS audio frames → STT (streaming) → transcript → Agent Orchestrator
(LangGraph) → tool calls / LLM tokens streamed back → TTS chunks → speaker`,
with wake-word ("Hey Nova") detected client-side to gate the mic.

**RAG query:** `upload → parse → chunk → embed → Qdrant` then at query time
`hybrid retrieve (dense+sparse) → rerank → metadata filter → LLM answer + citations`.

**Agent action:** planner decides a plan → specialized agents (browser/file/coding/
scheduling/vision) execute via typed tools → confirmation gate for risky actions.

---

## 2. Multi-agent design (LangGraph)

A **supervisor/planner** graph routes user intent to specialist agents, each exposing
a well-typed toolset. All tools are pure functions behind interfaces (unit-testable).

| Agent            | Responsibility                                   | Example tools |
|------------------|--------------------------------------------------|---------------|
| Planning         | Decompose goals, route to specialists            | `make_plan`, `handoff` |
| Research         | Web / Wikipedia / papers / GitHub search         | `web_search`, `wiki`, `arxiv` |
| Browser          | Navigate, fill forms, read/summarize pages       | `open`, `click`, `type`, `read` (Playwright) |
| File             | Search/rename/move/copy/zip (confirm destructive)| `find`, `move`, `zip`, `delete*` |
| Coding           | Run scripts, git, build (sandboxed)              | `run`, `git`, `build` |
| Memory           | Long-term memory read/write                      | `remember`, `recall` |
| Scheduling       | Reminders, alarms, calendar, meetings            | `add_reminder`, `schedule` |
| Vision           | Analyze images/screenshots, OCR, charts          | `describe`, `ocr`, `detect_ui` |
| Shopping/Booking | Search, compare, cart, **confirm before buy**    | `search_products`, `compare`, `add_to_cart` |

`*` destructive/financial tools always return a **confirmation request**, never execute directly.

---

## 3. Folder structure (monorepo)

```
nova/
├── README.md
├── DESIGN.md                     # this document
├── docker-compose.yml            # postgres, redis, qdrant, api, web
├── .github/workflows/ci.yml      # lint, typecheck, test, build
├── .env.example
│
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py               # FastAPI app factory + router mount
│   │   ├── core/                 # config, logging, security, DI container
│   │   │   ├── config.py         # pydantic-settings
│   │   │   ├── logging.py        # structlog
│   │   │   ├── security.py       # JWT, password hashing
│   │   │   └── container.py      # dependency injection wiring
│   │   ├── domain/               # entities + port interfaces (framework-free)
│   │   │   ├── models/           # User, Conversation, Message, Document...
│   │   │   └── ports/            # LLMProvider, STT, TTS, VectorStore, Repo...
│   │   ├── services/             # use-cases (auth, conversation, voice, rag, agents)
│   │   ├── adapters/             # implementations of ports
│   │   │   ├── llm/  stt/  tts/  vectorstore/  db/  cache/  oauth/
│   │   ├── agents/               # LangGraph graphs + tools + MCP clients
│   │   ├── api/                  # routers (auth, chat, voice, rag, agents, users)
│   │   │   └── ws/               # websocket handlers (voice, streaming)
│   │   └── db/                   # SQLAlchemy models, Alembic migrations
│   └── tests/                    # unit + integration (pytest)
│
├── frontend/
│   ├── package.json
│   ├── app/                      # Next.js App Router
│   │   ├── (auth)/  (dashboard)/  settings/
│   ├── components/               # Orb, Waveform, Mic, Chat, Sidebar, ThemeToggle
│   ├── lib/                      # api client, ws client, auth, hooks
│   ├── stores/                   # zustand state
│   └── styles/                   # tailwind + glassmorphism tokens
│
└── infra/
    ├── docker/                   # per-service Dockerfiles
    └── scripts/                  # bootstrap, seed, dev helpers
```

---

## 4. Technology choices & rationale

| Layer | Choice | Why |
|-------|--------|-----|
| Frontend | **Next.js + React + TS** | SSR/streaming, mature ecosystem, type safety |
| Styling | **Tailwind + Framer Motion** | Rapid premium UI, glassmorphism, fluid animation |
| State | **Zustand + TanStack Query** | Simple client state + server cache/streaming |
| API | **FastAPI (async)** | First-class async, Pydantic validation, auto OpenAPI |
| Auth | **JWT + OAuth (Google/GitHub) + Authlib** | Standard, stateless access + refresh, social login |
| DB | **PostgreSQL + SQLAlchemy 2 + Alembic** | Relational integrity, async, versioned migrations |
| Cache/queue | **Redis** | Sessions, rate limiting, pub/sub for streaming, task queue |
| Vectors | **Qdrant** | Fast ANN, hybrid search, metadata filters, payload store |
| Agents | **LangGraph** | Stateful, controllable multi-agent graphs, tool calling |
| Interop | **MCP** | Standard tool/server protocol; pluggable capabilities |
| Voice | **Provider-abstracted STT/TTS** | Swap OpenAI/Deepgram/ElevenLabs/local (Whisper/Piper) |
| Wake word | **openWakeWord / Porcupine (client)** | On-device "Hey Nova", privacy + latency |
| Infra | **Docker + Compose + GitHub Actions** | Reproducible dev/prod, CI gates |
| Obs | **structlog + OpenTelemetry (opt)** | Structured logs, tracing, cost metering |

---

## 5. Phased delivery plan

Each phase ends with a runnable app, tests, and docs. ✅ = target of that phase.

**Phase 0 — Foundation (scaffold + DX)**
Monorepo, Docker Compose (pg/redis/qdrant), config/logging, CI, README, `.env.example`,
health endpoints, DI container, base test harness.

**Phase 1 — Core assistant (the working vertical slice)** ⭐ *proposed first build*
Email/password + Google/GitHub OAuth + JWT; user profiles/settings; conversation
persistence + history; **streaming LLM chat** with tool-calling; **voice loop**
(wake word → STT → LLM → TTS) over WebSocket; long-term **memory**; premium UI
(Orb, waveform, animated mic, chat, sidebar, dashboard, settings, dark/light,
responsive, shortcuts, a11y). Provider abstraction with 1 default provider wired.

**Phase 2 — Knowledge & RAG**
Uploads (PDF/DOCX/XLSX/PPTX/CSV/TXT/images), parsing, chunking, embeddings,
Qdrant hybrid search + rerank + metadata filter, citations, document memory.

**Phase 3 — Multi-agent + tools**
LangGraph supervisor; Research/Memory/Scheduling agents; web/Wikipedia search;
reminders/alarms/calendar; productivity (weather, news, units, currency, timer).
MCP client support + model switching + cost dashboard.

**Phase 4 — Automation agents (careful scope)**
Browser agent (Playwright): navigate/read/summarize/fill forms; **Shopping/Booking**
search+compare+cart with **mandatory confirmation** before any purchase/booking.
File agent + Coding agent + Vision agent run in a **sandbox**, confirmation-gated.

**Phase 5 — Bonus / polish**
Plugin system, multi-language, emotion detection, analytics dashboard, model
marketplace, offline mode (local Whisper/Piper/Ollama), mobile/desktop companions.

---

## 6. Cross-cutting concerns

- **Security:** hashed passwords (argon2), short-lived JWT + rotating refresh,
  CSRF for cookie flows, per-user rate limits, secret management via env, no secrets in logs.
- **Confirmation gating:** a shared `RiskyAction` pattern — tools return a proposed
  action + preview; execution only proceeds after explicit user (voice/UI) confirm.
- **Testing:** pytest (unit + integration) backend; Vitest/Playwright frontend;
  contract tests for provider adapters; CI runs lint + typecheck + tests + build.
- **Docs:** README + install guide + OpenAPI (auto) + architecture (this doc).

---

## 7. Feasibility notes (honest)

- **On-machine control** (open/close desktop apps, mouse/keyboard, Spotify, screenshots)
  is inherently **host/OS-specific** and needs a local companion agent with granted
  permissions. In a server/cloud deployment these run against the *server's* environment,
  not the user's laptop, unless a local agent is installed. We'll implement these as a
  well-defined **local-agent interface** and ship a reference implementation for Linux.
- **Shopping/booking automation** via scraping is brittle and ToS-sensitive. We prefer
  official APIs, fall back to Playwright, and **never** complete a purchase/payment
  without explicit confirmation.
- **Voice cloning / emotion detection / full offline** are bonus and provider-dependent;
  scaffolded behind interfaces, enabled where keys/models are available.
```
