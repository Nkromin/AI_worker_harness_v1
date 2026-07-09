#!/usr/bin/env bash
set -a; source .env; set +a
# PYTHONUTF8: LiteLLM's banner crashes on Windows cp1252 consoles without it
export PYTHONUTF8=1
litellm --config harness/litellm_config.yaml --port 4000
