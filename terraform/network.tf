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

resource "aws_subnet" "management_private" {
  vpc_id                  = aws_vpc.wazuh_vpc.id
  cidr_block              = var.management_private_subnet_cidr
  map_public_ip_on_launch = false

  tags = {
    Name      = "wazuh-management-private-subnet"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_subnet" "production_private" {
  vpc_id                  = aws_vpc.wazuh_vpc.id
  cidr_block              = var.production_private_subnet_cidr
  map_public_ip_on_launch = false

  tags = {
    Name      = "wazuh-production-private-subnet"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_subnet" "nat_public" {
  vpc_id                  = aws_vpc.wazuh_vpc.id
  cidr_block              = var.nat_public_subnet_cidr
  map_public_ip_on_launch = true

  tags = {
    Name      = "wazuh-nat-public-subnet"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name      = "wazuh-nat-eip"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.nat_public.id

  tags = {
    Name      = "wazuh-nat-gateway"
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

resource "aws_route_table_association" "nat_public" {
  subnet_id      = aws_subnet.nat_public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.wazuh_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = {
    Name      = "wazuh-private-rt"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_route_table_association" "management_private" {
  subnet_id      = aws_subnet.management_private.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "production_private" {
  subnet_id      = aws_subnet.production_private.id
  route_table_id = aws_route_table.private.id
}
