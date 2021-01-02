import click
from ec2_manager import EC2_Manager
import logging
import time

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
    ec2 = EC2_Manager()

    # find latest ami
    amis = ec2.get_images()
    # print(amis)
    ami_id = sorted([ami for ami in amis if AMI_PREFIX in ami['Name']], key=lambda x:x['Name'],
                    reverse=True)[0]['ImageId']
    logger.info(f"Latest AMI ID: {ami_id}")

    instance_id = ec2.create_spot_instance(ami_id, wait=True)
    logger.info(f"Instance has created: {instance_id}")

@cmd.command()
def get_info():
    ec2 = EC2_Manager()

    instance_id = ec2.get_instance_id()
    print(instance_id)
    instance_status = ec2.get_instance_status(instance_id)
    logger.info(f"Instance status {instance_status}")

    if instance_status in ['pending', 'running']:
        instance = ec2.ec2r.Instance(instance_id)

        logger.info(f"Instance dns: {instance.public_dns_name}")
        logger.info(f"Instance ip: {instance.public_ip_address}")

@cmd.command()
def stop():
    ec2 = EC2_Manager()

    instance_id = ec2.get_instance_id()
    instance_status = ec2.get_instance_status(instance_id)
    logger.info(f"Instance status {instance_status}")

    if instance_status in ['pending', 'running']:
        logger.info(f"Create AMI for {instance_id}")
        unix_time = int(time.time())
        res = ec2.create_ami(instance_id, f"{AMI_PREFIX}_{unix_time}", wait=True)

    request_id = ec2.get_active_request_id()
    if request_id is not None:
        logger.info(f"Stoping request: {request_id}")
        ec2.cancel_spot_fleet_request(request_id)

if __name__ == "__main__":
    cmd()
