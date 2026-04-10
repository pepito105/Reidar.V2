# V3 Backend Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap the Reidar V3 FastAPI backend: venv, config, async database layer, CORS app, Alembic wired for async, Layer 1 SQLAlchemy models, and the first migration file.

**Architecture:** Module-level async SQLAlchemy engine (`create_async_engine` + `async_sessionmaker`) with PgBouncer-compatible `statement_cache_size=0`. Pydantic-settings loads all env from `backend/.env`. Vector extension created in FastAPI startup event (not in migrations). Alembic URL injected at runtime from config.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy 2.x async, asyncpg, Alembic, pgvector, pydantic-settings, pytest, pytest-asyncio

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `venv/` | Create | Python 3.11 virtualenv (gitignored) |
| `backend/requirements.txt` | Create | Pinned deps from pip freeze |
| `backend/pytest.ini` | Create | Test runner config |
| `backend/tests/__init__.py` | Create | Makes tests a package |
| `backend/tests/conftest.py` | Create | (empty — no shared fixtures needed) |
| `backend/app/__init__.py` | Create | Package marker |
| `backend/app/core/__init__.py` | Create | Package marker |
| `backend/app/models/__init__.py` | Create | Imports all models for Alembic |
| `backend/app/core/config.py` | Create | pydantic-settings BaseSettings, 9 env vars |
| `backend/app/core/database.py` | Create | Engine, AsyncSessionLocal, get_db, Base, create_vector_extension |
| `backend/app/main.py` | Create | FastAPI app, CORS, /health, startup event |
| `backend/alembic.ini` | Create | Alembic config, blank sqlalchemy.url |
| `backend/alembic/env.py` | Create | Async migration runner |
| `backend/app/models/global_kb.py` | Create | 8 Layer 1 SQLAlchemy models |
| `backend/alembic/versions/xxxx_layer1_global_knowledge_base.py` | Generate | First migration (not executed) |
| `backend/tests/test_config.py` | Create | Config field declarations |
| `backend/tests/test_database.py` | Create | Engine, session factory, get_db shape |
| `backend/tests/test_main.py` | Create | /health endpoint, CORS middleware |
| `backend/tests/test_global_kb.py` | Create | Model columns, constraints, no firm_id |

---

## Task 1: Create venv and install dependencies

**Files:**
- Create: `venv/` (at repo root `~/Desktop/reidar-v3/venv`)
- Create: `backend/requirements.txt`

- [ ] **Step 1: Create the venv**

```bash
/opt/homebrew/bin/python3.11 -m venv ~/Desktop/reidar-v3/venv
```

Expected: `venv/` directory appears with `bin/`, `lib/`, `pyvenv.cfg`.

- [ ] **Step 2: Install all dependencies**

```bash
~/Desktop/reidar-v3/venv/bin/pip install \
  fastapi \
  "uvicorn[standard]" \
  "sqlalchemy[asyncio]" \
  asyncpg \
  alembic \
  pgvector \
  pydantic \
  pydantic-settings \
  python-dotenv \
  anthropic \
  openai \
  httpx \
  "python-jose[cryptography]" \
  sendgrid \
  pytest \
  pytest-asyncio
```

Expected: All packages install without errors.

- [ ] **Step 3: Save requirements.txt**

```bash
~/Desktop/reidar-v3/venv/bin/pip freeze > ~/Desktop/reidar-v3/backend/requirements.txt
```

Expected: `backend/requirements.txt` is created with pinned versions.

- [ ] **Step 4: Commit**

```bash
cd ~/Desktop/reidar-v3 && git add backend/requirements.txt && git commit -m "feat: add requirements.txt"
```

---

## Task 2: Set up test infrastructure

**Files:**
- Create: `backend/pytest.ini`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Create pytest.ini**

