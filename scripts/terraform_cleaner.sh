#!/usr/bin/env bash
set -euo pipefail

# Environment:
TERRAFORM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../terraform" && pwd)"
AWS_REGION="${AWS_REGION:-eu-north-1}"

echo "Terraform dir: $TERRAFORM_DIR"
echo "AWS region:   $AWS_REGION"
echo "Ensure this is run from your main repo workspace."

# 0) Validate required tools
for cmd in terraform aws jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: $cmd is needed" >&2
    exit 1
  fi
done

cd "$TERRAFORM_DIR"

# 1) state info
echo "=== Terraform state list ==="
if terraform state list | tee /tmp/tfstate.list; then
  echo "State entries written to /tmp/tfstate.list"
else
  echo "No state file or empty yet."
fi

# 2) force destroy plan
echo "=== Creating destroy plan ==="
terraform plan -destroy -out=/tmp/tf-destroy.plan
terraform show -json /tmp/tf-destroy.plan > /tmp/tf-destroy.json

cat /tmp/tf-destroy.json | jq -r '.planned_values.root_module.resources[] | "\(.address) \(.type) \(.name)"' | tee /tmp/tf-destroy-resources.txt

echo "Destroy plan resources (preview):"
cat /tmp/tf-destroy-resources.txt

# 3) apply destroy plan
read -p "Proceed with terraform destroy (yes/no)? " ans
if [[ "$ans" != "yes" ]]; then
  echo "Canceled."
  exit 0
fi

terraform apply -auto-approve /tmp/tf-destroy.plan
echo "Terraform destroy completed."

# 4) Cleanup potential orphan resources via AWS CLI
echo "=== AWS orphan cleanup check ==="

sleep 1
echo "Instances (wazuh / victim) in region $AWS_REGION"
aws ec2 describe-instances --region "$AWS_REGION" \
  --filters "Name=tag:Name,Values=wazuh-server,victim-server" |
  jq -r '.Reservations[].Instances[].InstanceId' | tee /tmp/aws-instance-ids.txt

if [ -s /tmp/aws-instance-ids.txt ]; then
  echo "Terminating these instances..."
  aws ec2 terminate-instances --region "$AWS_REGION" --instance-ids $(cat /tmp/aws-instance-ids.txt)
  echo "terminate-instances sent"
else
  echo "No matching instances found."
fi

echo "Look for leftover security groups (wazuh-sg, victim-sg, jail-sg standbys)"
aws ec2 describe-security-groups --region "$AWS_REGION" \
  --filters "Name=group-name,Values=wazuh-sg,victim-sg,jail-sg" |
  jq -r '.SecurityGroups[].GroupId' | tee /tmp/aws-sg-ids.txt

if [ -s /tmp/aws-sg-ids.txt ]; then
  while read -r sgid; do
    echo "Deleting SG $sgid"
    aws ec2 delete-security-group --region "$AWS_REGION" --group-id "$sgid" || true
  done < /tmp/aws-sg-ids.txt
fi

echo "Done cleanup helper."
