variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  type    = string
  default = "10.0.1.0/24"
}

variable "instance_type" {
  type    = string
  default = "t3.large"
}

variable "wazuh_key_name" {
  type    = string
  description = "Existing EC2 key pair name for SSH access"
  default = ""
}

variable "allowed_ssh_cidr" {
  type    = string
  default = "0.0.0.0/0"
}
