variable "ecr_repository_name" {
  type        = string
  description = "ECR repository name for SOC container images. Must be unique within AWS account region."
  default     = "cloud-soc-wazuh-repo"
}

resource "aws_ecr_repository" "wazuh_repo" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"

  tags = {
    Name      = "cloud-soc-wazuh-repo"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_ecr_lifecycle_policy" "wazuh_repo_prune" {
  repository = aws_ecr_repository.wazuh_repo.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 3 images, delete older"
        selection = {
          tagStatus = "any"
          countType = "imageCountMoreThan"
          countNumber = 3
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

