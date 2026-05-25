data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "wazuh_ec2_role" {
  name               = "wazuh-ec2-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json

  tags = {
    Name      = "wazuh-ec2-role"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_iam_policy" "wazuh_ec2_policy" {
  name        = "wazuh-ec2-policy"
  description = "Permissions for Wazuh response automation"

  tags = {
    Name      = "wazuh-ec2-policy"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "EC2ReadOnly"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeTags"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Sid = "EC2WriteTaggedResources"
        Action = [
          "ec2:StopInstances",
          "ec2:StartInstances",
          "ec2:RebootInstances",
          "ec2:ModifyInstanceAttribute",
          "ec2:CreateTags"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:instance/*",
          "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:network-interface/*"
        ]
      },
      {
        Sid = "SecurityGroupModifyTagged"
        Action = [
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:RevokeSecurityGroupIngress"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:security-group/*"
        ]
      },
      {
        Sid = "S3ProjectBucket"
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:ListBucketVersions",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:PutObjectVersionAcl"
        ]
        Resource = [
          "arn:aws:s3:::${local.asset_bucket_name}",
          "arn:aws:s3:::${local.asset_bucket_name}/*"
        ]
      },
      {
        Sid = "ECRProjectRepositories"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:DescribeRepositories",
          "ecr:CreateRepository",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = [
          "arn:aws:ecr:${var.aws_region}:${data.aws_caller_identity.current.account_id}:repository/${var.ecr_victim_repository_name}",
          "arn:aws:ecr:${var.aws_region}:${data.aws_caller_identity.current.account_id}:repository/${var.ecr_manager_repository_name}"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_wazuh_policy" {
  role       = aws_iam_role.wazuh_ec2_role.name
  policy_arn = aws_iam_policy.wazuh_ec2_policy.arn
}

resource "aws_iam_role_policy_attachment" "attach_ssm_managed" {
  role       = aws_iam_role.wazuh_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role" "victim_ec2_role" {
  name               = "victim-ec2-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json

  tags = {
    Name      = "victim-ec2-role"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_iam_role_policy_attachment" "attach_victim_ssm_managed" {
  role       = aws_iam_role.victim_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_policy" "victim_ec2_policy" {
  name        = "victim-ec2-policy"
  description = "Permissions for Victim instance to pull images from ECR."

  tags = {
    Name      = "victim-ec2-policy"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "ECRAuthToken"
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = ["*"]
      },
      {
        Sid = "ECRImagePull"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:DescribeImages",
          "ecr:DescribeRepositories"
        ]
        Resource = [
          "arn:aws:ecr:${var.aws_region}:${data.aws_caller_identity.current.account_id}:repository/${var.ecr_victim_repository_name}"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_victim_policy" {
  role       = aws_iam_role.victim_ec2_role.name
  policy_arn = aws_iam_policy.victim_ec2_policy.arn
}

resource "aws_iam_instance_profile" "wazuh_instance_profile" {
  name = "wazuh-instance-profile"
  role = aws_iam_role.wazuh_ec2_role.name

  tags = {
    Name      = "wazuh-instance-profile"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_iam_instance_profile" "victim_instance_profile" {
  name = "victim-instance-profile"
  role = aws_iam_role.victim_ec2_role.name

  tags = {
    Name      = "victim-instance-profile"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}
