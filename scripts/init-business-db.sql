-- ============================================================
-- XCEREBRO — BUSINESS DATA SCHEMAS (RehabBooks + DealEngine)
-- ============================================================
-- Run ONCE against the crew Postgres database on Railway:
--   railway run --service Xcerebro-Agents-2.0 -- \
--     python scripts/run-sql.py scripts/init-business-db.sql
--
-- These are the minimal tables backing the CFO / real-estate
-- agents' declared read tools. Data entry: SQL, CSV \copy, or a
-- future n8n form. Idempotent (IF NOT EXISTS everywhere).
-- ============================================================

CREATE EXTENSION IF NOT EXISTS vector;  -- pgvector, for knowledge.chunks embeddings

CREATE SCHEMA IF NOT EXISTS rehabbooks;
CREATE SCHEMA IF NOT EXISTS dealengine;
CREATE SCHEMA IF NOT EXISTS eos;
CREATE SCHEMA IF NOT EXISTS knowledge;

-- ── Knowledge base (RAG over business documents; pgvector) ────────────────────
-- Chunked + embedded documents (V/TO, SOPs, contracts) searchable by all
-- agents via kb.search. Also created idempotently by tools/knowledge.py.

CREATE TABLE IF NOT EXISTS knowledge.documents (
    id            SERIAL PRIMARY KEY,
    title         TEXT NOT NULL,
    source_type   TEXT NOT NULL DEFAULT 'drive',
    drive_file_id TEXT UNIQUE,
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS knowledge.chunks (
    id          SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES knowledge.documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content     TEXT NOT NULL,
    embedding   vector(1536)
);

CREATE INDEX IF NOT EXISTS idx_kb_chunks_embedding_hnsw
    ON knowledge.chunks USING hnsw (embedding vector_cosine_ops);

-- ── EOS: Vision/Traction Organizer (extracted from Google Drive V/TO doc) ─────
-- Injected into every Tier-A (leadership) agent invocation.
-- Quarterly rocks live in ClickUp (single source of truth), NOT here.

CREATE TABLE IF NOT EXISTS eos.vto (
    section    TEXT PRIMARY KEY,   -- mission | vision | core_values | ten_year_target |
                                   -- marketing_strategy | three_year_picture | one_year_plan | issues
    content    TEXT NOT NULL,
    source_doc TEXT,               -- Drive doc name/id it was extracted from
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── RehabBooks: accounting, personal finance, investments ────

CREATE TABLE IF NOT EXISTS rehabbooks.projects (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    address     TEXT,
    status      TEXT NOT NULL DEFAULT 'active',   -- active | listed | sold | archived
    budget      NUMERIC(12,2),
    start_date  DATE,
    deadline    DATE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rehabbooks.transactions (
    id           SERIAL PRIMARY KEY,
    date         DATE NOT NULL,
    amount       NUMERIC(12,2) NOT NULL,          -- negative = expense, positive = income
    category     TEXT,
    entity       TEXT NOT NULL DEFAULT 'personal', -- rehabco | notary | personal
    project_id   INTEGER REFERENCES rehabbooks.projects(id),
    description  TEXT,
    needs_review BOOLEAN NOT NULL DEFAULT false,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON rehabbooks.transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_entity ON rehabbooks.transactions(entity);

CREATE TABLE IF NOT EXISTS rehabbooks.accounts (
    id       SERIAL PRIMARY KEY,
    name     TEXT NOT NULL,
    type     TEXT NOT NULL,                        -- checking | savings | credit
    balance  NUMERIC(12,2) NOT NULL DEFAULT 0,
    entity   TEXT NOT NULL DEFAULT 'personal',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rehabbooks.budget_items (
    id         SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES rehabbooks.projects(id),
    category   TEXT NOT NULL,
    budgeted   NUMERIC(12,2) NOT NULL DEFAULT 0,
    actual     NUMERIC(12,2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS rehabbooks.investor_loans (
    id           SERIAL PRIMARY KEY,
    lender       TEXT NOT NULL,
    principal    NUMERIC(12,2) NOT NULL,
    rate         NUMERIC(5,2),                     -- annual %
    payment_due  DATE,
    project_id   INTEGER REFERENCES rehabbooks.projects(id)
);

-- ── DealEngine: deal analysis, rehab budgets, draws ──────────

CREATE TABLE IF NOT EXISTS dealengine.properties (
    id             SERIAL PRIMARY KEY,
    address        TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'analyzing', -- analyzing | under_contract | owned | sold | passed
    arv            NUMERIC(12,2),
    purchase_price NUMERIC(12,2),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS dealengine.deal_analyses (
    id          SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES dealengine.properties(id),
    strategy    TEXT NOT NULL,                     -- flip | wholesale | buy_hold | subto | creative
    offer_price NUMERIC(12,2),
    est_profit  NUMERIC(12,2),
    notes       TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS dealengine.project_draws (
    id           SERIAL PRIMARY KEY,
    project_id   INTEGER REFERENCES rehabbooks.projects(id),
    amount       NUMERIC(12,2) NOT NULL,
    status       TEXT NOT NULL DEFAULT 'pending',  -- pending | approved | funded
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
