#!/bin/bash
set -e

cd /workspace

if [ ! -d ".venv" ]; then
    uv venv
fi

source .venv/bin/activate

uv pip install -e .

# If a GitHub token is provided via environment (GITHUB_TOKEN or GH_TOKEN),
# perform a non-interactive gh authentication so the container can trigger workflows.
if command -v gh >/dev/null 2>&1; then
    if [ -n "$GITHUB_TOKEN" ]; then
        echo "$GITHUB_TOKEN" | gh auth login --with-token >/dev/null 2>&1 || true
    elif [ -n "$GH_TOKEN" ]; then
        echo "$GH_TOKEN" | gh auth login --with-token >/dev/null 2>&1 || true
    fi
fi

# Avoid 'dubious ownership' git error for mounted workspace
git config --global --add safe.directory /workspace 2>/dev/null || true

exec "$@"
