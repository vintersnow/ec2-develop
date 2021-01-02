import click
from ec2_manager import EC2Manager
from route53_manager import Route53Manager
import logging
import time
import subprocess

AMI_PREFIX='dev_ami'

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - [%(levelname)s] %(message)s',
    )
logger = logging.getLogger()

@click.group()
def cmd():
    pass

@cmd.command()
def start():
    ec2 = EC2Manager()
    dns = Route53Manager('default')

    # find latest ami
    amis = ec2.get_images()
    # print(amis)
    ami_id = sorted([ami for ami in amis if AMI_PREFIX in ami['Name']], key=lambda x:x['Name'],
                    reverse=True)[0]['ImageId']
    logger.info(f"Latest AMI ID: {ami_id}")

    instance_id = ec2.create_spot_instance(ami_id, wait=True)
    logger.info(f"Instance has created: {instance_id}")

    instance = ec2.ec2r.Instance(instance_id)
    logger.info(f"Instance dns: {instance.public_dns_name}")
    logger.info(f"Instance ip: {instance.public_ip_address}")

    host_zone_id = 'Z095484231BSVD296Q76I'
    host = dns.get_hosted_zone(host_zone_id)
    record = dns.create_record_set(host, 'dev1.vintersnow.ml', instance.public_ip_address)
    logger.info(f"Instance has created: {instance_id}")

    # attach volume
    volume_id = 'vol-088f7aec44dcfd9e5'
    device = '/dev/sdf'
    logger.info(f"Attach volume: {volume_id}")
    instance_id = ec2.get_instance_id()
    while ec2.get_instance_status(instance_id) != 'running':
        time.sleep(10)
    ec2.attach_volume(instance_id, volume_id, device)


@cmd.command()
def get_info():
    ec2 = EC2Manager()

    instance_id = ec2.get_instance_id()
    print(instance_id)
    instance_status = ec2.get_instance_status(instance_id)
    logger.info(f"Instance status {instance_status}")

    if instance_status in ['pending', 'running']:
        instance = ec2.ec2r.Instance(instance_id)

        logger.info(f"Instance dns: {instance.public_dns_name}")
        logger.info(f"Instance ip: {instance.public_ip_address}")

@cmd.command()
@click.option('--skip-save', is_flag=True)
def stop(skip_save):
    ec2 = EC2Manager()

    instance_id = ec2.get_instance_id()
    instance_status = ec2.get_instance_status(instance_id)
    logger.info(f"Instance status {instance_status}")

    if instance_status in ['pending', 'running'] and not skip_save:

        volume_id = 'vol-088f7aec44dcfd9e5'
        device = '/dev/sdf'
        logger.info(f"Detach volume {volume_id}")
        ec2.detach_volume(instance_id, volume_id, device, wait=True)
        input()

        logger.info(f"Create AMI for {instance_id}")
        unix_time = int(time.time())
        res = ec2.create_ami(instance_id, f"{AMI_PREFIX}_{unix_time}", wait=True)

    request_id = ec2.get_active_request_id()
    if request_id is not None:
        logger.info(f"Stoping request: {request_id}")
        ec2.cancel_spot_fleet_request(request_id)

@cmd.command()
@click.option('--key_path', default='~/.ssh/keys/aws')
@click.option('--user_name', default='vinter')
def connect(key_path, user_name):
    ec2 = EC2Manager()

    instance_id = ec2.get_instance_id()
    ipv4 = ec2.ec2r.Instance(instance_id).public_ip_address

    cmd = [
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-i",
        key_path,
        f"{user_name}@{ipv4}",
        "-L",
        "8000:localhost:8000",
        "-L",
        "8080:localhost:8080",
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    cmd()
