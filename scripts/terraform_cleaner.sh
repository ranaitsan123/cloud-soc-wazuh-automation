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

# Required tools
for cmd in terraform aws jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: $cmd is required" >&2
    exit 1
  fi
done

cd "$TERRAFORM_DIR"

find_vpc_id() {
  aws ec2 describe-vpcs --region "$AWS_REGION" \
    --filters "Name=tag:Name,Values=wazuh-vpc" "Name=tag:Project,Values=${PROJECT_TAG}" \
    --query 'Vpcs[0].VpcId' --output text 2>/dev/null || true
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

cleanup_nat_gateways() {
  local vpc_id="$1"
  local nat_ids

  nat_ids=$(aws ec2 describe-nat-gateways --region "$AWS_REGION" \
    --filters "Name=vpc-id,Values=$vpc_id" \
    --query 'NatGateways[].NatGatewayId' --output text 2>/dev/null || true)

  if [[ -z "${nat_ids// /}" ]]; then
    echo "No NAT gateways found in VPC $vpc_id."
    return 0
  fi

  for nat_id in $nat_ids; do
    echo "Deleting NAT gateway: $nat_id"
    aws ec2 delete-nat-gateway --region "$AWS_REGION" --nat-gateway-id "$nat_id" || true
  done

  echo "Waiting for NAT gateway deletion..."
  sleep 30
}

cleanup_elastic_ips() {
  local eip_ids
  eip_ids=$(aws ec2 describe-addresses --region "$AWS_REGION" \
    --filters "Name=tag:Project,Values=${PROJECT_TAG}" \
    --query 'Addresses[?AssociationId==null].AllocationId' --output text 2>/dev/null || true)

  if [[ -z "${eip_ids// /}" ]]; then
    echo "No unassociated Elastic IPs found."
    return 0
  fi

  for eip_id in $eip_ids; do
    echo "Releasing Elastic IP: $eip_id"
    aws ec2 release-address --region "$AWS_REGION" --allocation-id "$eip_id" || true
  done
}

cleanup_network_interfaces() {
  local vpc_id="$1"
  local eni_ids

  eni_ids=$(aws ec2 describe-network-interfaces --region "$AWS_REGION" \
    --filters "Name=vpc-id,Values=$vpc_id" "Name=status,Values=available" \
    --query 'NetworkInterfaces[].NetworkInterfaceId' --output text 2>/dev/null || true)

  if [[ -z "${eni_ids// /}" ]]; then
    echo "No orphaned ENIs found."
    return 0
  fi

  for eni in $eni_ids; do
    echo "Deleting ENI: $eni"
    aws ec2 delete-network-interface --region "$AWS_REGION" --network-interface-id "$eni" || true
  done
}

cleanup_route_tables() {
  local vpc_id="$1"
  local rt_ids

  rt_ids=$(aws ec2 describe-route-tables --region "$AWS_REGION" \
    --filters "Name=vpc-id,Values=$vpc_id" "Name=tag:Project,Values=${PROJECT_TAG}" \
    --query 'RouteTables[].RouteTableId' --output text 2>/dev/null || true)

  if [[ -z "${rt_ids// /}" ]]; then
    echo "No custom route tables found."
    return 0
  fi

  for rt_id in $rt_ids; do
    local assoc_ids
    assoc_ids=$(aws ec2 describe-route-table-associations --region "$AWS_REGION" \
      --filters "Name=route-table-id,Values=$rt_id" \
      --query 'Associations[?Main==false].RouteTableAssociationId' --output text 2>/dev/null || true)

    for assoc_id in $assoc_ids; do
      echo "Disassociating route table: $assoc_id"
      aws ec2 disassociate-route-table --region "$AWS_REGION" --association-id "$assoc_id" || true
    done

    echo "Deleting route table: $rt_id"
    aws ec2 delete-route-table --region "$AWS_REGION" --route-table-id "$rt_id" || true
  done
}

cleanup_subnets() {
  local vpc_id="$1"
  local subnet_ids

  subnet_ids=$(aws ec2 describe-subnets --region "$AWS_REGION" \
    --filters "Name=vpc-id,Values=$vpc_id" "Name=tag:Project,Values=${PROJECT_TAG}" \
    --query 'Subnets[].SubnetId' --output text 2>/dev/null || true)

  if [[ -z "${subnet_ids// /}" ]]; then
    echo "No project subnets found."
    return 0
  fi

  for subnet_id in $subnet_ids; do
    echo "Deleting subnet: $subnet_id"
    aws ec2 delete-subnet --region "$AWS_REGION" --subnet-id "$subnet_id" || true
  done
}

cleanup_internet_gateways() {
  local vpc_id="$1"
  local igw_ids

  igw_ids=$(aws ec2 describe-internet-gateways --region "$AWS_REGION" \
    --filters "Name=attachment.vpc-id,Values=$vpc_id" \
    --query 'InternetGateways[].InternetGatewayId' --output text 2>/dev/null || true)

  if [[ -z "${igw_ids// /}" ]]; then
    echo "No internet gateways found."
    return 0
  fi

  for igw_id in $igw_ids; do
    echo "Detaching internet gateway: $igw_id"
    aws ec2 detach-internet-gateway --region "$AWS_REGION" --internet-gateway-id "$igw_id" --vpc-id "$vpc_id" || true
    echo "Deleting internet gateway: $igw_id"
    aws ec2 delete-internet-gateway --region "$AWS_REGION" --internet-gateway-id "$igw_id" || true
  done
}

cleanup_vpc() {
  local vpc_id="$1"
  if [[ -z "$vpc_id" ]]; then
    return 0
  fi

  echo "Deleting VPC: $vpc_id"
  aws ec2 delete-vpc --region "$AWS_REGION" --vpc-id "$vpc_id" || true
}

cleanup_security_groups() {
  local vpc_id="$1"
  local sg_ids

  sg_ids=$(aws ec2 describe-security-groups --region "$AWS_REGION" \
    --filters "Name=vpc-id,Values=$vpc_id" "Name=tag:Project,Values=${PROJECT_TAG}" \
    --query 'SecurityGroups[?GroupName!=`default`].GroupId' --output text 2>/dev/null || true)

  if [[ -z "${sg_ids// /}" ]]; then
    echo "No project security groups found."
    return 0
  fi

  for sgid in $sg_ids; do
    echo "Deleting security group: $sgid"
    aws ec2 delete-security-group --region "$AWS_REGION" --group-id "$sgid" || true
  done
}

cleanup_vpc_resources() {
  local vpc_id="$1"

  terminate_project_instances "$vpc_id"
  wait_for_instance_termination "$vpc_id" || true
  cleanup_nat_gateways "$vpc_id"
  cleanup_elastic_ips
  cleanup_network_interfaces "$vpc_id"
  cleanup_security_groups "$vpc_id"
  cleanup_route_tables "$vpc_id"
  cleanup_subnets "$vpc_id"
  cleanup_internet_gateways "$vpc_id"
  cleanup_vpc "$vpc_id"
}

cleanup_orphaned_aws_resources() {
  local vpc_id
  vpc_id=$(find_vpc_id)

  if [[ -z "$vpc_id" || "$vpc_id" == "None" ]]; then
    echo "No project VPC found; skipping orphan cleanup."
    return 0
  fi

  cleanup_vpc_resources "$vpc_id"
}

show_destroy_plan() {
  echo "=== Terraform state list ==="
  terraform state list | tee /tmp/tfstate.list || true

  echo "=== Creating destroy plan ==="
  terraform plan -destroy -out=/tmp/tf-destroy.plan

  echo "=== Destroy plan resources ==="
  terraform show -json /tmp/tf-destroy.plan | jq -r '.resource_changes[] | select(.change.actions | index("delete")) | "- \(.address) \(.type)"' || true
}

main() {
  show_destroy_plan

  read -p "Proceed with terraform destroy (yes/no)? " ans
  if [[ "$ans" != "yes" ]]; then
    echo "Canceled."
    exit 0
  fi

  echo "Applying terraform destroy plan..."
  if terraform apply -auto-approve /tmp/tf-destroy.plan; then
    echo "Terraform destroy completed successfully."
  else
    echo "Terraform destroy failed. Performing cleanup and retrying..."
    cleanup_orphaned_aws_resources
    terraform destroy -auto-approve || true
  fi

  echo "=== AWS orphan cleanup check ==="
  cleanup_orphaned_aws_resources
  echo "Done cleanup helper."
}

main
