resource "aws_vpc" "wazuh_vpc" {
  cidr_block = var.vpc_cidr

  tags = {
    Name      = "wazuh-vpc"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.wazuh_vpc.id

  tags = {
    Name      = "wazuh-igw"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.wazuh_vpc.id
  cidr_block              = var.public_subnet_cidr
  map_public_ip_on_launch = true

  tags = {
    Name      = "wazuh-public-subnet"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.wazuh_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = {
    Name      = "wazuh-public-rt"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}
