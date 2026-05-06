resource "aws_ecr_repository" "victim_repo" {
  name                 = var.ecr_victim_repository_name
  image_tag_mutability = "MUTABLE"

  tags = {
    Name      = "cloud-soc-victim-repo"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_ecr_lifecycle_policy" "victim_repo_prune" {
  repository = aws_ecr_repository.victim_repo.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 3 images, delete older"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 3
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_ecr_repository" "manager_repo" {
  name                 = var.ecr_manager_repository_name
  image_tag_mutability = "MUTABLE"

  tags = {
    Name      = "cloud-soc-wazuh-manager-repo"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_ecr_lifecycle_policy" "manager_repo_prune" {
  repository = aws_ecr_repository.manager_repo.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 3 images, delete older"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 3
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

