import os
import socket
import asyncio
import json
import uuid
import shortuuid
from datetime import datetime
from pprint import pp
from periodic import Periodic


class UMFMessage:
    UMF_VERSION = 'UMF/1.4.6'
    message = None

    def __init__(self):
        self.message = {}

    def get_time_stamp(self):
        '''retrieve an ISO 8601 timestamp'''
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def create_message_id(self):
        '''Returns a UUID for use with messages'''
        return uuid.uuid4().hex

    def create_short_message_id(self):
        '''Returns a short form UUID for use with messages'''
        return shortuuid.uuid()

    def to_json(self):
        '''A JSON stringifiable version of message'''
        return self.message

    def to_short(self):
        '''convert a long message to a short one'''
        message = {}
        if 'to' in self.message:
            message['to'] = self.message['to']
        if 'from' in self.message:
            message['frm'] = self.message['from']
        if 'headers' in self.message:
            message['hdr'] = self.message['headers']
        if 'mid' in self.message:
            message['mid'] = self.message['mid']
        if 'rmid' in self.message:
            message['rmid'] = self.message['rmid']
        if 'signature' in self.message:
            message['sig'] = self.message['signature']
        if 'timeout' in self.message:
            message['tmo'] = self.message['timeout']
        if 'timestamp' in self.message:
            message['ts'] = self.message['timestamp']
        if 'type' in self.message:
            message['typ'] = self.message['type']
        if 'version' in self.message:
            message['ver'] = self.message['version']
        if 'via' in self.message:
            message['via'] = self.message['via']
        if 'forward' in self.message:
            message['fwd'] = self.message['forward']
        if 'body' in self.message:
            message['bdy'] = self.message['body']
        if 'authorization' in self.message:
            message['aut'] = self.message['authorization']
        return message

    def createMessage(self, message):
        '''Create a UMF message'''
        if 'to' in message:
            self.message['to'] = message['to']

        if 'from' in message:
            self.message['from'] = message['from']
        if 'frm' in message:
            self.message['from'] = message['frm']

        if 'headers' in message:
            self.message['headers'] = message['headers']
        if 'hdr' in message:
            self.message['headers'] = message['hdr']

        if 'mid' in message:
            self.message['mid'] = message.mid
        else:
            self.message['mid'] = self.create_message_id()

        if 'rmid' in message:
            self.message['rmid'] = message['rmid']

        if 'signature' in message:
            self.message['signature'] = message['signature']
        if 'sig' in message:
            self.message['signature'] = message['sig']

        if 'timout' in message:
            self.message['timeout'] = message['timeout']
        if 'tmo' in message:
            self.message['timeout'] = message['tmo']

        if 'timestamp' in message:
            self.message['timestamp'] = message['timestamp']
        elif 'ts' in message:
            self.message['timestamp'] = message['ts']
        else:
            self.message['timestamp'] = self.get_time_stamp()

        if 'type' in message:
            self.message['type'] = message['type']
        if 'typ' in message:
            self.message['type'] = message['typ']

        if 'version' in message:
            self.message['version'] = message['version']
        elif 'ver' in message:
            self.message['version'] = message['ver']
        else:
            self.message['version'] = self.UMF_VERSION

        if 'via' in message:
            self.message['via'] = message['via']

        if 'forward' in message:
            self.message['forward'] = message['forward']
        if 'fwd' in message:
            self.message['forward'] = message['fwd']

        if 'body' in message:
            self.message['body'] = message['body']
        if 'bdy' in message:
            self.message['body'] = message['bdy']

        if 'authorization' in message:
            self.message['authorization'] = message['authorization']
        if 'aut' in message:
            self.message['authorization'] = message['aut']

        return self.message


class Hydra:
    ONE_SECOND = 1
    ONE_WEEK_IN_SECONDS = 604800
    PRESENCE_UPDATE_INTERVAL = ONE_SECOND
    HEALTH_UPDATE_INTERVAL = ONE_SECOND * 5
    KEY_EXPIRATION_TTL = ONE_SECOND * 3

    redis_pre_key = 'hydra:service'
    mc_message_key = 'hydra:service:mc'

    redis = None
    config = None
    service_version = ''
    service_name = ''
    service_port = 0
    service_ip = '0.0.0.0'
    service_description = ''
    instance_id = None
    hydra_event_count = 0

    def __init__(self, redis, config, service_version):
        self.redis = redis
        self.config = config
        entry = self.config['hydra']
        self.service_version = service_version
        self.service_name = entry['serviceName']
        self.service_port = entry['servicePort']
        self.service_description = entry['serviceDescription']
        self.service_type = entry['serviceType']
        self.redis_database = entry['redis']['database']

    async def presence_event(self):
        umf = UMFMessage()
        entry = {
            'serviceName': self.service_name,
            'serviceDescription': self.service_description,
            'version': self.service_version,
            'instanceID': self.instance_id,
            'processID': os.getpid(),
            'ip': self.service_ip,
            'port': self.service_port,
            'hostName': socket.gethostname()
        }
        pp(f'{self.redis_pre_key}:{self.service_name}:service')
        entry['updatedOn'] = umf.get_time_stamp()
        tr = self.redis.multi_exec()
        f1 = tr.setex(f'{self.redis_pre_key}:{self.service_name}:{self.instance_id}:presence',
                      self.KEY_EXPIRATION_TTL,
                      self.instance_id)
        f2 = tr.hset(f'{self.redis_pre_key}:nodes',
                     self.instance_id, json.dumps(entry))
        await tr.execute()
        await asyncio.gather(f1, f2)

    async def health_check_event(self):
        pp(f'{self.redis_pre_key}:{self.service_name}:{self.instance_id}:health')

    async def hydra_event_loop(self):
        await self.presence_event()
        self.hydra_event_count = self.hydra_event_count + 1
        if self.hydra_event_count % self.HEALTH_UPDATE_INTERVAL == 0:
            self.hydra_event_count = 0
            await self.health_check_event()

    async def init(self):
        self.instance_id = uuid.uuid4().hex
        p = Periodic(1, self.hydra_event_loop)
        await p.start()
