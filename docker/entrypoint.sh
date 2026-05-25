#!/bin/bash
set -e

cd /workspace

if [ ! -d ".venv" ]; then
    uv venv
fi

source .venv/bin/activate

uv pip install -e .

# Install Ansible collections
if command -v ansible-galaxy &> /dev/null; then
    ansible-galaxy collection install -r ansible/requirements.yml
fi

exec "$@"
