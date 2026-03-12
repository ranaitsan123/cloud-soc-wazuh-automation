resource "aws_security_group" "wazuh_sg" {
  name        = "wazuh-sg"
  description = "Wazuh Manager security group"
  vpc_id      = aws_vpc.wazuh_vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS from anywhere"
  }

  ingress {
    from_port   = 1514
    to_port     = 1514
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Wazuh agent syslog/TCP"
  }

  ingress {
    from_port   = 1515
    to_port     = 1515
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Wazuh cluster communication"
  }

  ingress {
    from_port   = 55000
    to_port     = 55000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Wazuh agent registration"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
    description = "SSH access"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name      = "wazuh-sg"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_security_group" "victim_sg" {
  name        = "victim-sg"
  description = "Victim instance security group"
  vpc_id      = aws_vpc.wazuh_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access for testing"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP app traffic"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name      = "victim-sg"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_security_group" "jail_sg" {
  name        = "jail-sg"
  description = "Jail security group for isolated instances"
  vpc_id      = aws_vpc.wazuh_vpc.id

  ingress = []

  egress = []

  tags = {
    Name      = "jail-sg"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}
