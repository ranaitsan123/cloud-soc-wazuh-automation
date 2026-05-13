#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEFAULT_TECHNIQUE="T1053.005"
DEFAULT_ATOMICS_PATH="/opt/fortress/atomics"
INSTANCE_ID=""
TECHNIQUE="$DEFAULT_TECHNIQUE"
ATOMICS_PATH="$DEFAULT_ATOMICS_PATH"
CUSTOM_COMMAND=""

usage() {
  cat <<HELP
Usage: $0 [options]

Options:
  -i, --instance-id ID        Victim EC2 instance ID (defaults to terraform output)
  -t, --technique TECH        Atomic Red Team technique ID (default: $DEFAULT_TECHNIQUE)
  -p, --path PATH             Path to the atomics folder inside the victim container
  -c, --command COMMAND       Run a custom command instead of Invoke-AtomicTest
  -h, --help                  Show this help message

Examples:
  bash scripts/run-atomic-attack.sh
  bash scripts/run-atomic-attack.sh -t T1059.001
  bash scripts/run-atomic-attack.sh -t T1053.005 -p /opt/fortress/atomics
  bash scripts/run-atomic-attack.sh -i i-0123456789abcdef0
  bash scripts/run-atomic-attack.sh -c 'docker exec victim-art sh -c "echo hello"'
HELP
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -i|--instance-id)
      INSTANCE_ID="$2"
      shift 2
      ;;
    -t|--technique)
      TECHNIQUE="$2"
      shift 2
      ;;
    -p|--path)
      ATOMICS_PATH="$2"
      shift 2
      ;;
    -c|--command)
      CUSTOM_COMMAND="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$INSTANCE_ID" ]]; then
  if ! command -v terraform >/dev/null 2>&1; then
    echo "ERROR: terraform is required to resolve the victim instance ID." >&2
    exit 1
  fi
  INSTANCE_ID=$(cd "$REPO_ROOT/terraform" && terraform output -raw victim_instance_id)
fi

if [[ -z "$INSTANCE_ID" ]]; then
  echo "ERROR: Could not determine victim instance ID." >&2
  exit 1
fi

if [[ -n "$CUSTOM_COMMAND" ]]; then
  ATTACK_CMD="$CUSTOM_COMMAND"
else
  ATTACK_CMD="docker exec victim-art pwsh -NoLogo -NonInteractive -Command \"Invoke-AtomicTest $TECHNIQUE -PathToAtomics $ATOMICS_PATH\""
fi

echo "Running Atomic Red Team attack on victim instance: $INSTANCE_ID"
echo "Command: $ATTACK_CMD"

COMMAND_ID=$(aws ssm send-command \
  --instance-ids "$INSTANCE_ID" \
  --document-name AWS-RunShellScript \
  --comment "Atomic Red Team attack $TECHNIQUE" \
  --parameters '{"commands":["'"$ATTACK_CMD"'" ]}' \
  --query 'Command.CommandId' \
  --output text)

if [[ -z "$COMMAND_ID" ]]; then
  echo "ERROR: Failed to send SSM command." >&2
  exit 1
fi

echo "SSM command sent: $COMMAND_ID"
echo "Waiting for SSM command result..."

while true; do
  STATUS=$(aws ssm list-command-invocations \
    --command-id "$COMMAND_ID" \
    --instance-id "$INSTANCE_ID" \
    --details \
    --query 'CommandInvocations[0].Status' \
    --output text 2>/dev/null || true)

  case "$STATUS" in
    Pending|InProgress|Delayed)
      printf '.'
      sleep 3
      ;;
    Success|Cancelled|TimedOut|Failed|AccessDenied|DeliveryTimedOut)
      echo
      break
      ;;
    *)
      echo
      echo "ERROR: Unexpected command status: $STATUS" >&2
      exit 1
      ;;
  esac
done

echo "Command status: $STATUS"

OUTPUT=$(aws ssm get-command-invocation \
  --command-id "$COMMAND_ID" \
  --instance-id "$INSTANCE_ID" \
  --query '{stdout:StandardOutputContent, stderr:StandardErrorContent}' \
  --output json 2>/dev/null || true)

echo "$OUTPUT" | python3 - <<'PY'
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if data.get('stdout'):
    print('--- STDOUT ---')
    print(data['stdout'])
if data.get('stderr'):
    print('--- STDERR ---')
    print(data['stderr'])
PY

echo "Done. Use the Wazuh Manager UI or agent logs to verify detection." 
