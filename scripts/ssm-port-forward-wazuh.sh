#!/usr/bin/env bash
set -euo pipefail

# Forward local port 8443 to the Wazuh Manager UI on the target EC2 instance.
# Usage:
#   ./scripts/ssm-port-forward-wazuh.sh [instance-id]
# If no instance ID is provided, the script reads it from Terraform outputs.

WORKSPACE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
INSTANCE_ID="${1:-}"

if [[ -z "$INSTANCE_ID" ]]; then
  if ! command -v terraform >/dev/null 2>&1; then
    echo "ERROR: terraform is required to read the Wazuh instance ID." >&2
    exit 1
  fi

  INSTANCE_ID=$(cd "$WORKSPACE_DIR/terraform" && terraform output -raw wazuh_instance_id)
fi

if [[ -z "$INSTANCE_ID" ]]; then
  echo "ERROR: Wazuh Manager instance ID is not available." >&2
  exit 1
fi

cat <<EOF
Forwarding local https://127.0.0.1:8443 to Wazuh Manager on instance $INSTANCE_ID.
Use Ctrl+C to stop the session.
EOF

aws ssm start-session --target "$INSTANCE_ID" \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters '{"host":["127.0.0.1"],"portNumber":["443"],"localPortNumber":["8443"]}'
