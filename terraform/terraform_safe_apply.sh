#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./terraform_safe_apply.sh [plan|apply|destroy] [--auto-approve]
# Default action is apply.

cd "$(dirname "$0")"

ACTION=${1:-apply}
shift 1 || true
EXTRA_ARGS=("$@")

## Load .env if exists
if [[ -f .env ]]; then
  # shellcheck disable=SC1090
  source .env
fi

terraform init -input=false

# Shared tags used by this project
NAME_TAG="cloud-soc"
PROJECT_TAG="cloud-soc"
COMMON_TAG_FILTER="Name=tag:Project,Values=${PROJECT_TAG}"
HISTORY_FILE="terraform_safe_apply_history.json"

# Resource names (match terraform vars in s3.tf, ecr.tf)
S3_BUCKET_NAME="${S3_BUCKET_NAME:-cloud-soc-wazuh-assets}"
ECR_REPOSITORY_NAME="${ECR_REPOSITORY_NAME:-cloud-soc-wazuh-repo}"

########################################
# Helpers
########################################

echo_info() { echo -e "[INFO] $*"; }
echo_warn() { echo -e "[WARN] $*"; }

record_history() {
  local status="$1"
  local message="${2:-}" 
  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  # escape JSON special chars in message
  local escmsg
  escmsg=$(printf '%s' "$message" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')
  echo "{\"timestamp\": \"$timestamp\", \"action\": \"$ACTION\", \"status\": \"$status\", \"message\": $escmsg}" >> "$HISTORY_FILE"
}

trap 'record_history "error" "terraform_safe_apply.sh failed"' ERR
record_history "started" "terraform_safe_apply.sh started"

stack_has() {
  local resource=$1
  terraform state list | grep -q "^${resource}$"
}

import_if_missing() {
  local terraform_addr=$1
  local aws_id=$2
  if stack_has "$terraform_addr"; then
    echo_info "$terraform_addr already in state, skipping import"
    return
  fi
  if [[ -z "$aws_id" || "$aws_id" == "None" ]]; then
    echo_warn "No existing AWS resource ID for $terraform_addr; terraform will create it"
    return
  fi
  echo_info "Importing $terraform_addr: $aws_id"
  terraform import "$terraform_addr" "$aws_id"
}

# Query helpers for resources, matching by Name tags used in resources defined.
find_vpc_id() {
  aws ec2 describe-vpcs --filters Name=tag:Name,Values=wazuh-vpc Name=tag:Project,Values=${PROJECT_TAG} --query 'Vpcs[0].VpcId' --output text 2>/dev/null || true
}

find_subnet_id() {
  aws ec2 describe-subnets --filters Name=tag:Name,Values=wazuh-public-subnet Name=tag:Project,Values=${PROJECT_TAG} --query 'Subnets[0].SubnetId' --output text 2>/dev/null || true
}

find_igw_id() {
  local vpc_id
  vpc_id=$(find_vpc_id)
  [[ -z "$vpc_id" ]] && return 0
  aws ec2 describe-internet-gateways --filters Name=attachment.vpc-id,Values=$vpc_id Name=tag:Name,Values=wazuh-igw --query 'InternetGateways[0].InternetGatewayId' --output text 2>/dev/null || true
}

find_route_table_id() {
  local vpc_id
  vpc_id=$(find_vpc_id)
  [[ -z "$vpc_id" ]] && return 0
  aws ec2 describe-route-tables --filters Name=vpc-id,Values=$vpc_id Name=tag:Name,Values=wazuh-public-rt --query 'RouteTables[0].RouteTableId' --output text 2>/dev/null || true
}

find_route_table_association_id() {
  local rt_id subnet_id
  rt_id=$(find_route_table_id)
  subnet_id=$(find_subnet_id)
  [[ -z "$rt_id" || -z "$subnet_id" ]] && return 0
  aws ec2 describe-route-tables --route-table-ids "$rt_id" --query "RouteTables[0].Associations[?SubnetId=='$subnet_id'].RouteTableAssociationId | [0]" --output text 2>/dev/null || true
}

find_route_table_association_import_id() {
  local rt_id subnet_id
  rt_id=$(find_route_table_id)
  subnet_id=$(find_subnet_id)
  [[ -z "$rt_id" || -z "$subnet_id" ]] && return 0
  echo "$subnet_id/$rt_id"
}

find_security_group_id() {
  local name=$1
  # First try to find security groups in the current VPC (if VPC is already imported)
  if stack_has aws_vpc.wazuh_vpc; then
    local vpc_id
    vpc_id=$(terraform output -raw vpc_id 2>/dev/null || echo "")
    if [[ -n "$vpc_id" ]]; then
      aws ec2 describe-security-groups --filters Name=vpc-id,Values=$vpc_id Name=group-name,Values=$name --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || true
      return
    fi
  fi
  # Fallback: find by name and project tag
  aws ec2 describe-security-groups --filters Name=group-name,Values=$name Name=tag:Project,Values=${PROJECT_TAG} --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || true
}

find_instance_id_by_name() {
  local name=$1
  aws ec2 describe-instances --filters Name=tag:Name,Values=$name Name=instance-state-name,Values=running,stopped,pending,stopping --query 'Reservations[0].Instances[0].InstanceId' --output text 2>/dev/null || true
}

find_iam_role_arn() {
  local role_name="wazuh-ec2-role"
  aws iam get-role --role-name "$role_name" --query 'Role.Arn' --output text 2>/dev/null || true
}

find_iam_policy_arn() {
  local policy_name="wazuh-ec2-policy"
  aws iam list-policies --scope Local --query "Policies[?PolicyName=='$policy_name'].Arn | [0]" --output text 2>/dev/null || true
}

find_s3_bucket_name() {
  echo "$S3_BUCKET_NAME"
}

find_ecr_repository_name() {
  echo "$ECR_REPOSITORY_NAME"
}

find_instance_profile_name() {
  local instance_profile_name="wazuh-instance-profile"
  if aws iam get-instance-profile --instance-profile-name "$instance_profile_name" >/dev/null 2>&1; then
    echo "$instance_profile_name"
  fi
}

find_role_policy_attachment_id() {
  local role_name="wazuh-ec2-role"
  local policy_arn
  policy_arn=$(find_iam_policy_arn)
  [[ -z "$policy_arn" ]] && return 0
  aws iam list-attached-role-policies --role-name "$role_name" --query "AttachedPolicies[?PolicyArn=='$policy_arn'].PolicyArn | [0]" --output text 2>/dev/null || true
}

check_and_handle_vpc_limits() {
  # Check current VPC count
  local vpc_count
  vpc_count=$(aws ec2 describe-vpcs --query 'length(Vpcs[?IsDefault==`false`])' --output text 2>/dev/null || echo "0")

  # AWS default limit is 5 VPCs per region
  local vpc_limit=5

  if [[ "$vpc_count" -ge "$vpc_limit" ]]; then
    echo_warn "VPC limit reached ($vpc_count/$vpc_limit). Attempting to reuse existing VPC..."

    # Find an existing VPC that matches our project tags
    local existing_vpc_id
    existing_vpc_id=$(aws ec2 describe-vpcs \
      --filters "Name=tag:Project,Values=${PROJECT_TAG}" "Name=tag:Name,Values=wazuh-vpc" \
      --query 'Vpcs[0].VpcId' --output text 2>/dev/null || true)

    if [[ -n "$existing_vpc_id" && "$existing_vpc_id" != "None" ]]; then
      echo_info "Found existing VPC: $existing_vpc_id"

      # Check if VPC is already in Terraform state
      if stack_has aws_vpc.wazuh_vpc; then
        echo_info "VPC already in Terraform state, proceeding..."
        return 0
      fi

      # Import the existing VPC
      echo_info "Importing existing VPC..."
      terraform import aws_vpc.wazuh_vpc "$existing_vpc_id" || {
        echo_warn "Failed to import VPC, will try to clean up orphaned VPCs..."
        cleanup_orphaned_vpcs
      }
    else
      echo_warn "No suitable existing VPC found, attempting to clean up orphaned VPCs..."
      cleanup_orphaned_vpcs
    fi
  fi
}

check_and_resolve_security_group_conflicts() {
  # Check if VPC is imported and get its ID
  if stack_has aws_vpc.wazuh_vpc; then
    local vpc_id
    vpc_id=$(terraform output -raw vpc_id 2>/dev/null || echo "")
    if [[ -n "$vpc_id" ]]; then
      echo_info "Checking for security group conflicts in VPC: $vpc_id"

      # Check each security group
      local sg_names=("jail-sg" "victim-sg" "wazuh-sg")
      local conflicts_found=false

      for sg_name in "${sg_names[@]}"; do
        # Check if security group exists in the target VPC
        local existing_sg_id
        existing_sg_id=$(aws ec2 describe-security-groups \
          --filters "Name=vpc-id,Values=$vpc_id" "Name=group-name,Values=$sg_name" \
          --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo "None")

        if [[ "$existing_sg_id" != "None" && -n "$existing_sg_id" ]]; then
          echo_info "Found existing security group $sg_name ($existing_sg_id) in target VPC"

          # Check if it's already in Terraform state
          local tf_resource="aws_security_group.${sg_name%'-sg'}_sg"
          if stack_has "$tf_resource"; then
            # Get current security group VPC
            local current_vpc
            current_vpc=$(aws ec2 describe-security-groups \
              --group-ids "$existing_sg_id" \
              --query 'SecurityGroups[0].VpcId' --output text 2>/dev/null || echo "")

            if [[ "$current_vpc" != "$vpc_id" ]]; then
              echo_warn "Security group $sg_name is in different VPC ($current_vpc vs $vpc_id). Removing from state..."
              terraform state rm "$tf_resource"
              conflicts_found=true
            fi
          else
            # Import the existing security group
            echo_info "Importing existing security group $sg_name..."
            import_if_missing "$tf_resource" "$existing_sg_id"
          fi
        fi
      done

      if [[ "$conflicts_found" == "true" ]]; then
        echo_info "Security group conflicts resolved. Re-running plan..."
        return 1  # Signal that we need to re-run the plan
      fi
    fi
  fi
  return 0
}

cleanup_orphaned_vpcs() {
  echo_info "Looking for orphaned VPCs to clean up..."

  # Find VPCs with our project tag but no associated resources
  local orphaned_vpcs
  orphaned_vpcs=$(aws ec2 describe-vpcs \
    --filters "Name=tag:Project,Values=${PROJECT_TAG}" \
    --query 'Vpcs[?length(Associations)==`0`].VpcId' --output text 2>/dev/null || true)

  for vpc_id in $orphaned_vpcs; do
    if [[ "$vpc_id" != "None" && -n "$vpc_id" ]]; then
      echo_info "Attempting to delete orphaned VPC: $vpc_id"

      # Check if VPC has any dependencies
      local subnet_count igw_count sg_count
      subnet_count=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$vpc_id" --query 'length(Subnets)' --output text 2>/dev/null || echo "0")
      igw_count=$(aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$vpc_id" --query 'length(InternetGateways)' --output text 2>/dev/null || echo "0")
      sg_count=$(aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$vpc_id" "Name=group-name,Values=[\"default\"]" --query 'length(SecurityGroups)' --output text 2>/dev/null || echo "1")

      if [[ "$subnet_count" == "0" && "$igw_count" == "0" && "$sg_count" == "1" ]]; then
        # VPC appears to be empty (only default security group)
        echo_info "Deleting empty VPC: $vpc_id"
        aws ec2 delete-vpc --vpc-id "$vpc_id" 2>/dev/null && echo_info "Successfully deleted VPC: $vpc_id" || echo_warn "Failed to delete VPC: $vpc_id"
      else
        echo_warn "VPC $vpc_id has dependencies (subnets: $subnet_count, IGWs: $igw_count), skipping..."
      fi
    fi
  done

  # If still no space, try to request limit increase
  local vpc_count_after_cleanup
  vpc_count_after_cleanup=$(aws ec2 describe-vpcs --query 'length(Vpcs[?IsDefault==`false`])' --output text 2>/dev/null || echo "0")

  if [[ "$vpc_count_after_cleanup" -ge "5" ]]; then
    echo_warn "Still at VPC limit after cleanup. Attempting to request limit increase..."
    request_vpc_limit_increase
  fi
}

request_vpc_limit_increase() {
  echo_warn "VPC limit reached. Requesting an increase to 10 VPCs may incur additional costs."
  echo_warn "This request may require manual approval from AWS."

  # Prompt user for confirmation
  read -p "Do you want to request a VPC limit increase to 10? (y/N): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo_info "VPC limit increase request cancelled by user."
    return 1
  fi

  echo_info "Requesting VPC limit increase to 10..."

  # Try to request a limit increase (this may not work for all accounts)
  if aws service-quotas request-service-quota-increase \
    --service-code vpc \
    --quota-code L-F678F1CE \
    --desired-value 10 \
    --region "$AWS_DEFAULT_REGION" 2>/dev/null; then
    echo_info "✅ VPC limit increase request submitted successfully."
    echo_info "📋 Check AWS Service Quotas console for approval status."
    echo_info "⏱️  This may take some time to be approved."
  else
    echo_warn "❌ Failed to request VPC limit increase automatically."
    echo_warn "💡 Please request it manually in the AWS Service Quotas console:"
    echo_warn "   https://console.aws.amazon.com/servicequotas/"
    return 1
  fi
}

handle_destroy_with_s3_protection() {
  echo ""
  echo "============================================"
  echo "S3 Bucket Protection"
  echo "============================================"
  echo ""
  echo "The S3 bucket 'cloud-soc-wazuh-assets' has lifecycle.prevent_destroy enabled."
  echo ""
  echo "Choose what to destroy:"
  echo "  1) Everything EXCEPT the S3 bucket (recommended)"
  echo "  2) Everything INCLUDING the S3 bucket"
  echo "  3) Cancel destroy"
  echo ""
  read -p "Enter your choice (1-3): " -r choice

  case "$choice" in
    1)
      echo_info "Destroying all resources except S3 bucket..."
      terraform destroy \
        -target=aws_instance.wazuh_server \
        -target=aws_instance.victim_server \
        -target=aws_security_group.wazuh_sg \
        -target=aws_security_group.victim_sg \
        -target=aws_security_group.jail_sg \
        -target=aws_route_table_association.public \
        -target=aws_route_table.public \
        -target=aws_internet_gateway.igw \
        -target=aws_subnet.public \
        -target=aws_vpc.wazuh_vpc \
        -target=aws_iam_instance_profile.wazuh_instance_profile \
        -target=aws_iam_role_policy_attachment.attach_wazuh_policy \
        -target=aws_iam_role.wazuh_ec2_role \
        "${EXTRA_ARGS[@]}"
      record_history "success" "destroy complete (S3 preserved)"
      echo_info "✅ Destroy complete. S3 bucket 'cloud-soc-wazuh-assets' was preserved."
      ;;
    2)
      echo_warn "⚠️  You selected to destroy EVERYTHING including the S3 bucket."
      echo_warn "⚠️  This will delete all Wazuh Docker assets stored in S3."
      read -p "Are you SURE? Type 'yes' to confirm: " -r confirm
      if [[ "$confirm" == "yes" ]]; then
        echo_info "Removing prevent_destroy protection from S3 bucket..."
        sed -i.bak 's/prevent_destroy = true/prevent_destroy = false/' s3.tf
        echo_info "Destroying all resources including S3 bucket..."
        terraform destroy "${EXTRA_ARGS[@]}"
        record_history "success" "destroy complete (S3 destroyed)"
        echo_info "✅ Destroy complete. All resources including S3 bucket have been removed."
        echo_info "💾 Backup created: s3.tf.bak"
        echo_info "⚠️  Remember to restore prevent_destroy = true if you plan to rebuild."
      else
        echo_info "Destroy cancelled."
        record_history "cancelled" "user cancelled full destroy"
      fi
      ;;
    3)
      echo_info "Destroy cancelled."
      record_history "cancelled" "user cancelled destroy operation"
      exit 0
      ;;
    *)
      echo_warn "Invalid choice. Aborting destroy."
      record_history "error" "invalid destroy choice"
      exit 1
      ;;
  esac
}

