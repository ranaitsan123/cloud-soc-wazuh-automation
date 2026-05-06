# Terraform Tutorial: feature/art-soc-baseline Infrastructure

## Purpose

This tutorial explains the Terraform changes made for the `feature/art-soc-baseline` branch. The goal is to establish the internal SOC detection loop in VPC A only, with a Wazuh Manager and a Victim instance deployed in private subnets.

## What changed

### 1. Network topology (`terraform/network.tf`)

- Replaced the previous single public subnet design with a more secure private network layout.
- Created three subnets:
  - `management_private` for the Wazuh Manager
  - `production_private` for the Victim instance
  - `nat_public` to host the NAT Gateway
- Added:
  - an Internet Gateway for the VPC
  - an Elastic IP for the NAT Gateway
  - a NAT Gateway to allow outbound internet from private subnets
  - a private route table routing through the NAT Gateway

### 2. Terraform variables (`terraform/variables.tf`)

- Added dedicated CIDR variables for:
  - `management_private_subnet_cidr`
  - `production_private_subnet_cidr`
  - `nat_public_subnet_cidr`
- Added ECR repository name variables for future image builds:
  - `ecr_victim_repository_name`
  - `ecr_manager_repository_name`

### 3. Instance placement and startup logic (`terraform/instance.tf`)

- Placed the Wazuh Manager in the `management_private` subnet.
- Placed the Victim instance in the `production_private` subnet.
- Removed public IP assignment for both instances to keep them internal to VPC A.
- Added the shared IAM instance profile to both instances.

#### Wazuh Manager user data

- Installs Docker, Docker Compose, Python 3, `boto3`, and AWS CLI.
- Downloads Wazuh Docker Compose files and configuration from S3.
- Generates manager certificates if missing.
- Starts the Wazuh stack.

#### Victim instance user data

- Installs Docker and the Wazuh agent.
- Configures the Wazuh agent to connect to the Wazuh Manager private IP.
- Pulls the custom victim container image from ECR (which includes the baked-in atomics folder).
- Runs the container as `victim-art` with a volume mount for persistence.
- The container has PowerShell and Invoke-AtomicRedTeam pre-installed, with the atomics folder copied from the local workspace.

### 4. IAM and SSM readiness (`terraform/iam.tf`)

- Kept the custom EC2 policy for S3 and ECR access.
- Added the managed policy `AmazonSSMManagedInstanceCore` to support SSM commands from Codespace.
- Both EC2 instances now use the same instance profile.

### 5. Security groups (`terraform/security_groups.tf`)

- Scoped Wazuh Manager ports to the VPC CIDR instead of `0.0.0.0/0`.
- Kept SSH access configurable via `allowed_ssh_cidr`.
- Allowed Victim HTTP traffic only from inside the VPC.
- Left the jail security group with no ingress/egress as a future isolation control.

### 6. ECR repositories (`terraform/ecr.tf`)

- Added two ECR repositories:
  - `victim_repo`
  - `manager_repo`
- Added lifecycle policies to retain only the last 3 images.

### 8. Victim Dockerfile (`docker/Dockerfile.victim`)

- Created a new Dockerfile that:
  - Uses Ubuntu 22.04 as base
  - Installs PowerShell Core
  - Installs the Invoke-AtomicRedTeam PowerShell module
  - Copies the local `atomics/` folder into `/opt/fortress/atomics`
  - Sets appropriate permissions

## Why this design

This branch focuses on the first baseline win:

- a contained internal SOC loop
- a Wazuh Manager that can see and collect logs from the Victim
- no external attacker infrastructure yet
- no public-facing application servers in VPC A

The NAT Gateway enables the instances to reach the internet securely for package installation and S3/ECR access without exposing them publicly.

## How to use it

### Option 1: Manual Build and Push (Quick Start)

1. **Build and push the victim image to ECR:**

   From your Codespace terminal:

   ```bash
   cd /workspaces/cloud-soc-wazuh-automation

   # Authenticate Docker with ECR
   aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.eu-north-1.amazonaws.com

   # Build the victim image
   docker build -f docker/Dockerfile.victim -t cloud-soc-victim:latest .

   # Tag for ECR
   docker tag cloud-soc-victim:latest <your-account-id>.dkr.ecr.eu-north-1.amazonaws.com/cloud-soc-victim:latest

   # Push to ECR
   docker push <your-account-id>.dkr.ecr.eu-north-1.amazonaws.com/cloud-soc-victim:latest
   ```

   Replace `<your-account-id>` with your actual AWS account ID.

2. **Deploy the infrastructure:**

   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

### Option 2: Automated CI/CD (Recommended)

1. **Set up GitHub Secrets:**

   In your GitHub repository, go to Settings → Secrets and variables → Actions and add:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

   These credentials should have ECR push permissions.

2. **Push changes to trigger CI/CD:**

   ```bash
   git add .
   git commit -m "Add victim Dockerfile and CI/CD workflow"
   git push origin feature/art-soc-baseline
   ```

   The GitHub Actions workflow (`.github/workflows/build-victim-image.yml`) will automatically:
   - Build the Docker image when `docker/Dockerfile.victim` or `atomics/` files change
   - Push to ECR with `latest` tag and commit SHA tag
   - Comment on PRs with the image details

3. **Deploy the infrastructure:**

   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

3. **After deployment, use the output values to identify:**

   - the Wazuh Manager private IP
   - the Victim private IP
   - the S3 bucket name
   - the ECR repository URLs

## Notes and next steps

- The Wazuh Manager initialization depends on the `wazuh-docker` assets already being uploaded to the configured S3 bucket.
- The Victim instance now pulls the custom container image from ECR, which includes the atomics folder baked in from your local workspace.
- The SSM command for triggering the attack now uses `docker exec victim-art` to run inside the container.
- If you want to run manual tests, use SSM and `Invoke-AtomicTest` from your Codespace.

## File location

The tutorial is saved to:

- `docs/ART/terraform-feature-art-soc-baseline-tutorial.md`
