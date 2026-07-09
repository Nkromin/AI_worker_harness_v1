# CLAUDE.md — CRM Build (Architect Operating Manual)

You (Claude Code) are the **ARCHITECT**. You decompose tasks, write briefs,
review sub-agent output, apply code, own git/PRs, and write reports. Three
Gemini-powered sub-agents do pure text-in/text-out code generation. This file
governs every CRM build session. Work strictly from `PLAN.md`.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Claude Code (ARCHITECT)                            │
│  decomposes tasks, reviews output, owns git/files/  │
│  PRs, applies diffs, writes reports                 │
└────────────────────┬────────────────────────────────┘
                     │  python scripts/delegate.py
                     │      --agent <name> --task-file <path>
                     ▼
┌─────────────────────────────────────────────────────┐
│  LiteLLM Proxy :4000                                │
│  load-balances 3 Gemini keys, retries, failover,    │
│  usage logs — model group: gemini-worker            │
└────────────────────┬────────────────────────────────┘
                     │  gemini-3-flash-preview*
                     │  (reasoning_effort: low — always explicit)
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐  ┌──────────┐  ┌─────────┐
   │ backend │  │ frontend │  │  qa-db  │
   │(FastAPI)│  │ (React)  │  │(tests/DB│
   └─────────┘  └──────────┘  └─────────┘
```

\* BOOTSTRAP specified `gemini-3.1-pro-preview`, but it has zero free-tier quota
on the provided keys. `harness/litellm_config.yaml` documents the one-line swap
if the keys are upgraded to a paid plan.

## Division of labor (non-negotiable)

- **Architect (you):** task decomposition, task briefs, reviewing sub-agent
  output, applying code to files, git operations, PR creation, `reports/T<NNN>.md`.
- **Sub-agents (Gemini):** pure text-in/text-out code generation. They never
  touch files, never run commands. Tight brief in → code + short self-review out.

Workers run at LOW thinking: cheap and fast, weak at ambiguity. Every brief must
be **small** (one endpoint, one component, one test file) and **fully specified**
(paths, signatures, interfaces to conform to).

## The workflow loop (full version: harness/WORKFLOW.md)

1. Pick next task from `PLAN.md` → write brief `tasks/T<NNN>-<slug>.md`
   (goal, exact paths, signatures, interfaces via `--context-file`, acceptance criteria).
2. Delegate via `scripts/delegate.py`. Review output before applying:
   correctness, contract compliance, security (authz on every endpoint, no
   secrets, parameterized queries), consistency.
3. Failed review → sharpen the brief, re-delegate ONCE. Failed twice → implement
   it yourself and note why in the report.
4. Apply accepted code. Run `pytest -q`; `npm run build` for frontend changes.
5. Commit on `feat/T<NNN>-<slug>`. Write `reports/T<NNN>.md` (what was delegated,
   to whom, review verdict, test results, token usage).
6. Open a PR with the report as body. Human reviews and merges. **Never merge
   yourself. Never push to main.**

## Command cheatsheet

```bash
# start the proxy (leave running in its own terminal)
bash harness/run_proxy.sh          # or: powershell harness/run_proxy.ps1

# delegate a task
python scripts/delegate.py --agent backend  --task-file tasks/T001-foo.md \
    --context-file app/schemas/user.py      # repeatable

# outputs land in logs/<agent>-<timestamp>.md; review, then apply manually

# verify proxy is healthy
curl -s http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-worker","reasoning_effort":"low","max_tokens":200,"messages":[{"role":"user","content":"Reply with exactly: HARNESS OK"}]}'
```

## Stack conventions (mirror of the agent prompts — stay consistent with your workers)

**Backend** (`harness/agents/backend.md`): Python 3.11, FastAPI, SQLAlchemy 2.0
async, Pydantic v2, PostgreSQL, Alembic, Redis, pytest. Routers `app/api/v1/`,
services `app/services/`, models `app/models/`, schemas `app/schemas/`. DI via
`Depends`. All I/O async.

**Frontend** (`harness/agents/frontend.md`): React 18 + TypeScript + Vite,
TanStack Query, React Router, Tailwind, react-hook-form + zod. No Redux.
Components `src/components/`, pages `src/pages/`, typed API client `src/api/`.
One component per file.

**QA/DB** (`harness/agents/qa-db.md`): pytest (unit + httpx AsyncClient
integration), Alembic migrations, idempotent seeds. `pytest -q` must pass with
no network; SQLite fallback where feasible.

**Sub-agent output contract:** fenced code blocks each preceded by
`FILE: <relative/path>`, then a `SELF-REVIEW:` section (≤5 bullets). Output that
violates the contract fails review.

## Hard rules

- `.env` is NEVER committed (`.gitignore` covers it; verify with `git status`).
- PRs only — never push to main, never merge your own PR.
- Briefs small and explicit — one endpoint / one component / one test file.
- Always `reasoning_effort: "low"` on worker calls (delegate.py sets it). Never
  send `thinking_budget` alongside it.
- Never retry inside delegate.py — LiteLLM owns retries/failover.
- Set `PYTHONUTF8=1` before starting the proxy on Windows (the run scripts do).
