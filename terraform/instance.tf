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
              sysctl -w vm.max_map_count=262144
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
              version: '3.9'
              services:
                wazuh-indexer:
                  image: wazuh/wazuh-indexer:4.9.0
                  environment:
                    - "OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g"
                  ulimits:
                    memlock:
                      soft: -1
                      hard: -1
                  volumes:
                    - wazuh_indexer_data:/var/lib/wazuh-indexer
                  ports:
                    - "9200:9200"

                wazuh-manager:
                  image: wazuh/wazuh-manager:4.9.0
                  ports:
                    - "1514:1514"
                    - "1515:1515"
                    - "55000:55000"
                  volumes:
                    - wazuh_manager_data:/var/ossec/data
                    - /opt/wazuh/custom_scripts:/var/ossec/integration

                wazuh-dashboard:
                  image: wazuh/wazuh-dashboard:4.9.0
                  environment:
                    - WAZUH_INDEXER_URL=https://wazuh-indexer:9200
                  ports:
                    - "443:443"
                  depends_on:
                    - wazuh-indexer

              volumes:
                wazuh_indexer_data:
                  driver: local
                wazuh_manager_data:
                  driver: local
              EOD
              cd /opt/wazuh && docker compose up -d
              EOF

  tags = {
    Name = "wazuh-server"
  }
}

resource "aws_instance" "victim_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.victim_sg.id]
  associate_public_ip_address = true
  key_name               = var.wazuh_key_name != "" ? var.wazuh_key_name : null

  user_data = <<-EOF
              #!/bin/bash -xe
              apt-get update -y
              apt-get install -y nginx wazuh-agent
              systemctl enable nginx
              systemctl start nginx
              EOF

  tags = {
    Name = "victim-server"
  }
}
