# ☁️ Cloud SOC – Wazuh Threat Detection & Automated Response

<div align="center">

![GitHub License](https://img.shields.io/github/license/ranaitsan123/cloud-soc-wazuh-automation?style=flat-square)
![GitHub Stars](https://img.shields.io/github/stars/ranaitsan123/cloud-soc-wazuh-automation?style=flat-square)
![Terraform](https://img.shields.io/badge/Terraform-%3E%3D1.0-blueviolet?style=flat-square&logo=terraform)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?style=flat-square&logo=docker)
![Python](https://img.shields.io/badge/Python-3.8%2B-green?style=flat-square&logo=python)
![AWS](https://img.shields.io/badge/AWS-Enabled-orange?style=flat-square&logo=amazonaws)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)

*A cloud-native Security Operations Center (SOC) with threat detection, log analysis, and automated incident response*

[Documentation](#-documentation) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [Contributing](#-contribution)

</div>

---

## 📌 Overview

This project implements a **production-ready, cloud-based Security Operations Center (SOC)** designed to detect, analyze, and respond to security threats in real time.

It combines **cloud infrastructure, SIEM, attack simulation, and DevSecOps automation** to create a modern cybersecurity monitoring environment that bridges theory and practical implementation.

**Key Values:**
- 🛡️ **Real-time threat detection** using Wazuh
- 🔄 **Automated incident response** via Python + AWS SDK
- 🏗️ **Infrastructure as Code** with Terraform
- 📊 **Centralized log management** and analysis
- 🧪 **Attack simulation** for validation (Atomic Red Team, Caldera)
- 🔁 **Reproducible and scalable** cloud architecture

---

## 🎯 Objectives

✅ Centralize system and network logs  
✅ Detect malicious activities (SSH brute force, abnormal behavior, privilege escalation)  
✅ Generate real-time security alerts  
✅ Automate incident response workflows  
✅ Reduce Mean Time To Response (MTTR)  
✅ Build a reproducible and scalable cloud security architecture  
✅ Demonstrate DevSecOps principles in action  

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Cloud                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   EC2        │  │   EC2        │  │   EC2        │          │
│  │ (Protected)  │  │ (Protected)  │  │ (Protected)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         ▲                 ▲                  ▲                   │
│         │ Wazuh Agents   │ Wazuh Agents    │ Wazuh Agents      │
│         └─────────────────┴──────────────────┘                  │
│                           │                                     │
│                    ┌──────▼──────┐                             │
│                    │ Wazuh       │                             │
│                    │ Manager &   │                             │
│                    │ Indexer     │                             │
│                    │ (Docker)    │                             │
│                    └──────┬──────┘                             │
│                           │                                     │
│                    ┌──────▼──────┐                             │
│                    │ OpenSearch  │                             │
│                    │ Dashboard   │                             │
│                    │ (Wazuh UI)  │                             │
│                    └─────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
                           │
                    ┌──────▼──────────┐
                    │  Automation     │
                    │  Python Scripts │
                    │  (Boto3)        │
                    └─────────────────┘
```

**Core Components:**
- **Cloud Infrastructure** → AWS (EC2, VPC, Security Groups, IAM, S3, ECR)
- **SIEM Platform** → Wazuh (Manager, Indexer, Dashboard)
- **Containerization** → Docker & Docker Compose
- **Infrastructure as Code** → Terraform
- **Automation & Response** → Python (Boto3)
- **Attack Simulation** → Atomic Red Team, MITRE Caldera

---

## ⚙️ Features

### 🔹 Infrastructure Automation
- ✅ Fully automated AWS deployment using **Terraform**
- ✅ Reproducible and scalable environment
- ✅ Safe apply scripts with **changelogging** and rollback support
- ✅ Centralized configuration management (S3, ECR)
- ✅ IAM best practices with minimal privilege policies

### 🔹 Log Collection & Monitoring
- ✅ Wazuh agents deployed on monitored machines (EC2 instances)
- ✅ Centralized log aggregation via Wazuh Manager
- ✅ Real-time visualization via Wazuh Dashboard
- ✅ Automated container deployment and orchestration

### 🔹 Threat Detection
- ✅ Detection of:
  - SSH brute force attacks (T1110)
  - Suspicious command execution (T1059)
  - System anomalies & privilege escalation (T1068)
  - Unauthorized access attempts
- ✅ Custom detection rules
- ✅ Correlation with MITRE ATT&CK framework

### 🔹 Attack Simulation
- ✅ Unit attack testing with **Atomic Red Team**
- ✅ Advanced adversary simulation with **MITRE Caldera**
- ✅ Reproducible attack scenarios

### 🔹 Automated Incident Response
- ✅ Integration with Wazuh Active Response
- ✅ Python scripts using AWS SDK (Boto3)
- ✅ Automatic actions:
  - Blocking malicious IPs
  - Isolating compromised instances (Security Groups)
  - Triggering CloudWatch alarms
  - Logging incidents to S3

---

## 📂 Repository Structure

```
cloud-soc-wazuh-automation/
│
├── 📄 docker-compose.yml          # Global SOC orchestration
├── 📄 terraform.tfstate           # Terraform state (AWS resources)
│
├── 📁 terraform/                  # Infrastructure as Code
│   ├── providers.tf               # AWS provider configuration
│   ├── variables.tf               # Input variables
│   ├── main.tf / *.tf             # Resource definitions
│   ├── terraform_safe_apply.sh    # Safe deployment script
│   └── terraform_safe_apply_changelog.* # Deployment history
│
├── 📁 wazuh-docker/               # Wazuh SIEM deployment
│   ├── docker-compose.yml         # Wazuh services orchestration
│   ├── generate-indexer-certs.yml # Certificate generation
│   └── config/                    # Configuration files
│       ├── wazuh_manager.conf
│       ├── opensearch_dashboards.yml
│       └── wazuh.indexer.yml
│
├── 📁 docker/                     # Custom Docker images
│   └── Dockerfile
│
├── 📁 automation/                 # Incident response scripts
│   ├── isolate_vm.py              # VM isolation (Security Group)
│   └── README.md
│
├── 📁 attack-scenarios/           # Attack testing scenarios
│   ├── atomic_red_team_tests.yml
│   └── README.md
│
├── 📁 scripts/                    # Utility scripts
│   ├── terraform_cleaner.sh       # Cleanup resources
│   └── terraform_history_report.sh
│
├── 📁 docs/                       # Technical documentation
│   ├── architecture-diagrams/
│   ├── deployment-guide.md
│   ├── detection-rules.md
│   ├── operational-scenarios.md
│   ├── s3-ecr-workflow.md
│   ├── system-workflow.md
│   ├── uml-*.md                   # UML diagrams
│   └── iam-permissions.md
│
├── 📄 README.md                   # This file
└── 📄 LICENSE

```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required tools:
- AWS CLI (configured with credentials)
- Terraform >= 1.0
- Docker & Docker Compose
- Python 3.8+
- Git
- Linux environment (Codespaces, WSL, or native Linux)
```

### Installation & Deployment

**1. Clone the Repository**
```bash
git clone https://github.com/ranaitsan123/cloud-soc-wazuh-automation.git
cd cloud-soc-wazuh-automation
```

**2. Launch Development Environment**
```bash
# Start the DevOps container with AWS and Terraform mounted
docker-compose up -d devops

# Enter the container shell
docker-compose exec devops bash
```

**3. Deploy AWS Infrastructure**
```bash
cd terraform/

# Initialize Terraform
terraform init -input=false

# Review deployment plan
./terraform_safe_apply.sh plan

# Deploy infrastructure (with automatic VPC management & changelog)
./terraform_safe_apply.sh apply
```

The script will:
- ✅ Automatically import existing AWS resources (prevents duplicates)
- ✅ Manage VPC limits intelligently
- ✅ Create EC2 instances, Security Groups, S3, ECR, and IAM roles
- ✅ Log deployment history to `terraform_safe_apply_history.json`

**4. Deploy Wazuh SOC**

Terraform automatically handles the entire Wazuh Stack deployment on the EC2 instance:
- Sets system limits
- Downloads configurations from S3
- Generates certificates
- Starts all services via Docker Compose

**⏳ Wait ~2-3 minutes for EC2 instance to initialize and services to start**

**5. Access the Dashboard**
```
🌐 Wazuh Dashboard: https://localhost
📊 Port: 443 (HTTPS)
👤 Default Username: admin
🔐 Password: See wazuh-docker/config/wazuh.yml
```

**6. Verify Deployment**
```bash
# Check all services are running
docker compose ps

# View Wazuh logs
docker compose logs -f wazuh.manager
```

---

## 🔐 Cloud Security & Architecture Design

This project follows **cloud security best practices** and a **defense-in-depth strategy** to ensure a secure and resilient SOC environment.

---

### 🏗️ Architecture Design Principles

The infrastructure is designed with the following principles:

- **Isolation by design**
  - Separation between SOC components and monitored resources
  - Dedicated network segmentation using VPC

- **Least privilege access**
  - IAM roles and policies are strictly scoped
  - No hardcoded credentials

- **Infrastructure as Code (IaC)**
  - All resources are provisioned using Terraform
  - Ensures consistency, versioning, and reproducibility

- **Modular architecture**
  - Separation between infrastructure, detection, and automation layers

---

### 🌐 Network Security

- Custom **VPC** with controlled subnets
- Strict **Security Groups**:
  - Only required ports are open (principle of minimal exposure)
  - SSH access restricted to trusted IPs
- Internal communication between components is limited and controlled

---

### 🔑 Identity & Access Management (IAM)

- Use of **IAM Roles instead of static credentials**
- Fine-grained permissions for:
  - EC2 instances
  - Automation scripts (Boto3)
- Principle of **least privilege enforced across all services**

---

### 🖥️ Host Security

- Wazuh agents deployed on all monitored instances
- Continuous log monitoring:
  - Authentication logs
  - System activity
  - File integrity monitoring (FIM)

---

### 📊 Logging & Monitoring

- Centralized logging via Wazuh SIEM
- Real-time alerting and visualization
- Correlation of events with **MITRE ATT&CK framework**

---

### ⚔️ Threat Detection Strategy

The detection approach is based on:

- Signature-based detection (Wazuh rules)
- Behavior-based detection (anomaly patterns)
- Mapping to known attack techniques

---

### 🤖 Automated Incident Response

- Integration with Wazuh Active Response
- Python scripts using AWS SDK (Boto3)
- Automated remediation actions:
  - Blocking malicious IP addresses
  - Modifying Security Groups dynamically
  - Isolating compromised instances

---

### 🧪 Security Validation

To validate the effectiveness of the architecture:

- Simulated attacks using:
  - Atomic Red Team
  - MITRE Caldera
- Continuous testing of:
  - Detection capabilities
  - Response mechanisms

---

### 🛡️ Defense-in-Depth Strategy

Security is enforced across multiple layers:

1. **Network layer** (VPC, Security Groups)
2. **Identity layer** (IAM)
3. **Host layer** (Wazuh agents)
4. **Detection layer** (SIEM rules)
5. **Response layer** (automation scripts)

---

### 📌 Key Takeaway

This architecture demonstrates how to build a **secure, monitored, and automated cloud environment**, aligned with modern **DevSecOps and SOC practices**. It showcases proactive security thinking through layered defense mechanisms and automation-first incident response.

---

## 🧪 Attack & Detection Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Simulate Attack                                             │
│     (Atomic Red Team / Caldera)                                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Generate Logs on Target Machine                             │
│     (Binary execution, network activity, system calls)          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Collect via Wazuh Agent                                     │
│     (Real-time log forwarding)                                  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Analyze & Correlate Events                                  │
│     (Wazuh Manager processing)                                  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. Trigger Alerts in Dashboard                                 │
│     (Visual detection, analytics)                               │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. Map to MITRE ATT&CK Techniques                              │
│     (Threat intelligence correlation)                           │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. Execute Automated Response (if configured)                  │
│     (Block IP, isolate instance, alert ops team)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Example Detection Scenarios

| Scenario | MITRE Technique | Detection Method | Automated Response |
|----------|-----------------|-----------------|-------------------|
| **SSH Brute Force** | T1110 (Brute Force) | Wazuh rules (failed logins) | Block IP via SG |
| **Command Execution** | T1059 (Command Line) | Binary execution logs | Alert + Monitoring |
| **Privilege Escalation** | T1068 (Exploitation) | Sudoers activity logs | Isolate instance |
| **Suspicious Process** | T1543 (Process Creation) | Process monitoring | Kill process + Alert |
| **Unauthorized Access** | T1021 (Remote Access) | SSH/RDP logs | Revoke access |

---

## 📈 Project Status

| Feature | Status | Notes |
|---------|--------|-------|
| AWS Infrastructure (Terraform) | ✅ | EC2, VPC, SG, IAM, S3, ECR |
| Wazuh SOC Deployment | ✅ | Manager, Indexer, Dashboard |
| Log Collection & Monitoring | ✅ | Real-time agent deployment |
| Attack Simulation (Atomic Red Team) | ✅ | Basic scenarios implemented |
| Detection Rules | 🔄 | Ongoing optimization |
| Automated Response (Python + Boto3) | 🔄 | VM isolation implemented |
| Advanced Scenarios (Caldera) | ⏳ | In development |
| CI/CD Integration | ⏳ | Planned |

---

## 🔮 Future Roadmap

- 📌 **Multi-stage attack scenarios** with Caldera
- 📌 **Enhanced detection rules** for advanced threats
- 📌 **Full SOC playbooks** (Detection → Investigation → Response)
- 📌 **CI/CD pipeline** for deployment automation
- 📌 **Performance optimization** and load testing
- 📌 **SIEM integration** with Splunk/ELK alternatives
- 📌 **Threat intelligence feeds** integration
- 📌 **Custom dashboard** widgets and reports

---

## 📚 Documentation

Comprehensive documentation is available in the [`/docs`](./docs) folder:

- **Architecture Diagrams** – Component relationships and data flow
- **Deployment Guide** – Step-by-step setup instructions
- **Detection Rules** – Wazuh custom rules and logic
- **Operational Scenarios** – Real-world use cases
- **System Workflow** – End-to-end detection process
- **IAM Permissions** – AWS security best practices
- **Branch Strategy** – `feature/art-soc-baseline` plan and step-by-step validation
- **UML Diagrams** – System design and interactions

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create a feature branch** (`git checkout -b feature/my-feature`)
3. **Commit changes** with clear messages
4. **Push** to your fork (`git push origin feature/my-feature`)
5. **Open a Pull Request** with a detailed description

### Guidelines:
- Follow existing code style
- Add unit tests for new features
- Update documentation
- Test infrastructure changes in a sandbox environment

---

## 🔗 Related Repositories

- Related repo: https://github.com/ranaitsan123/cloud-soc-wazuh
- Main automation: https://github.com/ranaitsan123/cloud-soc-wazuh-automation

---

## 👤 Author

**Aicha Lahnite**  
*Master's in Intelligent Systems Engineering*  
*Cloud, Networks & Systems Specialization*  

---

## 📜 License

This project is licensed under the **MIT License** – see the [LICENSE](./LICENSE) file for details.

---

## 💡 Key Takeaways

This project demonstrates how to design and implement a **cloud-native SOC** capable of:

- 🎯 **Detecting threats in real time** using SIEM technology
- 🤖 **Automating incident response** to reduce MTTR
- 🧪 **Simulating real-world cyberattacks** for validation
- 🏗️ **Building scalable infrastructure** with IaC principles

It bridges the gap between **theoretical cybersecurity concepts** and **practical DevSecOps implementation**, serving as both a learning resource and a production-ready security framework.

---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star!**

</div>