`backend/pytest.ini`:
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
pythonpath = .
```

- [ ] **Step 2: Create package markers**

`backend/tests/__init__.py`: empty file.

`backend/tests/conftest.py`: empty file.

`backend/app/__init__.py`: empty file.

`backend/app/core/__init__.py`: empty file.

`backend/app/models/__init__.py`: empty file (will be filled in Task 8).

- [ ] **Step 3: Verify pytest is runnable**

```bash
cd ~/Desktop/reidar-v3/backend && ~/Desktop/reidar-v3/venv/bin/pytest --collect-only
```

Expected output:
```
======================== no tests ran ===========================
```

No errors. If `ModuleNotFoundError` appears, confirm `pythonpath = .` is in `pytest.ini` and you are running from `backend/`.

- [ ] **Step 4: Commit**

```bash
cd ~/Desktop/reidar-v3 && git add backend/pytest.ini backend/tests/ backend/app/__init__.py backend/app/core/__init__.py backend/app/models/__init__.py && git commit -m "feat: test infrastructure and package markers"
```

---

## Task 3: config.py

**Files:**
- Create: `backend/app/core/config.py`
- Create: `backend/tests/test_config.py`

- [ ] **Step 1: Write the failing test**

`backend/tests/test_config.py`:
```python
def test_settings_declares_all_required_fields():
    """All 9 required env vars must be declared as fields on Settings."""
    from app.core.config import Settings

    required_fields = {
        "DATABASE_URL",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "BRAVE_API_KEY",
        "SENDGRID_API_KEY",
        "CLERK_SECRET_KEY",
        "NOTIFICATION_EMAIL",
        "FROM_EMAIL",
        "APP_URL",
    }
    declared = set(Settings.model_fields.keys())
    missing = required_fields - declared
    assert not missing, f"Settings is missing fields: {missing}"
```

- [ ] **Step 2: Run to confirm it fails**

```bash
cd ~/Desktop/reidar-v3/backend && ~/Desktop/reidar-v3/venv/bin/pytest tests/test_config.py -v
```

Expected: `ERROR` — `ModuleNotFoundError: No module named 'app.core.config'`

- [ ] **Step 3: Write config.py**

`backend/app/core/config.py`:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str
    BRAVE_API_KEY: str
    SENDGRID_API_KEY: str
    CLERK_SECRET_KEY: str
    NOTIFICATION_EMAIL: str
    FROM_EMAIL: str
    APP_URL: str


settings = Settings()
```

- [ ] **Step 4: Run to confirm it passes**

```bash
cd ~/Desktop/reidar-v3/backend && ~/Desktop/reidar-v3/venv/bin/pytest tests/test_config.py -v
```

Expected:
```
PASSED tests/test_config.py::test_settings_declares_all_required_fields
```

- [ ] **Step 5: Commit**

```bash
cd ~/Desktop/reidar-v3 && git add backend/app/core/config.py backend/tests/test_config.py && git commit -m "feat: pydantic-settings config"
```

---

## Task 4: database.py

**Files:**
- Create: `backend/app/core/database.py`
- Create: `backend/tests/test_database.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_database.py`:
```python
import inspect


def test_get_db_is_async_generator():
    """get_db must be an async generator for use with FastAPI Depends()."""
    from app.core.database import get_db
    assert inspect.isasyncgenfunction(get_db)


def test_engine_exists():
    """Module-level engine must be created on import."""
    from app.core.database import engine
    assert engine is not None


def test_async_session_local_exists():
    """AsyncSessionLocal factory must be available on import."""
    from app.core.database import AsyncSessionLocal
    assert AsyncSessionLocal is not None


def test_base_has_metadata():
    """Base must be a declarative base with metadata for Alembic."""
    from app.core.database import Base
    assert hasattr(Base, "metadata")
    assert hasattr(Base, "registry")


def test_create_vector_extension_is_coroutine():
    """create_vector_extension must be an async function."""
    from app.core.database import create_vector_extension
    assert inspect.iscoroutinefunction(create_vector_extension)
```

- [ ] **Step 2: Run to confirm all fail**

```bash
cd ~/Desktop/reidar-v3/backend && ~/Desktop/reidar-v3/venv/bin/pytest tests/test_database.py -v
```

Expected: All 5 tests `ERROR` with `ModuleNotFoundError`.

- [ ] **Step 3: Write database.py**

`backend/app/core/database.py`:
```python
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"statement_cache_size": 0},
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def create_vector_extension() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
```

- [ ] **Step 4: Run to confirm all pass**

