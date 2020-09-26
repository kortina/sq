provider "aws" {
  region = "us-west-1"
}

module "aws-client-vpn" {
  source = "./terraform-aws-client-vpn-endpoint"

  aws_access_key = var.access_key
  aws_secret_key = var.secret_key
  aws_region     = var.aws_region
  subnet_id      = var.subnet_id
  domain         = var.domain
}
