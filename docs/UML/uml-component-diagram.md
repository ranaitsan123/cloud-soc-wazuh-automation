# UML Component Diagram - Cloud SOC Wazuh Automation

## Overview

This UML component diagram describes the main logical components of the Cloud SOC Wazuh Automation project and how they relate to each other.

## Diagram

```mermaid
classDiagram
    class Developer {
        +Git Push()
        +Build Image()
    }

    class Terraform {
        +Plan()
        +Apply()
        +UploadAssets()
        +CreateResources()
    }

    class AWS_S3 {
        +StoreAssets()
        +VersionAssets()
        +RetrieveAssets()
    }

    class AWS_ECR {
        +StoreImages()
        +PullImages()
        +PruneImages()
    }

    class EC2_Instance {
        +RunDockerCompose()
        +AssumeRole()
        +PullFromS3()
        +PullFromECR()
    }

    class Wazuh_Manager {
        +CollectLogs()
        +DetectThreats()
        +TriggerResponse()
    }

    class Wazuh_Indexer {
        +IndexData()
        +SearchLogs()
    }

    class Wazuh_Dashboard {
        +VisualizeAlerts()
        +DisplayMetrics()
    }

    class IAM_Role {
        +S3Permissions()
        +ECRPermissions()
        +EC2Permissions()
    }

    Developer --|> Terraform : uses
    Terraform --> AWS_S3 : uploads assets
    Terraform --> AWS_ECR : configures repo
    Terraform --> EC2_Instance : provisions
    EC2_Instance --> IAM_Role : assumes
    EC2_Instance --> AWS_S3 : reads/writes
    EC2_Instance --> AWS_ECR : pulls images
    EC2_Instance --> Wazuh_Manager : runs
    Wazuh_Manager --> Wazuh_Indexer : sends logs
    Wazuh_Manager --> Wazuh_Dashboard : sends alerts
    Wazuh_Indexer --> AWS_S3 : stores indices
    IAM_Role --> AWS_S3 : grants access
    IAM_Role --> AWS_ECR : grants access
    IAM_Role --> EC2_Instance : attaches
```

## Explanation

- **Developer**: Authoring and pushing code, building container images, and triggering Terraform deployment.
- **Terraform**: Infrastructure-as-Code responsible for provisioning AWS resources, uploading S3 assets, and preparing the ECR repository.
- **AWS S3**: Stores configuration assets, Docker Compose files, and logs; versioning enables rollback.
- **AWS ECR**: Stores container images with lifecycle pruning of old builds.
- **EC2 Instance**: Hosts Wazuh services and pulls configuration/images from S3 and ECR using IAM credentials.
- **Wazuh Manager**: Central security engine that collects logs, detects threats, and triggers response.
- **Wazuh Indexer**: Indexes event data for search and analytics.
- **Wazuh Dashboard**: Visualizes alerts and security status.
- **IAM Role**: Grants EC2 instances the necessary access to AWS services without embedded credentials.
