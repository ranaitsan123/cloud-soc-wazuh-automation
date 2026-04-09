# Cloud SOC Wazuh Automation - Terraform Infrastructure

This repository contains the Terraform configuration for deploying a Cloud Security Operations Center (SOC) using Wazuh, integrated with AWS services like S3 and ECR for secure, versioned asset management and containerized deployments.

## Overview

The infrastructure includes:
- **VPC and Networking**: Isolated VPC with public subnets, internet gateway, and route tables. The deployment script automatically handles VPC limits by reusing existing VPCs or cleaning up orphaned ones.
- **Security Groups**: Separate groups for Wazuh server, victim VM, and jail (isolation) security group.
- **EC2 Instances**: Wazuh server and victim server with IAM roles for automation.
- **S3 Bucket**: Versioned storage for SOC assets (e.g., Docker Compose files, scripts).
- **ECR Repository**: Container registry with lifecycle policies for image management.
- **IAM Policies**: Permissions for EC2 instances to interact with S3, ECR, and EC2 services.

## Features

- **State-Aware Safe Apply**: The `terraform_safe_apply.sh` script automatically discovers and imports existing AWS resources to prevent duplicate creations, enabling safe redeployments even after Codespace timeouts.
- **VPC Limit Management**: Automatically handles AWS VPC limits by reusing existing VPCs, cleaning up orphaned resources, and prompting for limit increases when needed.
- **Security Group Conflict Resolution**: Automatically detects and resolves security group conflicts when importing VPCs from different environments.
- **Versioning Support**:
  - S3 bucket with versioning enabled for rollback of configurations.
  - ECR repository with lifecycle policy to retain the last 3 images, ensuring cost-effective version management.
- **Secure by Design**: All resources are encrypted, public access is blocked, and IAM roles follow least-privilege principles.
- **Modular Configuration**: Infrastructure is split into specialized files (vpc.tf, iam.tf, s3.tf, ecr.tf, etc.) for maintainability.
- **Automation Ready**: EC2 instances have permissions to pull from S3 and ECR, supporting automated deployments and response scripts.

## Prerequisites

- AWS CLI configured with appropriate credentials.
- Terraform v1.0+ installed.
- Bash environment (e.g., GitHub Codespaces).
- Optional: `.env` file for environment variables (e.g., custom bucket/repo names).

## Usage

### Initial Setup

1. Navigate to the `terraform/` directory:
   ```bash
   cd terraform
   ```

2. Initialize Terraform:
   ```bash
   terraform init -input=false
   ```

3. (Optional) Load environment variables from `.env`:
   ```bash
   source .env
   ```

### Safe Apply Script

Use the provided `terraform_safe_apply.sh` script for state-aware deployments:

- **Plan**: `./terraform_safe_apply.sh plan`
- **Apply**: `./terraform_safe_apply.sh apply` (default action)
- **Destroy**: `./terraform_safe_apply.sh destroy`

The script:
- Imports existing resources if they exist in AWS but not in Terraform state.
- Records deployment history in `terraform_safe_apply_history.json`.
- Supports custom arguments via `--auto-approve` or other Terraform flags.
- **Automatically handles AWS VPC limits** by reusing existing VPCs or cleaning up orphaned ones.
- **Prompts for confirmation** before requesting VPC limit increases to avoid unexpected costs.
- **Retries failed deployments** due to VPC limits after automatic cleanup.

#### VPC Limit Management
When VPC limits are reached (default: 5 VPCs per region), the script:
1. **Reuses existing VPCs** with matching project tags (`Project=cloud-soc`)
2. **Cleans up orphaned VPCs** that have no dependencies (subnets, IGWs, custom security groups)
3. **Prompts for limit increase** if cleanup is insufficient
4. **Resolves security group conflicts** automatically by importing existing groups or removing conflicting ones
5. **Retries deployment** after successful cleanup

#### Security Group Conflict Resolution
The script automatically handles security group conflicts that can occur when importing VPCs:
- **Detects existing security groups** in imported VPCs
- **Imports compatible groups** instead of creating duplicates
- **Removes conflicting groups** from state when VPC changes
- **Prevents deployment failures** due to duplicate names

#### S3 Bucket Protection During Destroy
The script provides safe destruction options for the S3 bucket containing Wazuh assets:
- **Preserves S3 by default**: Option to destroy all resources except the S3 bucket
- **Full destruction with protection**: When destroying the S3 bucket, temporarily disables `prevent_destroy`, empties the bucket, destroys all resources, then **automatically restores** `prevent_destroy = true` for future safety
- **No manual restoration needed**: The script handles protection restoration automatically after successful destruction

Example:
```bash
./terraform_safe_apply.sh destroy
# Prompts for S3 destruction choice, then proceeds safely
```

### Script Workflow Diagram

The following diagram illustrates the complete workflow of the `terraform_safe_apply.sh` script, including all resource types and S3 bucket protection during destroy operations:

