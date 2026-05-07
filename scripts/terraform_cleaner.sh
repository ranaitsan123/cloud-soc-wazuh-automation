#!/usr/bin/env bash
set -euo pipefail

# Environment:
TERRAFORM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../terraform" && pwd)"
AWS_REGION="${AWS_REGION:-eu-north-1}"
PROJECT_TAG="${PROJECT_TAG:-cloud-soc}"

echo "Terraform dir: $TERRAFORM_DIR"
echo "AWS region:   $AWS_REGION"
echo "AWS project:  $PROJECT_TAG"
echo "Ensure this is run from your main repo workspace."

# 0) Validate required tools
for cmd in terraform aws jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: $cmd is needed" >&2
    exit 1
  fi
done

cd "$TERRAFORM_DIR"

find_vpc_id() {
  aws ec2 describe-vpcs --region "$AWS_REGION" \
    --filters "Name=tag:Name,Values=wazuh-vpc" "Name=tag:Project,Values=${PROJECT_TAG}" \
    --query 'Vpcs[0].VpcId' --output text 2>/dev/null || true
}

find_security_group_ids() {
  local vpc_id="$1"
  aws ec2 describe-security-groups --region "$AWS_REGION" \
    --filters "Name=vpc-id,Values=$vpc_id" "Name=group-name,Values=wazuh-sg,victim-sg,jail-sg" \
    --query 'SecurityGroups[].GroupId' --output text 2>/dev/null || true
}

terminate_project_instances() {
  local vpc_id="$1"
  local ids
  ids=$(aws ec2 describe-instances --region "$AWS_REGION" \
    --filters "Name=vpc-id,Values=$vpc_id" "Name=tag:Project,Values=${PROJECT_TAG}" \
              "Name=instance-state-name,Values=pending,running,stopping,stopped,shutting-down" \
    --query 'Reservations[].Instances[].InstanceId' --output text 2>/dev/null || true)

  if [[ -z "${ids// /}" ]]; then
    echo "No project instances found in VPC $vpc_id."
    return 0
  fi

  echo "Terminating project instances: $ids"
  aws ec2 terminate-instances --region "$AWS_REGION" --instance-ids $ids || true
}

wait_for_instance_termination() {
  local vpc_id="$1"
  local attempt=0
  while true; do
    local ids
    ids=$(aws ec2 describe-instances --region "$AWS_REGION" \
      --filters "Name=vpc-id,Values=$vpc_id" "Name=tag:Project,Values=${PROJECT_TAG}" \
                "Name=instance-state-name,Values=pending,running,stopping,stopped,shutting-down" \
      --query 'Reservations[].Instances[].InstanceId' --output text 2>/dev/null || true)

    if [[ -z "${ids// /}" ]]; then
      echo "All project instances have terminated."
      return 0
    fi

    attempt=$((attempt + 1))
    if [[ $attempt -ge 20 ]]; then
      echo "WARNING: Instances still remain after waiting: $ids"
      return 1
    fi

    echo "Waiting for instances to terminate: $ids"
    sleep 15
  done
}

cleanup_network_interfaces() {
  local vpc_id="$1"
  local sg_ids
  sg_ids=$(find_security_group_ids "$vpc_id")
  local sg_filter=""
  if [[ -n "${sg_ids// /}" ]]; then
    local sg_ids_csv
    sg_ids_csv=$(echo "$sg_ids" | tr ' ' ',')
    sg_filter="Name=group-id,Values=$sg_ids_csv"
  fi

  local eni_ids
  if [[ -n "$sg_filter" ]]; then
    eni_ids=$(aws ec2 describe-network-interfaces --region "$AWS_REGION" \
      --filters "Name=vpc-id,Values=$vpc_id" "$sg_filter" \
      --query 'NetworkInterfaces[].NetworkInterfaceId' --output text 2>/dev/null || true)
  else
    eni_ids=$(aws ec2 describe-network-interfaces --region "$AWS_REGION" \
      --filters "Name=vpc-id,Values=$vpc_id" \
      --query 'NetworkInterfaces[].NetworkInterfaceId' --output text 2>/dev/null || true)
  fi

  if [[ -z "${eni_ids// /}" ]]; then
    echo "No stale network interfaces found in VPC $vpc_id."
    return 0
  fi

  for eni in $eni_ids; do
    echo "Checking network interface $eni"
    local attachment_id
    attachment_id=$(aws ec2 describe-network-interfaces --region "$AWS_REGION" \
      --network-interface-ids "$eni" \
      --query 'NetworkInterfaces[0].Attachment.AttachmentId' --output text 2>/dev/null || true)

    if [[ -n "$attachment_id" && "$attachment_id" != "None" ]]; then
      echo "Detaching ENI $eni (attachment $attachment_id)"
      aws ec2 detach-network-interface --region "$AWS_REGION" --attachment-id "$attachment_id" --force || true
      aws ec2 wait network-interface-available --region "$AWS_REGION" --network-interface-ids "$eni" || true
    fi

    echo "Deleting ENI $eni"
    aws ec2 delete-network-interface --region "$AWS_REGION" --network-interface-id "$eni" || true
  done
}

cleanup_security_groups() {
  local vpc_id="$1"
  local sg_ids
  sg_ids=$(find_security_group_ids "$vpc_id")
  if [[ -z "${sg_ids// /}" ]]; then
    echo "No matching project security groups found in VPC $vpc_id."
    return 0
  fi

  for sgid in $sg_ids; do
    echo "Deleting security group $sgid"
    aws ec2 delete-security-group --region "$AWS_REGION" --group-id "$sgid" || true
  done
}

cleanup_orphaned_aws_resources() {
  local vpc_id
  vpc_id=$(find_vpc_id)
  if [[ -z "$vpc_id" || "$vpc_id" == "None" ]]; then
    echo "No project VPC found; skipping orphan cleanup."
    return 0
  fi

  terminate_project_instances "$vpc_id"
  wait_for_instance_termination "$vpc_id" || true
  cleanup_network_interfaces "$vpc_id"
  cleanup_security_groups "$vpc_id"
}

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

echo "Applying destroy plan..."
if terraform apply -auto-approve /tmp/tf-destroy.plan; then
  echo "Terraform destroy completed."
else
  echo "Terraform destroy failed. Attempting automated cleanup of AWS dependency blockers..."
  cleanup_orphaned_aws_resources

  echo "Retrying terraform destroy after cleanup..."
  terraform destroy -auto-approve || true
fi

echo "=== AWS orphan cleanup check ==="
cleanup_orphaned_aws_resources

echo "Done cleanup helper."
