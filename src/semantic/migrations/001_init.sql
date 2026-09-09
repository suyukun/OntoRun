-- 001_init.sql: app persistence for the semantic service (product doc appendix D).
-- Delete semantics: hidden flag only — physical rows are preserved for audit.

CREATE TABLE IF NOT EXISTS conversations (
    id          TEXT PRIMARY KEY,
    title       TEXT    NOT NULL,
    pinned      INTEGER NOT NULL DEFAULT 0,
    starred     INTEGER NOT NULL DEFAULT 0,
    hidden      INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id              TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role            TEXT NOT NULL,            -- user | assistant
    question        TEXT,                     -- asked question (kept on both rows)
    request_id      TEXT,                     -- trace link (assistant messages)
    state           TEXT,                     -- eight-state snapshot (assistant messages)
    answer          TEXT,
    result_json     TEXT,                     -- full final result snapshot (replay = snapshot)
    created_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);

CREATE TABLE IF NOT EXISTS idempotency (
    client_request_id TEXT PRIMARY KEY,
    request_id        TEXT NOT NULL UNIQUE,
    created_at        TEXT NOT NULL
);

-- History delete = hidden marker; trace JSONL stays append-only (audit chain).
CREATE TABLE IF NOT EXISTS history_hidden (
    request_id TEXT PRIMARY KEY,
    hidden_at  TEXT NOT NULL
);
