#!/bin/bash
# https://github.com/hashicorp/terraform/issues/2957#issuecomment-150613677
id="/home/ubuntu/.INSTANCE_ID"
test -e $id || curl -K http://169.254.169.254/latest/meta-data/instance-id -o $id
INSTANCE_ID=`cat $id`
# written by the userdata
volume_id=`cat /home/ubuntu/.EBS_VOLUME_ID`
lsblk_name="xvdf"
device_name="/dev/xvdf"
mount_point="/opt/ebs"

echo "-- NB: this script will fail if you dont have the AWS_ evn vars set. --"

# wait for ebs volume to be attached
while :
do
    # self-attach ebs volume
    aws --region us-east-1 ec2 attach-volume --volume-id $volume_id --instance-id $INSTANCE_ID --device $device_name

    if lsblk | grep $lsblk_name; then
        echo "attached"
        break
    else
        sleep 5
    fi
done

# create fs if needed
if sudo file -s $device_name | grep "$device_name: data"; then
    echo "creating fs"
    sudo mkfs -t xfs $device_name
fi

# mount it
test -e $mount_point || sudo mkdir $mount_point
sudo chown -R ubuntu:ubuntu $mount_point
grep -q "$mount_point" /etc/fstab || echo "$device_name       $mount_point   xfs    defaults,nofail  0 2" | sudo tee -a /etc/fstab
echo "mounting"
sudo mount -a
sudo chown -R ubuntu:ubuntu $mount_point