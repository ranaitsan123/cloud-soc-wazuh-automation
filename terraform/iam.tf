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
}

resource "aws_iam_policy" "wazuh_ec2_policy" {
  name        = "wazuh-ec2-policy"
  description = "Permissions for Wazuh response automation"

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
}