```mermaid
graph TD
    A["Start: terraform_safe_apply.sh"] --> B["Initialize Terraform"]
    B --> C["Load .env variables"]
    C --> D{"ACTION Type?"}
    
    D -->|plan/apply| E["Check VPC Limits"]
    D -->|destroy| DEST1["Prompt for S3<br/>destruction choice"]
    D -->|other| G["Error: Unknown action"]
    
    DEST1 --> DEST2{"Choice?"}
    DEST2 -->|1: Keep S3| DEST3["Destroy all<br/>except S3"]
    DEST2 -->|2: Destroy S3| DEST5["Temporarily disable<br/>prevent_destroy"]
    DEST2 -->|3: Cancel| DEST10["Record cancelled"]
    DEST2 -->|Invalid| DEST11["Error: invalid choice"]
    
    DEST3 --> DEST4["Record destroy<br/>(S3 preserved)"]
    DEST4 --> AA
    
    DEST5 --> DEST6["Empty S3 bucket"]
    DEST6 --> DEST7["Destroy all resources"]
    DEST7 --> DEST8["Restore prevent_destroy"]
    DEST8 --> DEST9["Record destroy<br/>(S3 destroyed)"]
    DEST9 --> AA
    
    DEST10 --> AA
    DEST11 --> AI
    
    G --> AI
    
    E --> H{"VPC Limit<br/>Reached?"}
    H -->|No| I["Find existing resources"]
    H -->|Yes| J["Try to reuse<br/>existing VPC"]
    
    J --> K{"Existing VPC<br/>Found?"}
    K -->|Yes| L["Import VPC"]
    K -->|No| M["Clean up orphaned VPCs"]
    
    L --> I
    M --> N{"Still at<br/>Limit?"}
    N -->|Yes| O["Prompt user for<br/>limit increase"]
    N -->|No| I
    
    O --> P{"User<br/>Approved?"}
    P -->|Yes| Q["Request quota increase"]
    P -->|No| I
    
    Q --> I
    
    I --> S1["Import Networking<br/>Resources"]
    S1 --> S1A["Import VPC"]
    S1A --> S1B["Import IGW"]
    S1B --> S1C["Import Subnet"]
    S1C --> S1D["Import Route Table"]
    S1D --> S1E["Import Route Table Association"]
    
    S1E --> S2["Check Security Group<br/>Conflicts"]
    
    S2 --> U{"Conflicts<br/>Found?"}
    U -->|Yes| V["Remove conflicting SGs<br/>from state"]
    U -->|No| W["Import Security Groups"]
    
    V --> W
    W --> W1["Import Jail SG"]
    W1 --> W2["Import Victim SG"]
    W2 --> W3["Import Wazuh SG"]
    
    W3 --> S3["Import IAM Resources"]
    S3 --> S3A["Import IAM Role"]
    S3A --> S3B["Import IAM Policy"]
    S3B --> S3C["Import Instance Profile"]
    S3C --> S3D["Import Role Policy Attachment"]
    
    S3D --> S4["Import Storage Resources"]
    S4 --> S4A["Import S3 Bucket"]
    S4A --> S4B["Import S3 Versioning"]
    S4B --> S4C["Import S3 Encryption Config"]
    S4C --> S4D["Import S3 Public Access Block"]
    S4D --> S4E["Import S3 Objects<br/>Wazuh Docker Files"]
    
    S4E --> S5["Import EC2 Instances"]
    S5 --> S5A["Find Wazuh Server"]
    S5A --> S5B["Find Victim Server"]
    S5B --> S5C["Import if exists<br/>or create new"]
    
    S5C --> Y["Run terraform plan"]
    
    D -->|plan| Z["Save plan to tfplan"]
    Z --> AA
    
    D -->|apply| Y
    Y --> AB["Run terraform apply"]
    AB --> AC{"Apply<br/>Successful?"}
    
    AC -->|Yes| AD["Record success<br/>in history"]
    AD --> AA
    
    AC -->|No| AF{"VPC Limit<br/>Error?"}
    AF -->|Yes| AG["Clean up orphaned VPCs"]
    AF -->|No| AH["Record failure<br/>in history"]
    AH --> AI
    
    AG --> AJ["Re-import resources"]
    AJ --> AK["Retry terraform apply"]
    AK --> AL{"Retry<br/>Successful?"}
    
    AL -->|Yes| AM["Record success<br/>after retry"]
    AM --> AA
    AL -->|No| AN["Record failure<br/>after retry"]
    AN --> AI
    
    style A fill:#e1f5e1
    style AA fill:#e1f5e1
    style AI fill:#ffe1e1
    style G fill:#ffe1e1
    style DEST1 fill:#fff4e1
    style DEST2 fill:#fff4e1
    style DEST3 fill:#fff4e1
    style DEST4 fill:#fff4e1
    style DEST5 fill:#fff4e1
    style DEST6 fill:#fff4e1
    style DEST7 fill:#fff4e1
    style DEST8 fill:#fff4e1
    style DEST9 fill:#fff4e1
    style DEST10 fill:#fff4e1
    style DEST11 fill:#ffe1e1
    style S1 fill:#e3f2fd
    style S2 fill:#fff3e0
    style S3 fill:#f3e5f5
    style S4 fill:#e0f2f1
    style S5 fill:#fce4ec
    style AB fill:#c8e6c9
    style AC fill:#ffccbc
```

