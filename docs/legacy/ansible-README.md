# Ansible Deployment Plan

## Overview

This directory documents the new Ansible-based deployment plan for the `feature/art-soc-baseline-ansible` workflow.

The goal is to keep Terraform focused on infrastructure, and move service provisioning and runtime configuration into Ansible executed over AWS SSM.

## What changed

- Terraform now creates the VPC, subnets, NAT gateway, EC2 instances, IAM roles, S3 bucket, and ECR repositories.
- EC2 instances are launched in private subnets with no public IPs.
- Instance bootstrap is limited to installing the AWS SSM agent, Python, Docker, and Ansible dependencies.
- The heavy logic is moved out of EC2 `user_data` and into Ansible playbooks that run after apply.
- SSM is used as the secure control plane for remote execution and port forwarding.

## How it works

### 1. Terraform provisions infrastructure

Terraform deploys:

- `aws_vpc.wazuh_vpc`
- private subnets for the Wazuh Manager and Victim instances
- a NAT gateway for outbound package access
- EC2 instances with IAM instance profiles and `AmazonSSMManagedInstanceCore`
- S3 bucket for Wazuh Docker assets
- ECR repository for the victim container image

### 2. Bootstrap on the instance

The EC2 user data bootstraps each instance with a minimal agent stack:

- `amazon-ssm-agent`
- Python 3 and `pip`
- Docker and Docker Compose
- AWS CLI
- Ansible

This keeps the initial VM image lightweight and avoids embedding business logic in user data.

### 3. Post-apply Ansible configuration

After `cloud-soc apply`, the Python orchestration workflow handles post-apply configuration to:

- wait until each instance is reachable through SSM
- run `ansible-playbook` remotely on the instance via `AWS-RunShellScript`
- apply the `wazuh_manager.yml` playbook to the Wazuh Manager instance
- apply the `victim_server.yml` playbook to the Victim instance

The remote Ansible execution happens inside `/opt/ansible` on the target instance and uses `localhost` as the inventory.

### 4. Role responsibilities

- `ansible/playbooks/wazuh_manager.yml`
  - deploys the Wazuh Manager Docker stack
  - pulls configuration and compose assets from S3
  - starts the Wazuh containers and ensures the manager service is running

- `ansible/playbooks/victim_server.yml`
  - installs Docker and the Wazuh agent
  - configures the agent to register with the Wazuh Manager private IP
  - pulls and starts the victim container image from ECR
  - prepares the attack simulation environment inside the victim container

## Local access and SSM port forwarding

The Wazuh Manager UI is intentionally private inside the VPC.

To access it from your local environment, use SSM port forwarding to map remote HTTPS port `443` to local port `8443`.

### Recommended helper

Use the Python CLI helper:

```bash
cloud-soc dashboard
```

This opens an SSM port-forwarding tunnel to the Wazuh Manager and maps it to `https://127.0.0.1:8443` by default.

Alternative (manual AWS CLI):

```bash
aws ssm start-session --target $(terraform -chdir=terraform output -raw wazuh_instance_id) \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["443"],"localPortNumber":["8443"]}'
```

## Running Atomic Red Team attacks via SSM

The victim image includes the Atomic Red Team assets under `/opt/fortress/atomics` and the PowerShell `Invoke-AtomicRedTeam` module.

This repository's preferred workflow is to run remote actions via Ansible executed over SSM from the Python orchestration layer. Instead of a local helper script, use the orchestrator to run an Ansible task or ad-hoc command on the Victim instance through the `AWS-RunShellScript` document.

Recommended options:

- Use the Python CLI orchestrator to run a dedicated Ansible play or ad-hoc task that executes `pwsh -Command "Invoke-AtomicTest <TECHNIQUE> -PathToAtomics /opt/fortress/atomics"` inside the `victim-art` container.
- Create an Ansible task that uses the `command` or `shell` module and execute the task remotely via the orchestrator's SSM runner.

If you'd like, the orchestrator can be extended to provide a convenience command to trigger Atomic Red Team techniques; open an issue or a PR with your preferred UX.

## Notes

- This plan separates infrastructure from configuration, so Terraform can remain stable while Ansible handles service setup.
- The instance bootstrap is kept minimal to reduce drift and make the deployment easier to maintain.
- SSM provides a secure remote execution channel and avoids the need for SSH access to private instances.
