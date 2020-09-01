provider "aws" {
  version = "~> 2.44.0"
  region     = var.aws_region
}

data "aws_caller_identity" "current" {}

output "aws_account_id" {
  value = "${data.aws_caller_identity.current.account_id}"
}

locals {
  postgres_version = "xyz"
}

resource "aws_db_instance" "davinci16" {
  # (resource arguments)
}
