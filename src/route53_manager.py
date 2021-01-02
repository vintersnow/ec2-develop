import boto3
import datetime
import re
from pprint import pprint

class Route53Manager:
    _client_name = 'route53'
    _session = None
    _hosted_zone_name = None
    # _resource = None

    def __init__(self, profile_name):
        self._session = boto3.Session(profile_name=profile_name)

    @property
    def session(self):
        return self._session

    def get_client(self, client_name=None):
        if not client_name:
            client_name = self._client_name
        return self.session.client(client_name)

    @property
    def client_name(self):
        return self._client_name

    @property
    def resource(self):
        return self._resource

    @property
    def hosted_zone_name(self):
        return self._hosted_zone_name

    def create_hosted_zone(self):
        params = {
            'Name': self.hosted_zone_name,
            'CallerReference': str(datetime.datetime.now().timestamp()),
        }
        return self.get_client().create_hosted_zone(**params)

    def get_hosted_zone(self, host_zone_id):
        return self.get_client().get_hosted_zone(Id=host_zone_id)

    def create_record_set(self, host, name, ip):
        params = {
            'HostedZoneId': host['HostedZone']['Id'],
            'ChangeBatch': {
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': name,
                            'Type': 'A',
                            'TTL': 3600,
                            'ResourceRecords': [
                                {
                                    'Value': ip
                                }
                            ]
                        }
                    }
                ]
            }
        }
        return self.get_client().change_resource_record_sets(**params)

    def set_hosted_zone_name(self, hosted_zone_name):
        self._hosted_zone_name = hosted_zone_name

    # def set_resource(self, resource):
    #     self._resource = resource
