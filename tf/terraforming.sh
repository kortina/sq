#!/usr/bin/env bash
terraforming alb > alb.tf             # ALB
terraforming asg > asg.tf             # AutoScaling Group
terraforming cwa > cwa.tf             # CloudWatch Alarm
terraforming dbpg > dbpg.tf            # Database Parameter Group
terraforming dbsg > dbsg.tf            # Database Security Group
terraforming dbsn > dbsn.tf            # Database Subnet Group
terraforming ddb > ddb.tf             # DynamoDB
terraforming ec2 > ec2.tf             # EC2
terraforming ecc > ecc.tf             # ElastiCache Cluster
terraforming ecsn > ecsn.tf            # ElastiCache Subnet Group
terraforming efs > efs.tf             # EFS File System
terraforming eip > eip.tf             # EIP
terraforming elb > elb.tf             # ELB
terraforming iamg > iamg.tf            # IAM Group
terraforming iamgm > iamgm.tf           # IAM Group Membership
terraforming iamgp > iamgp.tf           # IAM Group Policy
terraforming iamip > iamip.tf           # IAM Instance Profile
terraforming iamp > iamp.tf            # IAM Policy
terraforming iampa > iampa.tf           # IAM Policy Attachment
terraforming iamr > iamr.tf            # IAM Role
terraforming iamrp > iamrp.tf           # IAM Role Policy
terraforming iamu > iamu.tf            # IAM User
terraforming iamup > iamup.tf           # IAM User Policy
terraforming igw > igw.tf             # Internet Gateway
terraforming kmsa > kmsa.tf            # KMS Key Alias
terraforming kmsk > kmsk.tf            # KMS Key
terraforming lc > lc.tf              # Launch Configuration
terraforming nacl > nacl.tf            # Network ACL
terraforming nat > nat.tf             # NAT Gateway
terraforming nif > nif.tf             # Network Interface
terraforming r53r > r53r.tf            # Route53 Record
terraforming r53z > r53z.tf            # Route53 Hosted Zone
terraforming rds > rds.tf             # RDS
terraforming rs > rs.tf              # Redshift
terraforming rt > rt.tf              # Route Table
terraforming rta > rta.tf             # Route Table Association
terraforming s3 > s3.tf              # S3
terraforming sg > sg.tf              # Security Group
terraforming sn > sn.tf              # Subnet
terraforming snst > snst.tf            # SNS Topic
terraforming snss > snss.tf            # SNS Subscription
terraforming sqs > sqs.tf             # SQS
terraforming vgw > vgw.tf             # VPN Gateway
terraforming vpc > vpc.tf             # VPC
