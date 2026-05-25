# Current Code Issues Report

This report summarizes non-syntactic, logic-level issues found in the current repository code related to Terraform, Python orchestration, and Ansible deployment.

> Update: the latest changes now generate inventory hosts with SSM connection settings for remote EC2 execution and validate remote prerequisites before playbook execution.

## 1. Terraform backend configuration is incomplete

- `terraform/backend.tf` declares:
  ```hcl
  terraform {
    backend "s3" {}
  }
  ```
- That backend block requires runtime values for `bucket`, `key`, and usually `region`.
- `cloudsoc/terraform/runner.py` expects these values to be provided via settings/env vars: `TERRAFORM_BACKEND_BUCKET`, `TERRAFORM_BACKEND_KEY`, and optionally `TERRAFORM_BACKEND_REGION`.
- If those values are not supplied, `terraform init` will fail because the S3 backend is incomplete and `-input=false` is used.

## 2. Ansible playbooks now target remote EC2 hosts through generated SSM inventory

- The orchestrator generates a remote inventory file with EC2 private IPs and group sections for `wazuh` and `victims`.
- The new deployment flow runs `bootstrap.yml` first and then validates remote prerequisites before applying `wazuh_manager.yml` and `victim_server.yml`.
- This means the playbooks are now aligned with the intended remote execution model and no longer rely on `localhost` as the target.

## 3. Victim EC2 instance IAM role lacks ECR/S3 permissions

- Terraform defines `aws_iam_role.victim_ec2_role` and attaches only `AmazonSSMManagedInstanceCore`.
- The `ansible/roles/victim_server/tasks/main.yml` role then attempts to:
  - authenticate to ECR
  - pull a Docker image from ECR
- The victim instance role does not have the required ECR permissions to perform these operations.
- This will likely fail during deployment even if the instance is reachable and SSM is ready.

## 4. Terraform outputs and Ansible variable assumptions are not fully aligned

- The orchestrator uses:
  - `outputs.get("s3_bucket_name")`
  - `outputs.get("s3_prefix")`
  - `outputs.get("wazuh_instance_private_ip")`
  - `outputs.get("ecr_victim_repository_url")`
- Terraform defines `s3_bucket_name`, `wazuh_instance_private_ip`, and `ecr_victim_repository_url`, but it does not define `s3_prefix`.
- The code compensates with a default value of `wazuh-docker`, but this is implicit and fragile.
- If the naming convention ever changes, Ansible will start looking in the wrong S3 path.

## 5. Unused or misleading Terraform resources

- `aws_security_group.jail_sg` is defined in `terraform/security_groups.tf` but never attached to any instance.
- This is not a fatal error, but it is dead configuration and can confuse the infrastructure design.

## 6. Networking and security mismatches

- Both EC2 instances are deployed into private subnets, which is fine for SSM-based management.
- However, the Terraform security groups still expose SSH to `allowed_ssh_cidr` by default (`0.0.0.0/0`).
- Since the instances are in private subnets with no public IPs, that SSH rule is effectively useless and overly broad.

## 7. Additional deployment concerns

- The Wazuh manager and victim user data scripts install `snapd` and `amazon-ssm-agent`, but the Ansible roles assume Docker and AWS CLI are already available and usable on remote hosts.
- If the remote instance bootstrap fails or if the instance is not fully configured, Ansible will not be able to complete.

## Summary of the most critical breaking issues

1. **Terraform backend requires explicit S3 backend configuration** before init/apply.
2. **Ansible orchestration now validates generated inventory and remote prerequisites**, improving deployment safety.
3. **Victim instance role still requires explicit ECR permissions**, and this remains the most likely runtime failure point for victim image pulls.

## Recommended next steps

- Add clear default or documented backend configuration for `terraform/backend.tf`, or switch to a local backend for easy testing.
- Document the generated inventory groups and connection settings for `wazuh` and `victims` so the Ansible workflow is easier to audit.
- Grant the victim instance IAM permissions for ECR pulls, at minimum `ecr:GetAuthorizationToken`, `ecr:BatchGetImage`, `ecr:GetDownloadUrlForLayer`, `ecr:BatchCheckLayerAvailability`.
- Consider whether `s3_prefix` should be an explicit Terraform output to avoid implicit assumptions.
- Remove or reuse the unused `jail_sg` security group if it is not needed.