########################################
# Import existing resources in AWS if not in Terraform state
########################################

echo_info "Checking and importing possibly existing resources..."

# Handle VPC limits before attempting to create/import VPC
check_and_handle_vpc_limits

import_if_missing aws_vpc.wazuh_vpc "$(find_vpc_id)"
import_if_missing aws_internet_gateway.igw "$(find_igw_id)"
import_if_missing aws_subnet.public "$(find_subnet_id)"
import_if_missing aws_route_table.public "$(find_route_table_id)"
import_if_missing aws_route_table_association.public "$(find_route_table_association_import_id)"

# Check for security group conflicts before importing them
check_and_resolve_security_group_conflicts

import_if_missing aws_security_group.jail_sg "$(find_security_group_id jail-sg)"
import_if_missing aws_security_group.victim_sg "$(find_security_group_id victim-sg)"
import_if_missing aws_security_group.wazuh_sg "$(find_security_group_id wazuh-sg)"

import_if_missing aws_instance.wazuh_server "$(find_instance_id_by_name wazuh-server)"
import_if_missing aws_instance.victim_server "$(find_instance_id_by_name victim-server)"

import_if_missing aws_s3_bucket.wazuh_assets "$(find_s3_bucket_name)"
# ECR import commented out - ECR resources are disabled for now
# import_if_missing aws_ecr_repository.wazuh_repo "$(find_ecr_repository_name)"

