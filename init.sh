#!/bin/bash

set -x


export AWS_DEFAULT_REGION=ap-northeast-1

region=$1
hosted_zone_id=$2
domain=$3

instance_id=$(curl -s 169.254.169.254/latest/meta-data/instance-id)
ip=$(curl -s 169.254.169.254/latest/meta-data/public-ipv4)

if ! test -e /usr/bin/aws ; then
  curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "/tmp/awscli-bundle.zip"
  unzip /tmp/awscli-bundle.zip -d /tmp
  /tmp/awscli-bundle/install -i /usr/lib/aws -b /usr/bin/aws
fi

# register route53
curl https://raw.githubusercontent.com/vintersnow/ec2-develop/master/dyndns.tmpl -O
sed -e "s/{%IP%}/$ip/g;s/{%domain%}/$domain/g" dyndns.tmpl > change_resource_record_sets.json
aws route53 change-resource-record-sets --hosted-zone-id $hosted_zone_id --change-batch file:///home/ubuntu/change_resource_record_sets.json
