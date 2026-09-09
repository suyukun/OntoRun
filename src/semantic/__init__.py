"""OntoRun semantic interface service (T1).

Engineering-grade migration of scripts/fortune_demo (rule registry, decision-chain
event stream, LLM routing with keyword fallback), plus: structured eight-state
mapping, session/message persistence, client_request_id idempotency, error codes,
LLM-output sanitization and PII guards. Product contract: docs/财富广场-ChatBI展示层产品设计_v0.2.md.
"""
