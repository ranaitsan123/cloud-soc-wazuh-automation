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

Use the helper script:

```bash
bash scripts/ssm-port-forward-wazuh.sh
```

Then open:

```text
https://127.0.0.1:8443
```

## Running Atomic Red Team attacks via SSM

A helper script is available in `scripts/run-atomic-attack.sh`.

### What it does

- resolves the victim EC2 instance ID from Terraform outputs
- sends an SSM `AWS-RunShellScript` command to the victim instance
- executes `docker exec victim-art pwsh -NoLogo -NonInteractive -Command "Invoke-AtomicTest ..."`
- waits for the SSM command to complete and prints stdout/stderr

### Run an attack

From the repository root:

```bash
bash scripts/run-atomic-attack.sh
```

This runs the default technique:

```bash
Invoke-AtomicTest T1053.005 -PathToAtomics /opt/fortress/atomics
```

### Customize the attack

Run a different technique:

```bash
bash scripts/run-atomic-attack.sh -t T1059.001
```

Use a custom path to the atomics folder:

```bash
bash scripts/run-atomic-attack.sh -p /opt/fortress/atomics
```

Send a custom shell command directly:

```bash
bash scripts/run-atomic-attack.sh -c 'docker exec victim-art sh -c "echo hello"'
```

If the script completes, the attack command was delivered via SSM and you can verify detection in Wazuh.

## Notes

- This plan separates infrastructure from configuration, so Terraform can remain stable while Ansible handles service setup.
- The instance bootstrap is kept minimal to reduce drift and make the deployment easier to maintain.
- SSM provides a secure remote execution channel and avoids the need for SSH access to private instances.
