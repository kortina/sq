- [ ] build pg docker container on aws
  - [ ] use EBS as persistent state
  - [ ] only port 22 open to web
  - [ ] sq command to connect to this docker container in a bash shell
  - [ ] backups
- [ ] sq command to forward aws pg to local port via ssh
- [ ] s3 bucket in us-west-1
- [ ] define project directory / bin structure (new project command)
- [ ] s3 rsync scripts

Cluster Resources
Instance typet2.micro
Desired number of instances1
Key pairsq_aws
ECS AMI IDami-0b95d46a7f7393cfa
VPC vpc-08ecdd9d68981bee5
Subnet 1subnet-01c1d06ee4451e7ff
Subnet 1 route table associationrtbassoc-0d04cc4a2a47010da
Subnet 2subnet-082e323ce59d549e3
Subnet 2 route table associationrtbassoc-0a62f9adf8b403ba4
VPC Availability Zonesus-west-1a, us-west-1b
Security groupsg-0176e8021bec0c6b4
Internet gatewayigw-0803f93bfcb0b3158
Route tablertb-006b1040443ad832a
Amazon EC2 routeEC2Co-Publi-1AW1X0RHCXAZW
Virtual private gateway attachmentEC2Co-Attac-RR5D8PN88WDU
Launch configurationEC2ContainerService-sq-EcsInstanceLc-1CM7WE9CWHJCC
Auto Scaling groupEC2ContainerService-sq-EcsInstanceAsg-18YFD43EPILLE

efs-for-ecs
file system id: fs-e7507afe
