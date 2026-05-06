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
    aws_s3_object.wazuh_dashboard_wazuh_yml
  ]

  user_data = base64encode(<<-EOF
#!/bin/bash
set -e

# Enable error logging
exec > >(tee /var/log/wazuh-init.log)
exec 2>&1

echo "[$(date)] Starting Wazuh server initialization..."

# System configuration
sysctl -w vm.max_map_count=262144

# Update package list
apt-get update -y

# Install dependencies
apt-get install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  software-properties-common \
  git \
  awscli \
  python3 \
  python3-pip

# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmour -o /usr/share/keyrings/docker-archive-keyring.gpg
 echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu jammy stable" > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io
usermod -aG docker ubuntu

# Install Python libs
pip3 install boto3

# Create wazuh directory structure
mkdir -p /opt/wazuh/{config,custom_scripts}

# Download files from S3
echo "[$(date)] Downloading wazuh-docker files from S3..."
S3_BUCKET="${var.s3_bucket_name}"
S3_PREFIX="wazuh-docker"

aws s3 cp "s3://$${S3_BUCKET}/$${S3_PREFIX}/docker-compose.yml" /opt/wazuh/docker-compose.yml
aws s3 cp "s3://$${S3_BUCKET}/$${S3_PREFIX}/generate-indexer-certs.yml" /opt/wazuh/generate-indexer-certs.yml
aws s3 cp "s3://$${S3_BUCKET}/$${S3_PREFIX}/config/certs.yml" /opt/wazuh/config/certs.yml

# Download config files
mkdir -p /opt/wazuh/config/{wazuh_cluster,wazuh_indexer,wazuh_dashboard,wazuh_indexer_ssl_certs}

aws s3 cp "s3://$${S3_BUCKET}/$${S3_PREFIX}/config/wazuh_cluster/wazuh_manager.conf" /opt/wazuh/config/wazuh_cluster/wazuh_manager.conf
aws s3 cp "s3://$${S3_BUCKET}/$${S3_PREFIX}/config/wazuh_indexer/wazuh.indexer.yml" /opt/wazuh/config/wazuh_indexer/wazuh.indexer.yml
aws s3 cp "s3://$${S3_BUCKET}/$${S3_PREFIX}/config/wazuh_indexer/internal_users.yml" /opt/wazuh/config/wazuh_indexer/internal_users.yml
aws s3 cp "s3://$${S3_BUCKET}/$${S3_PREFIX}/config/wazuh_dashboard/opensearch_dashboards.yml" /opt/wazuh/config/wazuh_dashboard/opensearch_dashboards.yml
aws s3 cp "s3://$${S3_BUCKET}/$${S3_PREFIX}/config/wazuh_dashboard/wazuh.yml" /opt/wazuh/config/wazuh_dashboard/wazuh.yml

# Generate certificates ONLY if they don't already exist
CERTS_DIR="/opt/wazuh/config/wazuh_indexer_ssl_certs"
if [ ! -d "$CERTS_DIR" ] || [ -z "$(ls -A $CERTS_DIR 2>/dev/null)" ]; then
  echo "[$(date)] Certificate directory is empty or missing. Generating certificates..."
  mkdir -p "$CERTS_DIR"
  cd /opt/wazuh
  docker compose -f generate-indexer-certs.yml run --rm generator
  echo "[$(date)] Certificates generated successfully."
else
  echo "[$(date)] Certificates already exist. Skipping generation."
fi

# Set permissions
chown -R ubuntu:ubuntu /opt/wazuh
chmod -R 755 /opt/wazuh

# Start Wazuh services
echo "[$(date)] Starting Wazuh services..."
cd /opt/wazuh
docker compose up -d

echo "[$(date)] Wazuh server initialization completed successfully."
EOF
  )

  tags = {
    Name      = "wazuh-server"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_instance" "victim_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.production_private.id
  vpc_security_group_ids = [aws_security_group.victim_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.wazuh_instance_profile.name
  key_name               = var.wazuh_key_name != "" ? var.wazuh_key_name : null

  user_data = <<-EOF
#!/bin/bash -xe
apt-get update -y
apt-get install -y apt-transport-https ca-certificates curl gnupg software-properties-common git wget

# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmour -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu jammy stable" > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io
usermod -aG docker ubuntu

# Install and configure Wazuh agent
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && chmod 644 /usr/share/keyrings/wazuh.gpg
cat <<WAZUH_REPO >/etc/apt/sources.list.d/wazuh.list
deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main
WAZUH_REPO
apt-get update -y
WAZUH_MANAGER="${aws_instance.wazuh_server.private_ip}" apt-get install -y wazuh-agent
systemctl daemon-reload
systemctl enable wazuh-agent
systemctl start wazuh-agent

# Pull and run the victim container from ECR
aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.victim_repo.repository_url}
docker pull ${aws_ecr_repository.victim_repo.repository_url}:latest
docker run -d --name victim-art -v /opt/fortress:/opt/fortress ${aws_ecr_repository.victim_repo.repository_url}:latest tail -f /dev/null

# Start Wazuh agent service
systemctl enable wazuh-agent
systemctl start wazuh-agent
EOF

  tags = {
    Name      = "victim-server"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}
