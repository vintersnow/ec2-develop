import boto3
import datetime
import botocore
import logging
import sys
import json
import os
import time

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - [%(levelname)s] %(message)s',
    )
logger = logging.getLogger()

TMP_FILE='/tmp/aws_actives'

class EC2Manager(object):

    """Docstring for EC2_Manager. """

    def __new__(cls, *args, **kargs):
        """Singleton pattern"""
        if not hasattr(cls, "_instance"):
            cls._instance = super(EC2Manager, cls).__new__(cls)
        return cls._instance

    def __init__(self, local_file_name='/tmp/aws_actives.json'):
        """TODO: to be defined.

        :Docstring for EC2_Manager.: TODO

        """
        self.ec2 = boto3.client('ec2')
        self.ec2r = boto3.resource('ec2')

        # self._Docstring for EC2_Manager. = Docstring for EC2_Manager.
        self.local_file_name = local_file_name
        if not os.path.exists(self.local_file_name):
            with open(self.local_file_name, "w") as f:
                f.write("{}")
        with open(self.local_file_name, 'r') as f:
            self.local_data = json.load(f)

    def save_local_file(self):
        with open(self.local_file_name, 'w') as f:
            json.dump(self.local_data, f)

    def create_ami(self, instance_id, ami_name, wait=False):
        logger.info(f'create ami image from {instance_id}')
        res = self.ec2.create_image(InstanceId=instance_id, Name=ami_name)
        if wait:
            waiter = self.ec2.get_waiter('image_available')
            waiter.wait(ImageIds=[res['ImageId']])
        return res

    def get_images(self):
        res = self.ec2.describe_images(Owners=['self'])
        return res['Images']

    def get_image(self, image_id):
        res = self.ec2.describe_images(Owners=['self'], ImageIds=[image_id])
        return res['Images'][0]

    def delete_instance(self, instance_id):
        res = self.ec2.terminate_instances(InstanceIds=[instance_id])
        return res

    def get_instance_status(self, instance_id):
        # instance = self.ec2r.Instance(instance_id)
        instance_iterator = self.ec2r.instances.all()

        for instance in instance_iterator:
            if instance.instance_id == instance_id:
                return instance.state['Name']
        return None

    def request_spot_instance(self, image_id, request_template='spot_fleet_config.json'):
        with open(request_template) as f:
            config = json.load(f)

        image = self.get_image(image_id)
        def modify(req):
            req['ImageId'] = image_id
            req['BlockDeviceMappings'] = image['BlockDeviceMappings']
            return req

        config['LaunchSpecifications'] = [modify(sf) for sf in config['LaunchSpecifications']]

        try:
            request = self.ec2.request_spot_fleet(SpotFleetRequestConfig=config)
        except botocore.exceptions.ParamValidationError as err:
            logger.fatal('Bad parameters provided, cannot continue: %s', err)
            sys.exit(-3)
        except botocore.exceptions.ClientError as err:
            logger.fatal('Failed to request spot fleet, cannot continue: %s', err)
            sys.exit(-4)

        logger.info('Spot fleet requested! Reference is %s', request['SpotFleetRequestId'])
        return request

    def cancel_spot_fleet_request(self, request_id):
        return self.ec2.cancel_spot_fleet_requests(SpotFleetRequestIds=[request_id], TerminateInstances=True)

    def create_spot_instance(self, image_id, request_template='spot_fleet_config.json', wait=False):
        # logger.info()
        res = self.request_spot_instance(image_id, request_template)
        request_id = res['SpotFleetRequestId']
        self.local_data['spot_fleet_request_id'] = request_id
        self.save_local_file()

        logger.info("Wait for request to be fulfilled...")
        # waiter = self.ec2.get_waiter('spot_fleet_request_fulfilled')
        # waiter.wait(SpotInstanceRequestIds=[request_id])
        # logger.info('Wait for ec2 instance to boot up...')

        while True:
            res = self.ec2.describe_spot_fleet_instances(SpotFleetRequestId=request_id)
            if len(res['ActiveInstances']) > 0:
                break
            time.sleep(10)
            # print(res)
        instance_id = res['ActiveInstances'][0]['InstanceId']
        self.local_data['active_instance_id'] = instance_id
        self.save_local_file()

        if wait:
            while self.get_instance_status(instance_id) == 'running':
                pass

        return instance_id

    def get_active_request_id(self):
        if 'spot_fleet_request_id' in self.local_data:
            return self.local_data['spot_fleet_request_id']
        return None

    def get_instance_id(self):
        if 'active_instance_id' in self.local_data:
            return self.local_data['active_instance_id']
        return None
