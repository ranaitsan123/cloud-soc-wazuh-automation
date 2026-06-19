data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_instance" "wazuh_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.management_private.id
  vpc_security_group_ids = [aws_security_group.wazuh_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.wazuh_instance_profile.name
  key_name               = var.wazuh_key_name != "" ? var.wazuh_key_name : null

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 50
    delete_on_termination = true
  }

  depends_on = [
    aws_s3_object.wazuh_docker_compose,
    aws_s3_object.wazuh_certs_generator,
    aws_s3_object.wazuh_config_certs,
    aws_s3_object.wazuh_manager_conf,
    aws_s3_object.wazuh_indexer_config,
    aws_s3_object.wazuh_indexer_users,
    aws_s3_object.wazuh_dashboard_config,
    aws_s3_object.wazuh_dashboard_wazuh_yml,
    aws_nat_gateway.nat,
    aws_route_table_association.management_private
  ]

  user_data = base64encode(<<-EOF
#!/bin/bash
set -e

exec > >(tee /var/log/bootstrap.log)
exec 2>&1

apt-get update -y
apt-get install -y apt-transport-https ca-certificates curl software-properties-common git python3 python3-apt python3-pip awscli snapd

snap install amazon-ssm-agent --classic || true
systemctl enable --now amazon-ssm-agent
EOF
  )

  tags = {
    Name      = "wazuh-server"
    Role      = "wazuh"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_instance" "victim_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.production_private.id
  vpc_security_group_ids = [aws_security_group.victim_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.victim_instance_profile.name
  key_name               = var.wazuh_key_name != "" ? var.wazuh_key_name : null

  depends_on = [
    aws_nat_gateway.nat,
    aws_route_table_association.production_private
  ]

  user_data = base64encode(<<-EOF
#!/bin/bash
set -e

exec > >(tee /var/log/bootstrap.log)
exec 2>&1

apt-get update -y
apt-get install -y apt-transport-https ca-certificates curl gnupg software-properties-common git wget python3 python3-apt python3-pip awscli snapd

snap install amazon-ssm-agent --classic || true
systemctl enable --now amazon-ssm-agent

snap install amazon-ssm-agent --classic || true
systemctl enable --now amazon-ssm-agent
EOF
  )

  tags = {
    Name      = "victim-server"
    Role      = "victim"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}
