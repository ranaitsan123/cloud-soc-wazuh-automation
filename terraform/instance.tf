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
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.wazuh_sg.id]
  associate_public_ip_address = true
  iam_instance_profile   = aws_iam_instance_profile.wazuh_instance_profile.name
  key_name               = var.wazuh_key_name != "" ? var.wazuh_key_name : null

  user_data = <<-EOF
              #!/bin/bash -xe
              apt-get update -y
              apt-get install -y apt-transport-https ca-certificates curl software-properties-common git
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmour -o /usr/share/keyrings/docker-archive-keyring.gpg
              echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu jammy stable" > /etc/apt/sources.list.d/docker.list
              apt-get update -y
              apt-get install -y docker-ce docker-ce-cli containerd.io
              usermod -aG docker ubuntu
              curl -L "https://github.com/docker/compose/releases/download/v2.23.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
              chmod +x /usr/local/bin/docker-compose
              mkdir -p /opt/wazuh
              cat > /opt/wazuh/docker-compose.yml <<'EOD'
              version: '3.17'
              services:
                wazuh:
                  image: wazuh/wazuh:5.0.2
                  ports:
                    - "443:443"
                    - "1514:1514/tcp"
                    - "1515:1515/tcp"
                    - "55000:55000/tcp"
                  volumes:
                    - wazuh_data:/var/ossec/data
                    - /opt/wazuh/custom_scripts:/var/ossec/integration
              volumes:
                wazuh_data:
                  driver: local
              EOD
              cd /opt/wazuh && docker compose up -d
              EOF

  tags = {
    Name = "wazuh-server"
  }
}
