#!/bin/bash
set -e

cd /workspace

if [ ! -d ".venv" ]; then
    uv venv
fi

source .venv/bin/activate

uv pip install -e .

exec "$@"
