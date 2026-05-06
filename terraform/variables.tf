variable "aws_region" {
  type    = string
  default = "eu-north-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "management_private_subnet_cidr" {
  type    = string
  default = "10.0.1.0/24"
}

variable "production_private_subnet_cidr" {
  type    = string
  default = "10.0.2.0/24"
}

variable "nat_public_subnet_cidr" {
  type    = string
  default = "10.0.3.0/24"
}

variable "instance_type" {
  type    = string
  default = "t3.large"
}

variable "wazuh_key_name" {
  type        = string
  description = "Existing EC2 key pair name for SSH access"
  default     = ""
}

variable "allowed_ssh_cidr" {
  type    = string
  default = "0.0.0.0/0"
}

variable "prevent_destroy" {
  type        = bool
  description = "If true, resources are protected from destroy (use with caution)."
  default     = false
}

variable "ecr_victim_repository_name" {
  type        = string
  description = "ECR repository name for the victim image."
  default     = "cloud-soc-victim"
}

variable "ecr_manager_repository_name" {
  type        = string
  description = "ECR repository name for the Wazuh manager image."
  default     = "cloud-soc-wazuh-manager"
}
