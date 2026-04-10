# Reidar V3 — Backend Setup Design

**Date:** 2026-04-10  
**Scope:** Steps 1–9 of the V3 backend bootstrap: venv, dependencies, core modules, Alembic, Layer 1 models, first migration, initial commit.  
**Status:** Approved

---

## 1. What We're Building

A clean FastAPI backend foundation for Reidar V3. No business logic yet — just the skeleton every subsequent feature will build on:

- Python venv + pinned dependencies
- Pydantic-settings config layer
- Async SQLAlchemy engine (asyncpg + Supabase-compatible)
- Minimal FastAPI app with CORS and `/health`
- Alembic wired for async migrations
- Layer 1 (Global Knowledge Base) SQLAlchemy models
- First migration file (not executed — run manually)

---

## 2. File Layout

```
reidar-v3/
├── venv/                              # Python 3.11 venv (gitignored)
└── backend/
    ├── .env                           # exists, never modified
    ├── requirements.txt               # pip freeze output
    ├── alembic.ini                    # Alembic config (URL injected at runtime)
    ├── alembic/
    │   ├── env.py                     # async migration runner
    │   ├── script.py.mako
    │   └── versions/
    │       └── xxxx_layer1_global_knowledge_base.py
    └── app/
        ├── main.py
        ├── core/
        │   ├── config.py
        │   └── database.py
        └── models/
            ├── __init__.py
            └── global_kb.py
```

---

## 3. Dependencies (`requirements.txt`)

Installed into `~/Desktop/reidar-v3/venv` via `/opt/homebrew/bin/python3.11`.

| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn[standard]` | ASGI server |
| `sqlalchemy[asyncio]` | ORM + async support |
| `asyncpg` | Async PostgreSQL driver |
| `alembic` | Schema migrations |
| `pgvector` | Vector column type for SQLAlchemy |
| `pydantic` | Data validation |
| `pydantic-settings` | BaseSettings / env loading |
| `python-dotenv` | .env loading |
| `anthropic` | Claude API |
| `openai` | Embeddings (text-embedding-3-small) |
| `httpx` | Async HTTP for scrapers |
| `python-jose[cryptography]` | JWT decoding (Clerk tokens) |
| `sendgrid` | Email delivery |

Saved via `pip freeze > backend/requirements.txt`.

---

## 4. `backend/app/core/config.py`

`pydantic-settings` `BaseSettings` subclass. Loads from `backend/.env`.

**Variables (all `str`, all required — missing var = startup failure):**
- `DATABASE_URL`
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `BRAVE_API_KEY`
- `SENDGRID_API_KEY`
- `CLERK_SECRET_KEY`
- `NOTIFICATION_EMAIL`
- `FROM_EMAIL`
- `APP_URL`

Module-level `settings = Settings()` singleton imported everywhere.

---

## 5. `backend/app/core/database.py`

**Engine:**
```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"statement_cache_size": 0},  # required for Supabase PgBouncer
)
```

**Session factory:**
```python
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

**`get_db` dependency:**
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

**`create_vector_extension()`:**
```python
async def create_vector_extension():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
```
Called from `main.py` startup event. Not in migrations.

**`Base`:** `declarative_base()` defined here, imported by all models.

---

## 6. `backend/app/main.py`

```python
app = FastAPI(title="Reidar V3")

app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.on_event("startup")
async def startup():
    await create_vector_extension()

@app.get("/health")
async def health():
    return {"status": "ok", "version": "v3"}
```

---

## 7. Alembic Setup

**`alembic.ini`:**
- `script_location = alembic` (relative to `backend/`)
- `sqlalchemy.url` left blank — overridden at runtime by `env.py`
- Run location: always from `backend/` directory

**`alembic/env.py`:**
- Imports `settings` from `app.core.config`
- Imports `Base` from `app.models` (triggers all model imports via `__init__.py`)
- Sets `config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)`
- `target_metadata = Base.metadata`
- Online migrations use `asyncio.run(run_async_migrations())` pattern
- Offline mode kept for SQL script generation

**Running migrations (manual only):**
```bash
cd backend && alembic upgrade head
```
Never automated. Never in Procfile.

---

## 8. Layer 1 Models (`backend/app/models/global_kb.py`)

All 8 models mirror `reidar_v3_schema.md` exactly — every column, index, and constraint.

| Model | Table | Notable |
|---|---|---|
| `Company` | `companies` | `tags ARRAY(Text)`, 5 indexes |
| `Founder` | `founders` | `prior_companies`, `prior_roles`, `education` arrays |
| `CompanyFounder` | `company_founders` | Composite PK, join table |
| `Investor` | `investors` | `focus_stages`, `focus_sectors` arrays |
| `FundingRound` | `funding_rounds` | FK → companies, 2 indexes |
| `RoundInvestor` | `round_investors` | Composite PK, join table |
| `GlobalSignal` | `global_signals` | FK → companies, 3 indexes |
| `CompanyEmbedding` | `company_embeddings` | `Vector(1536)`, `firm_id DEFAULT NULL`, `CHECK (firm_id IS NULL)` |

**Key implementation details:**
- `from pgvector.sqlalchemy import Vector` for the embedding column
- `from sqlalchemy.dialects.postgresql import ARRAY, JSONB` for array/json columns
- `CheckConstraint("firm_id IS NULL", name="pool1_no_firm_id")` in `__table_args__`
- All indexes declared as `Index(...)` in `__table_args__`
- No `firm_id` column on any Layer 1 table except `company_embeddings` (where it is always NULL)

---

## 9. `backend/app/models/__init__.py`

```python
from app.models.global_kb import (
    Company, Founder, CompanyFounder,
    Investor, FundingRound, RoundInvestor,
    GlobalSignal, CompanyEmbedding,
)
```

Ensures `Base.metadata` is populated when Alembic imports `Base`.

---

## 10. First Migration

Generated (not run):
```bash
cd backend && alembic revision --autogenerate -m "layer1_global_knowledge_base"
```

Produces `alembic/versions/xxxx_layer1_global_knowledge_base.py`.  
You run `alembic upgrade head` manually after reviewing.

---

## 11. Commit

```bash
git add -A && git commit -m "feat: FastAPI setup, Layer 1 models, first migration"
git push
```

---

## Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| Vector extension setup | FastAPI startup event | Simple, guaranteed before any query, visible |
| PgBouncer compatibility | `statement_cache_size=0` | Prevents prepared statement errors with Supabase |
| Session factory | `async_sessionmaker` (SQLAlchemy 2.x) | Idiomatic, clean `Depends(get_db)` pattern |
| Alembic URL | Injected from `config.py` at runtime | Single source of truth for DATABASE_URL |
| Layer 1 firm_id | Not present on global tables | Schema rule #1 — global tables never have firm_id |
| Pool 1 CHECK constraint | `firm_id IS NULL` enforced in DB | Schema rule #3 — pools never cross-contaminate |
