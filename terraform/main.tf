terraform {
    required_version = ">= 1.0"
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
}

provider "aws" {
    region = var.aws_region
}


output "aws_region" {
    description = "AWS region where resources are deployed"
    value       = var.aws_region
}