**Diagram Legend:**
- 🟢 **Green nodes**: Start and successful completion
- 🔴 **Red nodes**: Errors or invalid actions
- 🟡 **Yellow nodes**: Destruction operations
- 🔵 **Blue nodes**: Networking resources
- 🟠 **Orange nodes**: Security/conflict resolution
- 🟣 **Purple nodes**: IAM resources
- 🟦 **Teal nodes**: Storage resources
- 🩷 **Pink nodes**: EC2 instances

**Resource Categories:**
1. **Networking**: VPC, IGW, Subnet, Route Table, Route Table Association
2. **Security**: Security Groups (Jail, Victim, Wazuh)
3. **IAM**: Role, Policy, Instance Profile, Role Policy Attachment
4. **Storage**: S3 Bucket, Versioning, Encryption, Public Access Block, S3 Objects
5. **Compute**: EC2 Instances (Wazuh Server, Victim Server)

### Manual Terraform Commands

If needed, run Terraform directly:
```bash
terraform plan -out=tfplan
terraform apply -auto-approve tfplan
terraform destroy
```

## Project Structure

- `iam.tf`: IAM roles, policies, and instance profiles for EC2 automation.
- `instance.tf`: EC2 instances (Wazuh server and victim VM).
- `network.tf`: VPC, subnets, internet gateway, route tables.
- `providers.tf`: AWS provider configuration.
- `security_groups.tf`: Security groups for network isolation.
- `s3.tf`: S3 bucket with versioning, encryption, and public access block.
- `ecr.tf`: ECR repository with lifecycle policy for image retention.
- `outputs.tf`: Terraform outputs (e.g., instance IPs, S3 bucket name, ECR URL).
- `variables.tf`: Input variables (e.g., bucket/repo names, destroy protection).
- `terraform_safe_apply.sh`: Bash script for safe, state-aware deployments.
- `terraform_safe_apply_history.json`: JSON log of deployment actions.
- `terraform_safe_apply_changelog.md`: Changelog for script updates.
- `README.md`: This file.

## Key Configurations

### S3 Bucket
- **Name**: `cloud-soc-wazuh-assets` (configurable via `s3_bucket_name` variable).
- **Versioning**: Enabled for configuration rollback.
- **Encryption**: AES256 server-side encryption.
- **Public Access**: Blocked for security.

### ECR Repository
- **Name**: `cloud-soc-wazuh-repo` (configurable via `ecr_repository_name` variable).
- **Lifecycle Policy**: Retains last 3 images; deletes older ones to manage costs.
- **Mutability**: Tags are mutable for easy updates.
- **Wazuh Docker Integration**: The S3 bucket stores Wazuh docker configuration files from `wazuh-docker/` directory, which are deployed to EC2.

### IAM Permissions
- **EC2 Role**: `wazuh-ec2-role` with permissions for:
  - EC2 management (isolation, tagging).
  - S3 operations (get/put/list versions).
  - ECR operations (push/pull images).

## Outputs

After deployment, key outputs include:
- `vpc_id`: VPC ID.
- `public_subnet_id`: Public subnet ID.
- `wazuh_instance_public_ip`: Wazuh server public IP.
- `victim_instance_ip`: Victim server private IP.
- `s3_bucket_name`: S3 bucket name.
- `ecr_repository_url`: ECR repository URL.

## Security Considerations

- All resources are tagged with `Project=cloud-soc` for easy identification.
- S3 bucket blocks public access and uses encryption.
- IAM policies follow least-privilege; no wildcard resources where avoidable.
- Use the safe apply script to avoid accidental duplicate resources.

## Troubleshooting

- **Import Errors**: If resources exist in AWS but not in state, the script will attempt to import them. Check AWS console if imports fail.
- **Permissions Issues**: Ensure AWS CLI is configured with sufficient permissions (e.g., EC2, S3, ECR, IAM).
- **State Drift**: The safe apply script mitigates this by importing existing resources.
- **VPC Limit Errors**: The script automatically handles VPC limits by reusing existing VPCs, cleaning up orphaned ones, and prompting for limit increases when needed.
- **Security Group Conflicts**: The script automatically detects and resolves conflicts when importing VPCs with existing security groups.
- **History Logs**: Check `terraform_safe_apply_history.json` for deployment status.

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make changes and test with `terraform validate` and `terraform plan`.
4. Submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file in the root directory.