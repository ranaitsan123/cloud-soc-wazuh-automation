# Cloud SOC Wazuh Automation - System Workflow

## Overview

This diagram illustrates the complete workflow of the Cloud SOC Wazuh Automation system, showing how all components interact from infrastructure deployment to incident response.

## Diagram

```mermaid
graph TD
    A["AWS Infrastructure<br/>Terraform Deployment"] --> B["VPC Network<br/>Security Groups"]
    A --> C["EC2 Instances<br/>Wazuh Server & Victim VM"]
    A --> D["S3 Bucket<br/>Asset Storage"]
    A --> E["ECR Repository<br/>Container Registry"]
    A --> F["IAM Roles & Policies<br/>Permissions Management"]

    B --> G["Docker Compose<br/>Orchestration"]
    C --> G

    G --> H["Wazuh Manager<br/>Core Engine"]
    G --> I["Wazuh Indexer<br/>Log Storage & Search"]
    G --> J["Wazuh Dashboard<br/>OpenSearch Visualization"]

    H --> K["Log Collection<br/>&amp; Analysis"]
    I --> K
    J --> L["Security Alerts<br/>Real-time Monitoring"]

    K --> M{"Threat<br/>Detection"}

    M -->|Attack Detected| N["Attack Scenarios<br/>Test &amp; Validation"]
    M -->|Incident Response| O["Automation Scripts<br/>VM Isolation"]

    N --> P["Simulate Attacks<br/>Test Detection Capabilities"]
    P --> Q["Validate SOC<br/>Configuration"]

    O --> R["Isolate Compromised VM<br/>Containment"]
    R --> S["Execute Response<br/>Actions"]

    D -.->|Versioned Assets| O
    E -.->|Container Images| G

    S --> T["Post-Incident<br/>Analysis & Logging"]
    Q --> T
    T --> U["Continuous Improvement<br/>Configuration Updates"]

    style A fill:#ff9999
    style G fill:#99ccff
    style M fill:#ffcc99
    style U fill:#99ff99
```

## Key Components Explained

### Infrastructure Layer (Red)
- **AWS Infrastructure**: Terraform provisions all cloud resources
- **VPC Network & Security Groups**: Isolated network environment with security controls
- **EC2 Instances**: Wazuh server and victim VM for testing
- **S3 Bucket**: Versioned storage for configurations and assets
- **ECR Repository**: Container registry for Docker images
- **IAM Roles & Policies**: Secure permissions for automation

### Container Layer (Blue)
- **Docker Compose**: Orchestrates Wazuh services deployment
- **Wazuh Manager**: Core security engine for threat detection
- **Wazuh Indexer**: Log storage and search capabilities
- **Wazuh Dashboard**: OpenSearch visualization interface

### Security Operations (Orange)
- **Log Collection & Analysis**: Gathers and processes security events
- **Security Alerts**: Real-time monitoring and notifications
- **Threat Detection**: Automated identification of security incidents

### Response Flow
- **Attack Scenarios**: Testing and validation of detection capabilities
- **Automation Scripts**: VM isolation and incident response actions
- **Post-Incident Analysis**: Review and improvement of SOC configuration

## Workflow Flow

1. **Infrastructure Setup**: Terraform deploys AWS resources
2. **Service Deployment**: Docker Compose launches Wazuh components
3. **Monitoring**: Wazuh collects and analyzes logs in real-time
4. **Detection**: Automated threat identification
5. **Response**: Either testing scenarios or incident containment
6. **Analysis**: Post-incident review and configuration updates