```bash
cd ~/Desktop/reidar-v3/backend && ~/Desktop/reidar-v3/venv/bin/pytest tests/test_database.py -v
```

Expected:
```
PASSED tests/test_database.py::test_get_db_is_async_generator
PASSED tests/test_database.py::test_engine_exists
PASSED tests/test_database.py::test_async_session_local_exists
PASSED tests/test_database.py::test_base_has_metadata
PASSED tests/test_database.py::test_create_vector_extension_is_coroutine
```

- [ ] **Step 5: Commit**

```bash
cd ~/Desktop/reidar-v3 && git add backend/app/core/database.py backend/tests/test_database.py && git commit -m "feat: async SQLAlchemy engine, session factory, Base"
```

---

## Task 5: main.py

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/tests/test_main.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_main.py`:
```python
from unittest.mock import AsyncMock, patch


def test_health_endpoint():
    """GET /health must return 200 with status and version."""
    with patch("app.main.create_vector_extension", new_callable=AsyncMock):
        from fastapi.testclient import TestClient
        from app.main import app
        with TestClient(app) as client:
            response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "v3"}


def test_cors_middleware_present():
    """CORSMiddleware must be registered on the app."""
    from app.main import app
    middleware_names = [m.cls.__name__ for m in app.user_middleware]
    assert "CORSMiddleware" in middleware_names
```

- [ ] **Step 2: Run to confirm they fail**

```bash
cd ~/Desktop/reidar-v3/backend && ~/Desktop/reidar-v3/venv/bin/pytest tests/test_main.py -v
```

Expected: Both tests `ERROR` with `ModuleNotFoundError`.

- [ ] **Step 3: Write main.py**

`backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_vector_extension

