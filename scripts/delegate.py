#!/usr/bin/env python3
"""Delegate a task brief to a Gemini sub-agent via the local LiteLLM proxy.

Usage:
    python scripts/delegate.py --agent backend --task-file tasks/T001-health.md \
        [--context-file app/schemas/user.py ...] [--out logs/backend-<ts>.md]

The agent's system prompt is harness/agents/<agent>.md. Context files are
wrapped in <context file="..."> tags after the brief. Output (raw model text)
is written to --out; path + token usage printed to stdout.

Retries are NOT done here — the LiteLLM proxy handles retries/failover.
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / "harness" / "agents"
PROXY_URL = "http://localhost:4000/v1/chat/completions"
AGENTS = ("backend", "frontend", "qa-db")


def load_env_key() -> str:
    """LITELLM_MASTER_KEY from the environment, falling back to .env."""
    key = os.environ.get("LITELLM_MASTER_KEY")
    if key:
        return key
    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("LITELLM_MASTER_KEY="):
                return line.split("=", 1)[1].strip()
    print("ERROR: LITELLM_MASTER_KEY not set and not found in .env", file=sys.stderr)
    sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True, choices=AGENTS)
    parser.add_argument("--task-file", required=True)
    parser.add_argument(
        "--context-file",
        action="append",
        default=[],
        help="Existing code the agent must conform to (repeatable).",
    )
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    system_prompt = (AGENTS_DIR / f"{args.agent}.md").read_text(encoding="utf-8")
    task_brief = Path(args.task_file).read_text(encoding="utf-8")

    user_parts = [task_brief]
    for cf in args.context_file:
        content = Path(cf).read_text(encoding="utf-8")
        user_parts.append(f'<context file="{cf}">\n{content}\n</context>')
    user_prompt = "\n\n".join(user_parts)

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = Path(args.out) if args.out else REPO_ROOT / "logs" / f"{args.agent}-{timestamp}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "model": "gemini-worker",
        "reasoning_effort": "low",  # maps to Gemini thinking_level: low; API default is HIGH
        "max_tokens": 8000,
        # temperature intentionally unset: Gemini 3 default (1.0) recommended,
        # low temps can cause looping
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        response = httpx.post(
            PROXY_URL,
            json=payload,
            headers={"Authorization": f"Bearer {load_env_key()}"},
            timeout=300.0,
        )
    except httpx.HTTPError as exc:
        print(f"ERROR: request to proxy failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if response.status_code != 200:
        print(f"ERROR: HTTP {response.status_code}\n{response.text}", file=sys.stderr)
        sys.exit(1)

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})

    out_path.write_text(content, encoding="utf-8")
    print(f"output: {out_path}")
    print(
        "tokens: prompt={p} completion={c} total={t}".format(
            p=usage.get("prompt_tokens", "?"),
            c=usage.get("completion_tokens", "?"),
            t=usage.get("total_tokens", "?"),
        )
    )


if __name__ == "__main__":
    main()