import_if_missing aws_iam_role.wazuh_ec2_role "$(find_iam_role_arn | awk -F'/' '{print $NF}')"
import_if_missing aws_iam_policy.wazuh_ec2_policy "$(find_iam_policy_arn)"
import_if_missing aws_iam_instance_profile.wazuh_instance_profile "$(find_instance_profile_name)"

# Import role-policy attachment only if not in state and exists in AWS
if ! stack_has aws_iam_role_policy_attachment.attach_wazuh_policy; then
  attachment_policy_arn=$(find_iam_policy_arn)
  if [[ -n "$attachment_policy_arn" && -n "$(find_iam_role_arn)" ]]; then
    echo_info "Attempting to import IAM role policy attachment"
    terraform import aws_iam_role_policy_attachment.attach_wazuh_policy "wazuh-ec2-role/$attachment_policy_arn" || echo_warn "Attachment not present; plan/apply will create if needed"
  fi
fi

########################################
# Plan/apply/destroy
########################################

if [[ "$ACTION" == "plan" ]]; then
  terraform plan -out=tfplan "${EXTRA_ARGS[@]}"
  record_history "success" "plan complete"
  exit 0
elif [[ "$ACTION" == "apply" ]]; then
  # Check for security group conflicts before planning
  if check_and_resolve_security_group_conflicts; then
    echo_info "No security group conflicts detected, proceeding..."
  else
    echo_info "Security group conflicts resolved, re-planning..."
  fi

  terraform plan -out=tfplan "${EXTRA_ARGS[@]}"

  # Attempt apply with error handling for VPC limits
  if terraform apply -auto-approve tfplan 2>&1; then
    record_history "success" "apply complete"
    exit 0
  else
    apply_exit_code=$?
    apply_output=$(terraform apply -auto-approve tfplan 2>&1 || true)

    # Check if the error is VPC limit exceeded
    if echo "$apply_output" | grep -q "VpcLimitExceeded"; then
      echo_warn "VPC limit exceeded during apply. Attempting automatic cleanup and retry..."

      # Clean up orphaned VPCs
      cleanup_orphaned_vpcs

      # Re-run the import process
      echo_info "Re-running import process after cleanup..."
      check_and_handle_vpc_limits
      import_if_missing aws_vpc.wazuh_vpc "$(find_vpc_id)"

      # Retry apply
      echo_info "Retrying terraform apply..."
      if terraform apply -auto-approve tfplan; then
        record_history "success" "apply complete (after VPC cleanup)"
        exit 0
      else
        record_history "error" "apply failed even after VPC cleanup"
        exit $apply_exit_code
      fi
    else
      # Not a VPC limit error, just record the failure
      record_history "error" "apply failed: $apply_output"
      exit $apply_exit_code
    fi
  fi
elif [[ "$ACTION" == "destroy" ]]; then
  handle_destroy_with_s3_protection
  exit 0
else
  echo_warn "Unknown action: $ACTION. Allowed: plan | apply | destroy"
  record_history "error" "invalid action $ACTION"
  exit 2
fi
