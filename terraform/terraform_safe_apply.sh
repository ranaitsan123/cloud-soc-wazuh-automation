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

########################################
# Import existing resources in AWS if not in Terraform state
########################################

echo_info "Checking and importing possibly existing resources..."

import_if_missing aws_vpc.wazuh_vpc "$(find_vpc_id)"
import_if_missing aws_internet_gateway.igw "$(find_igw_id)"
import_if_missing aws_subnet.public "$(find_subnet_id)"
import_if_missing aws_route_table.public "$(find_route_table_id)"
import_if_missing aws_route_table_association.public "$(find_route_table_association_import_id)"

import_if_missing aws_security_group.jail_sg "$(find_security_group_id jail-sg)"
import_if_missing aws_security_group.victim_sg "$(find_security_group_id victim-sg)"
import_if_missing aws_security_group.wazuh_sg "$(find_security_group_id wazuh-sg)"

import_if_missing aws_instance.wazuh_server "$(find_instance_id_by_name wazuh-server)"
import_if_missing aws_instance.victim_server "$(find_instance_id_by_name victim-server)"

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
  terraform plan -out=tfplan "${EXTRA_ARGS[@]}"
  terraform apply -auto-approve tfplan
  record_history "success" "apply complete"
  exit 0
elif [[ "$ACTION" == "destroy" ]]; then
  terraform destroy "${EXTRA_ARGS[@]}"
  record_history "success" "destroy complete"
  exit 0
else
  echo_warn "Unknown action: $ACTION. Allowed: plan | apply | destroy"
  record_history "error" "invalid action $ACTION"
  exit 2
fi