app = FastAPI(title="Reidar V3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.on_event("startup")
async def startup() -> None:
    await create_vector_extension()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": "v3"}
```

- [ ] **Step 4: Run to confirm both pass**

```bash
cd ~/Desktop/reidar-v3/backend && ~/Desktop/reidar-v3/venv/bin/pytest tests/test_main.py -v
```

Expected:
```
PASSED tests/test_main.py::test_health_endpoint
PASSED tests/test_main.py::test_cors_middleware_present
```

- [ ] **Step 5: Commit**

```bash
cd ~/Desktop/reidar-v3 && git add backend/app/main.py backend/tests/test_main.py && git commit -m "feat: FastAPI app, CORS, /health, startup vector extension"
```

---

## Task 6: Initialize Alembic

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py` (replace auto-generated)
- Create: `backend/alembic/script.py.mako` (auto-generated, keep as-is)

- [ ] **Step 1: Run alembic init from backend/**

```bash
cd ~/Desktop/reidar-v3/backend && ~/Desktop/reidar-v3/venv/bin/alembic init alembic
```

Expected: Creates `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, `alembic/versions/`.

- [ ] **Step 2: Edit alembic.ini**

In `backend/alembic.ini`, find the line `sqlalchemy.url = driver://user:pass@localhost/dbname` and replace it with:

```ini
sqlalchemy.url =
```

Leave it blank. The URL is injected at runtime by `env.py`. Also confirm this line exists (it should after `alembic init`):

```ini
prepend_sys_path = .
```

If it's missing, add it under `[alembic]`.

- [ ] **Step 3: Replace alembic/env.py**

Replace the entire contents of `backend/alembic/env.py` with:

```python
import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Ensure backend/ is on sys.path so app.* imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings  # noqa: E402
from app.models import Base  # noqa: E402  — imports all models via __init__.py

config = context.config

# Inject the real DATABASE_URL at runtime
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Generate a SQL script without a live DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 4: Commit**

```bash
cd ~/Desktop/reidar-v3 && git add backend/alembic.ini backend/alembic/ && git commit -m "feat: Alembic async setup"
```

---

## Task 7: Layer 1 models (global_kb.py)

**Files:**
- Create: `backend/app/models/global_kb.py`
- Create: `backend/tests/test_global_kb.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_global_kb.py`:
```python
def test_all_models_have_correct_tablenames():
    from app.models.global_kb import (
        Company, Founder, CompanyFounder,
        Investor, FundingRound, RoundInvestor,
        GlobalSignal, CompanyEmbedding,
    )
    assert Company.__tablename__ == "companies"
    assert Founder.__tablename__ == "founders"
    assert CompanyFounder.__tablename__ == "company_founders"
    assert Investor.__tablename__ == "investors"
    assert FundingRound.__tablename__ == "funding_rounds"
    assert RoundInvestor.__tablename__ == "round_investors"
    assert GlobalSignal.__tablename__ == "global_signals"
    assert CompanyEmbedding.__tablename__ == "company_embeddings"


def test_company_has_required_columns():
    from app.models.global_kb import Company
    col_names = {c.name for c in Company.__table__.columns}
    for col in [
        "id", "name", "slug", "domain", "sector", "stage",
        "source", "scraped_at", "updated_at", "created_at",
        "one_liner", "description", "tags", "ai_nativeness",
        "total_raised_usd", "last_round_type", "founding_year",
        "enrichment_status", "harmonic_id", "yc_id",
    ]:
        assert col in col_names, f"Company missing column: {col}"


def test_no_firm_id_on_layer1_tables():
    """Layer 1 tables must NEVER have a firm_id column. Schema Rule #1."""
    from app.models.global_kb import Company, Founder, Investor, FundingRound, GlobalSignal
    for model in [Company, Founder, Investor, FundingRound, GlobalSignal]:
        col_names = {c.name for c in model.__table__.columns}
        assert "firm_id" not in col_names, (
            f"{model.__name__} must not have firm_id (Layer 1 tables are global)"
        )


def test_company_embedding_pool1_check_constraint():
    """Pool 1 embeddings must enforce firm_id IS NULL at DB level. Schema Rule #3."""
    from app.models.global_kb import CompanyEmbedding
    from sqlalchemy import CheckConstraint
    check_names = {
        c.name for c in CompanyEmbedding.__table__.constraints
        if isinstance(c, CheckConstraint)
    }
    assert "pool1_no_firm_id" in check_names


def test_company_embedding_has_vector_column():
    from app.models.global_kb import CompanyEmbedding
    from pgvector.sqlalchemy import Vector
    col = CompanyEmbedding.__table__.c.embedding
    assert isinstance(col.type, Vector)


def test_funding_round_fk_to_companies():
    from app.models.global_kb import FundingRound
    fk_targets = {
        list(col.foreign_keys)[0].target_fullname
        for col in FundingRound.__table__.columns
        if col.foreign_keys
    }
    assert "companies.id" in fk_targets


def test_global_signal_fk_to_companies():
    from app.models.global_kb import GlobalSignal
    fk_targets = {
        list(col.foreign_keys)[0].target_fullname
        for col in GlobalSignal.__table__.columns
        if col.foreign_keys
    }
    assert "companies.id" in fk_targets


def test_company_founder_composite_pk():
    from app.models.global_kb import CompanyFounder
    pk_cols = {c.name for c in CompanyFounder.__table__.primary_key.columns}
    assert pk_cols == {"company_id", "founder_id"}


def test_round_investor_composite_pk():
    from app.models.global_kb import RoundInvestor
    pk_cols = {c.name for c in RoundInvestor.__table__.primary_key.columns}
    assert pk_cols == {"round_id", "investor_id"}
```

- [ ] **Step 2: Run to confirm all fail**

```bash
cd ~/Desktop/reidar-v3/backend && ~/Desktop/reidar-v3/venv/bin/pytest tests/test_global_kb.py -v
```

Expected: All 9 tests `ERROR` with `ModuleNotFoundError`.

- [ ] **Step 3: Write global_kb.py**

`backend/app/models/global_kb.py`:
```python
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.core.database import Base


# ---------------------------------------------------------------------------
# Layer 1 — Global Knowledge Base
# No firm_id on any table in this layer. Schema Rule #1.
# ---------------------------------------------------------------------------


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identity
    name = Column(Text, nullable=False)
    slug = Column(Text, unique=True, nullable=False)
    website = Column(Text)
    domain = Column(Text)

    # Description
    one_liner = Column(Text)
    description = Column(Text)
    business_model = Column(Text)
    target_customer = Column(Text)

    # Classification
    sector = Column(Text)
    subsector = Column(Text)
    tags = Column(ARRAY(Text))
    ai_nativeness = Column(SmallInteger)

    # Stage & Funding
    stage = Column(Text)
    total_raised_usd = Column(BigInteger)
    last_round_type = Column(Text)
    last_round_usd = Column(BigInteger)
    last_round_date = Column(Date)
    valuation_usd = Column(BigInteger)

    # Team
    employee_count = Column(Integer)
    founding_year = Column(Integer)
    headquarters = Column(Text)

    # Source tracking
    source = Column(Text, nullable=False)
    source_url = Column(Text)
    source_batch = Column(Text)
    harmonic_id = Column(Text)
    yc_id = Column(Text)

    # Quality
    enrichment_status = Column(Text, default="raw")
    last_enriched_at = Column(DateTime(timezone=True))

    # Timestamps
    founded_at = Column(Date)
    scraped_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_companies_domain", "domain"),
        Index("idx_companies_sector", "sector"),
        Index("idx_companies_stage", "stage"),
        Index("idx_companies_source", "source"),
        Index("idx_companies_created_at", "created_at"),
    )


class Founder(Base):
    __tablename__ = "founders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identity
    name = Column(Text, nullable=False)
    email = Column(Text)
    linkedin_url = Column(Text)
    twitter_url = Column(Text)

    # Background
    prior_companies = Column(ARRAY(Text))
    prior_roles = Column(ARRAY(Text))
    education = Column(ARRAY(Text))
    domain_years = Column(Integer)

    # Founder signals
    prior_exits = Column(Boolean, default=False)
    repeat_founder = Column(Boolean, default=False)
    technical = Column(Boolean)
    domain_expert = Column(Boolean)

    # Source
    source = Column(Text)
    source_url = Column(Text)

    # Timestamps
    scraped_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class CompanyFounder(Base):
    __tablename__ = "company_founders"

    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    founder_id = Column(
        UUID(as_uuid=True),
        ForeignKey("founders.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    role = Column(Text)
    is_primary = Column(Boolean, default=False)


class Investor(Base):
    __tablename__ = "investors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    type = Column(Text)
    tier = Column(SmallInteger)
    focus_stages = Column(ARRAY(Text))
    focus_sectors = Column(ARRAY(Text))
    website = Column(Text)
    crunchbase_url = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class FundingRound(Base):
    __tablename__ = "funding_rounds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    round_type = Column(Text, nullable=False)
    amount_usd = Column(BigInteger)
    valuation_usd = Column(BigInteger)
    announced_date = Column(Date)
    closed_date = Column(Date)
    lead_investor = Column(Text)
    notable_investors = Column(ARRAY(Text))
    source_url = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_funding_rounds_company", "company_id"),
        Index("idx_funding_rounds_date", "announced_date"),
    )


class RoundInvestor(Base):
    __tablename__ = "round_investors"

    round_id = Column(
        UUID(as_uuid=True),
        ForeignKey("funding_rounds.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    investor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("investors.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    is_lead = Column(Boolean, default=False)


class GlobalSignal(Base):
    __tablename__ = "global_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    signal_type = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    source_url = Column(Text, nullable=False)
    source_name = Column(Text)
    signal_strength = Column(SmallInteger)
    sentiment = Column(Text)
    published_at = Column(DateTime(timezone=True))
    detected_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_global_signals_company", "company_id"),
        Index("idx_global_signals_type", "signal_type"),
        Index("idx_global_signals_detected", "detected_at"),
    )


class CompanyEmbedding(Base):
    """Pool 1 embeddings. firm_id is ALWAYS NULL. Enforced by CHECK constraint."""

    __tablename__ = "company_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    firm_id = Column(UUID(as_uuid=True), nullable=True, default=None)
    embedding_type = Column(Text, nullable=False)
    content_hash = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    model_version = Column(Text, nullable=False, default="text-embedding-3-small")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("firm_id IS NULL", name="pool1_no_firm_id"),
        Index("idx_company_embeddings_company", "company_id"),
        Index("idx_company_embeddings_type", "embedding_type"),
    )
```

- [ ] **Step 4: Run to confirm all 9 tests pass**

```bash
cd ~/Desktop/reidar-v3/backend && ~/Desktop/reidar-v3/venv/bin/pytest tests/test_global_kb.py -v
```

Expected: All 9 tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
cd ~/Desktop/reidar-v3 && git add backend/app/models/global_kb.py backend/tests/test_global_kb.py && git commit -m "feat: Layer 1 global knowledge base models"
```

---

## Task 8: models/__init__.py

**Files:**
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: Write __init__.py**

`backend/app/models/__init__.py`:
```python
from app.models.global_kb import (  # noqa: F401
    Company,
    CompanyEmbedding,
    CompanyFounder,
    Founder,
    FundingRound,
    GlobalSignal,
    Investor,
    RoundInvestor,
)
```

- [ ] **Step 2: Verify all tests still pass**

```bash
cd ~/Desktop/reidar-v3/backend && ~/Desktop/reidar-v3/venv/bin/pytest -v
```

Expected: All tests `PASSED`. Count should be 17 (1 config + 5 database + 2 main + 9 global_kb = 17). If any fail, check for circular imports.

- [ ] **Step 3: Commit**

```bash
cd ~/Desktop/reidar-v3 && git add backend/app/models/__init__.py && git commit -m "feat: models __init__ for Alembic autogenerate"
```

---

## Task 9: Generate first Alembic migration

**Files:**
- Generate: `backend/alembic/versions/xxxx_layer1_global_knowledge_base.py`

- [ ] **Step 1: Generate the migration**

```bash
cd ~/Desktop/reidar-v3/backend && ~/Desktop/reidar-v3/venv/bin/alembic revision --autogenerate -m "layer1_global_knowledge_base"
```

Expected: Output like:
```
Generating /Users/remibalassanian/Desktop/reidar-v3/backend/alembic/versions/xxxx_layer1_global_knowledge_base.py ... done
```

If you get a `ModuleNotFoundError`, confirm you are running from `backend/` and that `prepend_sys_path = .` is in `alembic.ini`.

- [ ] **Step 2: Review the generated migration**

Open `backend/alembic/versions/xxxx_layer1_global_knowledge_base.py`. Verify:
- `upgrade()` contains `op.create_table("companies", ...)`, `op.create_table("founders", ...)` etc. for all 8 tables
- `op.create_index(...)` calls are present for all declared indexes
- The `pool1_no_firm_id` check constraint appears in `company_embeddings`
- `downgrade()` calls `op.drop_table(...)` for each table in reverse order

**DO NOT run `alembic upgrade head`** — Remi runs migrations manually.

- [ ] **Step 3: Final commit and push**

```bash
cd ~/Desktop/reidar-v3 && git add -A && git commit -m "feat: FastAPI setup, Layer 1 models, first migration" && git push
```

Expected: Push succeeds to `main`.

---

## Full Test Run Reference

After all tasks are complete, run the full suite from `backend/`:

```bash
cd ~/Desktop/reidar-v3/backend && ~/Desktop/reidar-v3/venv/bin/pytest -v
```

Expected — all 17 tests pass:
```
PASSED tests/test_config.py::test_settings_declares_all_required_fields
PASSED tests/test_database.py::test_get_db_is_async_generator
PASSED tests/test_database.py::test_engine_exists
PASSED tests/test_database.py::test_async_session_local_exists
PASSED tests/test_database.py::test_base_has_metadata
PASSED tests/test_database.py::test_create_vector_extension_is_coroutine
PASSED tests/test_main.py::test_health_endpoint
PASSED tests/test_main.py::test_cors_middleware_present
PASSED tests/test_global_kb.py::test_all_models_have_correct_tablenames
PASSED tests/test_global_kb.py::test_company_has_required_columns
PASSED tests/test_global_kb.py::test_no_firm_id_on_layer1_tables
PASSED tests/test_global_kb.py::test_company_embedding_pool1_check_constraint
PASSED tests/test_global_kb.py::test_company_embedding_has_vector_column
PASSED tests/test_global_kb.py::test_funding_round_fk_to_companies
PASSED tests/test_global_kb.py::test_global_signal_fk_to_companies
PASSED tests/test_global_kb.py::test_company_founder_composite_pk
PASSED tests/test_global_kb.py::test_round_investor_composite_pk
```
