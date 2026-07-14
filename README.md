# ✦ Nova — AI Voice Assistant

A production-grade, modular AI **voice assistant** (voice + chat) built with a clean,
provider-agnostic architecture. Phase 1 ships a fully-runnable core: authentication,
streaming voice chat with a wake word, long-term memory, and a premium Next.js UI.
Later phases add RAG, multi-agent tools, browser/shopping automation, and vision.

> See [`DESIGN.md`](./DESIGN.md) for the full architecture, multi-agent design, and
> the phased roadmap.

---

## ✨ Features (Phase 1)

- **Auth** — email/password + **Google/GitHub OAuth**, JWT access/refresh tokens.
- **Streaming chat** — token-by-token responses over Server-Sent Events.
- **Voice loop** — “**Hey Nova**” wake word, speech-to-text, spoken replies, live
  waveform + animated AI orb.
- **Conversations** — persistent history, auto-titling, per-user isolation.
- **Long-term memory** — facts Nova remembers and injects into the prompt.
- **Provider-agnostic** — LLM/STT/TTS behind interfaces; runs with **zero API keys**
  using built-in mock providers, or wire up OpenAI/Gemini/etc.
- **Premium UI** — glassmorphism, Framer Motion animations, dark/light mode,
  responsive, keyboard shortcuts, accessibility.

## 🧱 Tech stack

| Area      | Stack |
|-----------|-------|
| Frontend  | Next.js 14 · React 18 · TypeScript · Tailwind · Framer Motion · Zustand |
| Backend   | FastAPI · Python 3.11 · SQLAlchemy 2 (async) · Pydantic v2 |
| Data      | PostgreSQL · Redis · Qdrant (RAG, Phase 2) |
| AI        | Provider-abstracted LLM/STT/TTS · LangGraph + MCP (Phase 3+) |
| Infra     | Docker · Docker Compose · GitHub Actions CI |

---

## 🚀 Quick start

### Option A — Docker Compose (everything)

```bash
cp .env.example .env         # tweak if you like; defaults work out of the box
docker compose up --build
```

- Web UI: http://localhost:3000
- API docs: http://localhost:8000/docs

### Option B — Local dev (no Docker required)

The backend defaults to a local **SQLite** database and **mock** AI providers, so it
runs with no external services.

**Backend**

```bash
cd backend
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
# Use SQLite for zero-setup local dev:
export NOVA_DATABASE_URL="sqlite+aiosqlite:///./nova.db"
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000, create an account, and start talking.

> **Voice note:** the wake word and voice input use the browser's Web Speech API
> (best in Chrome). The mic requires a secure context (`localhost` is fine). Spoken
> replies use the browser's speech synthesis. The backend also exposes an
> audio-based `/ws/voice` websocket and provider-abstracted STT/TTS for server-side
> voice.

---

## ⚙️ Configuration

All backend settings come from environment variables (prefix `NOVA_`) — see
[`.env.example`](./.env.example). Highlights:

| Variable | Default | Purpose |
|----------|---------|---------|
| `NOVA_DATABASE_URL` | _(Postgres from parts)_ | Set to `sqlite+aiosqlite:///./nova.db` for local dev |
| `NOVA_LLM_PROVIDER` | `mock` | `mock` \| `openai` (set `OPENAI_API_KEY`) |
| `NOVA_JWT_SECRET` | `dev-insecure-change-me` | **Change in production** (`openssl rand -hex 32`) |
| `GOOGLE_CLIENT_ID/SECRET` | — | Enables Google login when set |
| `GITHUB_CLIENT_ID/SECRET` | — | Enables GitHub login when set |

Providers with no key configured automatically fall back to the mock implementation,
so the app always runs.

---

## 🧪 Testing, linting, types

**Backend**

```bash
cd backend
ruff check . && ruff format --check .
mypy app
pytest
```

**Frontend**

```bash
cd frontend
npm run lint
npm run typecheck
npm run test -- --run
npm run build
```

CI ([`.github/workflows/ci.yml`](./.github/workflows/ci.yml)) runs all of the above
on every push and pull request.

---

## 🗂️ Project layout

```
nova/
├── DESIGN.md            # architecture + phased roadmap
├── docker-compose.yml   # postgres, redis, qdrant, api, web
├── backend/             # FastAPI (clean/hexagonal: domain · ports · adapters · services · api)
└── frontend/            # Next.js App Router (components · lib · stores)
```

The backend follows a **ports & adapters** design: `domain/` holds framework-free
entities and interfaces, `adapters/` implements them (SQLAlchemy, LLM/STT/TTS
providers), `services/` holds use-cases, and `api/` exposes REST + WebSocket.

---

## 🔒 Safety

Nova is designed so that any **destructive, financial, or booking** action requires
**explicit user confirmation** — the assistant never places orders, makes payments,
or deletes data on its own. See the confirmation-gate design in `DESIGN.md`.

## 🗺️ Roadmap

Phase 0 (scaffold) and **Phase 1 (core assistant)** are implemented. Phases 2–5 (RAG,
multi-agent tools, browser/shopping automation, vision, plugins) are specified in
`DESIGN.md` and built behind the existing interfaces.

## 📄 License

MIT (see `LICENSE`) — add your preferred license before publishing.
