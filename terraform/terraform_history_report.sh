#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./terraform_history_report.sh [output.md]
# Default output file: terraform_safe_apply_history_report.md

HISTORY_FILE="terraform_safe_apply_history.json"
OUTPUT_FILE=${1:-terraform_safe_apply_history_report.md}

if [[ ! -f "$HISTORY_FILE" ]]; then
  echo "Error: $HISTORY_FILE not found. Run terraform_safe_apply.sh first."
  exit 1
fi

cat > "$OUTPUT_FILE" <<'EOF'
# Terraform Safe Apply History Report

This report is generated from terraform_safe_apply_history.json.

EOF

# Parse JSON lines and format as markdown
python3 - <<'PY'
import json
from pathlib import Path
file = Path('$HISTORY_FILE')
out = Path('$OUTPUT_FILE')
with file.open() as f:
    entries = [json.loads(line) for line in f if line.strip()]
with out.open('a') as f:
    for e in entries:
        f.write(f"## {e.get('timestamp', '')}\n")
        f.write(f"- action: {e.get('action','')}\n")
        f.write(f"- status: {e.get('status','')}\n")
        f.write(f"- message: {e.get('message','')}\n")
        f.write('\n')
print('Report written to', out)
PY

echo "Done. Report saved to $OUTPUT_FILE"
