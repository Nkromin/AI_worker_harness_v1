# AI Worker Harness — CRM Build

A CRM application built by a multi-agent harness: Claude Code acts as the
ARCHITECT (task decomposition, review, git/PRs) and delegates implementation
to three Gemini-powered sub-agents through a local LiteLLM proxy. See
`CLAUDE.md` for the operating manual and `PLAN.md` for the build plan.

## Repo layout

| Path        | Purpose                                                            |
|-------------|--------------------------------------------------------------------|
| `backend/`  | FastAPI application (Python 3.11, SQLAlchemy 2.0 async, Postgres)  |
| `frontend/` | React 18 + TypeScript + Vite app (TanStack Query, Tailwind)        |
| `harness/`  | LiteLLM proxy config, run scripts, agent prompts, WORKFLOW.md      |
| `scripts/`  | `delegate.py` — sends task briefs to sub-agents via the proxy      |
| `tasks/`    | Task briefs (`T<NNN>-<slug>.md`) written by the Architect          |
| `reports/`  | Per-task reports: what was delegated, review verdict, test results |
| `logs/`     | Raw sub-agent outputs (git-ignored)                                |

## Quick start

```bash
cp .env.example .env          # fill in your Gemini keys
bash harness/run_proxy.sh     # start the LiteLLM proxy on :4000
python scripts/delegate.py --agent backend --task-file tasks/<brief>.md
```
