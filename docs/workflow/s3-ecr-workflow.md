# S3 & ECR Workflow with System Interactions - Detailed Architecture

## Overview

This diagram provides a detailed view of how S3 and ECR services integrate with the overall system architecture, showing data flows, permissions, and operational interactions.

## Diagram

```mermaid
graph TD
    subgraph Developer["👤 Developer Workstation"]
        A["Local Repository<br/>Git Push"]
    end

    subgraph AWS["☁️ AWS Cloud"]
        subgraph Storage["Storage Layer"]
            S3["S3 Bucket<br/>cloud-soc-wazuh-assets<br/>- Versioning Enabled<br/>- Encryption AES256<br/>- Public Access Blocked"]
            ECR["ECR Repository<br/>cloud-soc-wazuh-repo<br/>- Lifecycle Policy<br/>- Keep Last 3 Images"]
        end

        subgraph Compute["Compute Layer"]
            TF["Terraform State<br/>IaC Execution"]
            EC2M["EC2 Wazuh Manager<br/>IAM Role Attached"]
            EC2V["EC2 Victim VM<br/>IAM Role Attached"]
        end

        subgraph Security["Security Layer"]
            IAM["IAM Role & Policies<br/>- S3 Read/Write Access<br/>- ECR Push/Pull Access<br/>- EC2 Control Actions"]
        end
    end

    subgraph Deployment["🐳 Deployment Process"]
        DC["Docker Compose<br/>Wazuh Services"]
        WM["Wazuh Manager"]
        WI["Wazuh Indexer"]
        WD["Wazuh Dashboard"]
    end

    A -->|1. Push Config| S3
    A -->|2. Build Images| ECR

    TF -->|3. Upload Assets| S3
    TF -->|3. Configure ECR| ECR

    TF -->|4. Create/Configure| EC2M
    TF -->|4. Create/Configure| EC2V

    IAM -->|Attach IAM Role| EC2M
    IAM -->|Attach IAM Role| EC2V

    EC2M -->|5. Pull docker-compose.yml<br/>s3:GetObject| S3
    EC2M -->|5. Pull config files<br/>s3:GetObject| S3
    EC2M -->|6. Pull Container Images<br/>ecr:BatchGetImage| ECR

    EC2V -->|5. Pull attack scripts<br/>s3:GetObject| S3
    EC2V -->|6. Pull test images<br/>ecr:BatchGetImage| ECR

    EC2M -->|7. Initialize| DC
    DC --> WM
    DC --> WI
    DC --> WD

    EC2M -->|8. Push Logs/Metrics<br/>s3:PutObject| S3
    EC2V -->|8. Send Logs| WM

    WM -->|9. Collect & Analyze| WI
    WI -->|10. Index & Store| S3

    WM -.->|11. Threat Detection| A

    subgraph Versioning["📦 Versioning & Rollback"]
        V1["Version 1<br/>docker-compose.yml"]
        V2["Version 2<br/>docker-compose.yml"]
        V3["Version 3<br/>docker-compose.yml"]
    end

    S3 -.->|Maintains All Versions| V1
    S3 -.->|Maintains All Versions| V2
    S3 -.->|Maintains All Versions| V3

    style Developer fill:#e1f5ff
    style AWS fill:#fff3e0
    style Storage fill:#f3e5f5
    style Compute fill:#e8f5e9
    style Security fill:#ffe0b2
    style Deployment fill:#f0f4c3
    style Versioning fill:#e0f2f1
```

## Key Components Explained

### Developer Workstation (Light Blue)
- **Local Repository**: Developer's local Git repository
- **Git Push**: Configuration changes and code updates

### AWS Cloud Infrastructure (Light Orange)

#### Storage Layer (Purple)
- **S3 Bucket**: Secure, versioned storage with encryption
  - Versioning enabled for rollback capabilities
  - AES256 encryption for data protection
  - Public access completely blocked
- **ECR Repository**: Container registry with lifecycle management
  - Automatic cleanup of old images
  - Cost optimization through retention policies

#### Compute Layer (Light Green)
- **Terraform State**: Infrastructure as Code execution
- **EC2 Wazuh Manager**: Main security server with IAM permissions
- **EC2 Victim VM**: Test environment with IAM permissions

#### Security Layer (Light Orange)
- **IAM Role & Policies**: Least-privilege access control
  - S3 read/write permissions for configurations and logs
  - ECR push/pull permissions for container images
  - EC2 control permissions for automation scripts

### Deployment Process (Light Yellow)
- **Docker Compose**: Container orchestration
- **Wazuh Services**: Manager, Indexer, and Dashboard components

### Versioning & Rollback (Light Cyan)
- **S3 Versioning**: Maintains all historical versions
- **Rollback Capability**: Instant restoration to previous configurations

## Workflow Flow

1. **Configuration Push**: Developer pushes configs to S3
2. **Image Building**: Custom container images pushed to ECR
3. **Infrastructure Setup**: Terraform uploads assets and configures services
4. **Instance Creation**: EC2 instances created with IAM roles attached
5. **Asset Retrieval**: Instances pull configurations and images from S3/ECR
6. **Service Initialization**: Docker Compose launches Wazuh services
7. **Runtime Operations**: Logs and metrics stored back to S3
8. **Threat Detection**: Wazuh analyzes logs and detects incidents
9. **Version Control**: S3 maintains all versions for rollback scenarios

## Security Features

- **IAM Instance Profiles**: No hardcoded credentials on EC2 instances
- **S3 Encryption**: All data encrypted at rest
- **Public Access Blocked**: S3 bucket completely private
- **Versioning**: Complete audit trail of configuration changes
- **Lifecycle Policies**: Automatic cleanup of ECR images