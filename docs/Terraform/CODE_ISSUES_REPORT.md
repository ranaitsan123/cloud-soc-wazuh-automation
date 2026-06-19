# Current Code Issues Report

This report summarizes non-syntactic, logic-level issues found in the current repository code related to Terraform, Python orchestration, and custom YAML-based deployment.

> Update: the latest changes now support a local Terraform backend by default when S3 backend values are not supplied, and the orchestrator now executes deployment plans via SSM remote commands.

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

## 2. Deployment plans require explicit SSM instance targeting

- `deployment/wazuh_manager.yml` and `deployment/victim_server.yml` define tasks that must run on the remote EC2 instances.
- The orchestrator must provide the target EC2 instance IDs to the SSM execution layer.
- If instance targeting is missing or incorrect, the remote deployment will not reach the intended hosts.
- This is a major deployment logic mismatch: the plan is designed for remote SSM execution, but the orchestrator must correctly map Terraform outputs to remote instances.

## 3. Victim EC2 instance IAM role lacks ECR/S3 permissions

- Terraform defines `aws_iam_role.victim_ec2_role` and attaches only `AmazonSSMManagedInstanceCore`.
- The deployment task flow then attempts to:
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

- The Wazuh manager and victim user data scripts install `snapd` and `amazon-ssm-agent`, but the YAML deployment tasks assume Docker and AWS CLI are already available and usable on remote hosts.
- If the remote instance bootstrap fails or if the instance is not fully configured, the SSM execution path will not be able to complete.

## Summary of the most critical breaking issues

1. **Terraform backend requires explicit S3 backend configuration** before init/apply.
2. **Deployment plans require explicit remote instance targeting via SSM**, which is mandatory for correct execution.
3. **Victim instance role lacks ECR access**, preventing the image pull and victim container deployment.

## Recommended next steps

- Add clear default or documented backend configuration for `terraform/backend.tf`, or switch to a local backend for easy testing.
- Verify the orchestrator is using `wazuh_instance_id` and `victim_instance_id` outputs to target SSM command execution.
- Grant the victim instance IAM permissions for ECR pulls, at minimum `ecr:GetAuthorizationToken`, `ecr:BatchGetImage`, `ecr:GetDownloadUrlForLayer`, `ecr:BatchCheckLayerAvailability`.
- Consider whether `s3_prefix` should be an explicit Terraform output to avoid implicit assumptions.
- Remove or reuse the unused `jail_sg` security group if it is not needed.
