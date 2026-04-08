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
        Action = [
          "ec2:DescribeInstances",
          "ec2:StopInstances",
          "ec2:StartInstances",
          "ec2:RebootInstances",
          "ec2:DescribeNetworkInterfaces",
          "ec2:ModifyInstanceAttribute",
          "ec2:DescribeSecurityGroups",
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:RevokeSecurityGroupIngress",
          "ec2:CreateTags"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
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
          "arn:aws:s3:::${var.s3_bucket_name}",
          "arn:aws:s3:::${var.s3_bucket_name}/*"
        ]
      },
      {
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
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_wazuh_policy" {
  role       = aws_iam_role.wazuh_ec2_role.name
  policy_arn = aws_iam_policy.wazuh_ec2_policy.arn
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
