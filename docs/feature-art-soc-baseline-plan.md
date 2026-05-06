# Branch 1: feature/art-soc-baseline

## Goal

Establish the internal detection loop between the Victim VM and the Wazuh Manager in VPC A.

This branch is focused on a clean proof-of-concept: the Victim should generate a known persistence event, Wazuh should collect and detect it, and the SOC should surface the alert in the dashboard.

## Scope

- Infrastructure: VPC A only
- Storage: S3 for Wazuh config and `docker-compose.yml`
- Container registry: ECR for the Victim image
- Attack simulation: Atomic Red Team T1053
- Success metric: Level 12 alert for Persistence appears in Wazuh Dashboard

## Phase 1: Local Setup & Asset Preparation

### Task 1.1: Atomics Library Prep

- Download or copy the `atomics/` folder from the Atomic Red Team repository into the Codespace project root.
- Place it under `/workspaces/cloud-soc-wazuh-automation/atomics/`.
- Confirm the folder contains MITRE ATT&CK technique directories and YAML metadata.

### Task 1.2: Dockerfile for Victim

Create a Dockerfile for the Victim instance with these requirements:

- Base image: Ubuntu
- Install PowerShell Core
- Install the `Invoke-AtomicRedTeam` PowerShell module
- Copy the local `atomics/` folder into `/opt/fortress/atomics`
- Configure any runtime dependencies needed for the scheduled task technique

### Task 1.3: Dockerfile for Wazuh Manager

Create or extend a Wazuh Manager Dockerfile with these requirements:

- Base image: official `wazuh/wazuh` manager image
- Install `python3`
- Install `boto3`
- Leave the image ready for Phase 3 response automation

## Phase 2: Infrastructure as Code (Terraform)

### Task 2.1: VPC A Implementation

- Define a single VPC named `vpc-a` or equivalent
- Add two private subnets:
  - Management subnet
  - Production subnet
- Configure routing appropriate for the Wazuh Manager and Victim instances

### Task 2.2: S3 Asset Deployment

- Deploy an S3 bucket for SOC assets
- Store the following in S3:
  - `docker-compose.yml`
  - Wazuh Manager config files
  - Any helper scripts needed for container startup

### Task 2.3: EC2 Configuration

- **Manager Instance**:
  - Use `user_data` to download files from S3
  - Start the custom Wazuh Manager image from ECR or local build
- **Victim Instance**:
  - Configure to pull the custom ART-ready Victim image from ECR
  - Ensure the Instance profile has access to SSM and ECR

### Task 2.4: IAM Roles

- Create IAM instance profiles for both EC2 instances
- Attach `AmazonSSMManagedInstanceCore` to both profiles
- Optionally attach minimal policies for S3/ECR access if pulling assets directly

## Phase 3: The Manual Validation Loop

### Task 3.1: Dashboard Verification

- Access the Wazuh Dashboard on port `443`
- Confirm the Victim Agent is appearing as `Active`
- Verify the Wazuh Manager is collecting logs from the Victim

### Task 3.2: Trigger the First Attack (ART)

From the Codespace terminal, execute the SSM command below, replacing `VICTIM_ID` with the EC2 instance ID:

```bash
aws ssm send-command \
  --instance-ids "VICTIM_ID" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["pwsh -Command \"Invoke-AtomicTest T1053.005 -PathToAtomics /opt/fortress/atomics\""]'
```

### Task 3.3: Log Analysis

- Confirm the scheduled task creation appears in Wazuh security events
- Validate that the detection corresponds to `Persistence` and `T1053`
- Record the alert details and timestamp for later reporting

## Phase 4: Baseline Clean-up

### Task 4.1: Documentation

- Document the successful detection in your project notes or thesis tracker
- Capture screenshots of the Wazuh alert and active agent state

### Task 4.2: Snapshot

- Commit the Terraform code and Dockerfiles to the `feature/art-soc-baseline` branch
- Keep the branch focused on internal SOC detection before merging external attack logic

## Success Criteria

- The Victim instance is deployed in VPC A
- The Wazuh Manager is running and receiving logs
- The Victim Agent is active in the Wazuh Dashboard
- `Invoke-AtomicTest T1053.005` creates a persistence event
- Wazuh generates a Level 12 Persistence alert

## Notes

- This branch is intentionally narrow: no Caldera, no cross-VPC traffic, no automatic response yet.
- The goal is to establish a reliable internal detection pipeline before adding attacker infrastructure.
- Keep the Dockerfiles and Terraform changes minimal and auditable for the next branch.
