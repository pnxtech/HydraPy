# MIT License
# Copyright (c) 2020 Carlos Justiniano, and Contributors
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import time
import platform
import psutil
import socket
import asyncio
import json
import uuid
import shortuuid

from datetime import datetime
from pprint import pp
from periodic import Periodic


class UMFMessage:
    _UMF_VERSION = 'UMF/1.4.6'
    _message = None

    def __init__(self):
        self._message = {}

    def get_time_stamp():
        '''retrieve an ISO 8601 timestamp'''
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def create_message_id():
        '''Returns a UUID for use with messages'''
        return uuid.uuid4().hex

    def create_short_message_id():
        '''Returns a short form UUID for use with messages'''
        return shortuuid.uuid()

    def to_json(self):
        '''A JSON stringifiable version of message'''
        return self._message

    def to_short(self):
        '''convert a long message to a short one'''
        message = {}
        if 'to' in self._message:
            message['to'] = self._message['to']
        if 'from' in self._message:
            message['frm'] = self._message['from']
        if 'headers' in self._message:
            message['hdr'] = self._message['headers']
        if 'mid' in self._message:
            message['mid'] = self._message['mid']
        if 'rmid' in self._message:
            message['rmid'] = self._message['rmid']
        if 'signature' in self._message:
            message['sig'] = self._message['signature']
        if 'timeout' in self._message:
            message['tmo'] = self._message['timeout']
        if 'timestamp' in self._message:
            message['ts'] = self._message['timestamp']
        if 'type' in self._message:
            message['typ'] = self._message['type']
        if 'version' in self._message:
            message['ver'] = self._message['version']
        if 'via' in self._message:
            message['via'] = self._message['via']
        if 'forward' in self._message:
            message['fwd'] = self._message['forward']
        if 'body' in self._message:
            message['bdy'] = self._message['body']
        if 'authorization' in self._message:
            message['aut'] = self._message['authorization']
        return message

    def createMessage(self, message):
        '''Create a UMF message'''
        if 'to' in message:
            self._message['to'] = message['to']

        if 'from' in message:
            self._message['from'] = message['from']
        if 'frm' in message:
            self._message['from'] = message['frm']

        if 'headers' in message:
            self._message['headers'] = message['headers']
        if 'hdr' in message:
            self._message['headers'] = message['hdr']

        if 'mid' in message:
            self._message['mid'] = message['mid']
        else:
            self._message['mid'] = UMFMessage.create_message_id()

        if 'rmid' in message:
            self._message['rmid'] = message['rmid']

        if 'signature' in message:
            self._message['signature'] = message['signature']
        if 'sig' in message:
            self._message['signature'] = message['sig']

        if 'timout' in message:
            self._message['timeout'] = message['timeout']
        if 'tmo' in message:
            self._message['timeout'] = message['tmo']

        if 'timestamp' in message:
            self._message['timestamp'] = message['timestamp']
        elif 'ts' in message:
            self._message['timestamp'] = message['ts']
        else:
            self._message['timestamp'] = UMFMessage.get_time_stamp()

        if 'type' in message:
            self._message['type'] = message['type']
        if 'typ' in message:
            self._message['type'] = message['typ']

        if 'version' in message:
            self._message['version'] = message['version']
        elif 'ver' in message:
            self._message['version'] = message['ver']
        else:
            self._message['version'] = self._UMF_VERSION

        if 'via' in message:
            self._message['via'] = message['via']

        if 'forward' in message:
            self._message['forward'] = message['forward']
        if 'fwd' in message:
            self._message['forward'] = message['fwd']

        if 'body' in message:
            self._message['body'] = message['body']
        if 'bdy' in message:
            self._message['body'] = message['bdy']

        if 'authorization' in message:
            self._message['authorization'] = message['authorization']
        if 'aut' in message:
            self._message['authorization'] = message['aut']

        return self._message


_routes = []


def hydra_route(*args, **kwargs):
    _routes.append(args)


class HydraPy:
    _ONE_SECOND = 1
    _ONE_WEEK_IN_SECONDS = 604800
    _PRESENCE_UPDATE_INTERVAL = _ONE_SECOND
    _HEALTH_UPDATE_INTERVAL = _ONE_SECOND * 5
    _KEY_EXPIRATION_TTL = _ONE_SECOND * 3

    _redis_pre_key = 'hydra:service'
    _mc_message_key = 'hydra:service:mc'

    _redis = None
    _config = None
    _service_version = ''
    _service_name = ''
    _service_port = 0
    _service_ip = ''
    _service_description = ''
    _instance_id = None
    _hydra_event_count = 0
    _hydra_routes = []

    _message_handler = None

    def __init__(self, redis, config):
        self._redis = redis
        self._config = config
        entry = self._config['hydra']
        if 'serviceVersion' in entry:
            self._service_version = entry['serviceVersion']
        else:
            self._service_version = '0.0.0'
        self._service_name = entry['serviceName']

        # TODO: handle DNS names
        if entry['serviceIP'] != '':
            self._service_ip = entry['serviceIP']
        else:
            ip = socket.gethostbyname(socket.gethostname())
            self._service_ip = ip

        self._service_port = entry['servicePort']
        self._service_description = entry['serviceDescription']
        self._service_type = entry['serviceType']
        self._redis_database = entry['redis']['database']

    def get_service_name(self):
        return self._service_name

    def get_server_instance_id(self):
        return self._instance_id

    def get_service_port(self):
        return self._service_port

    def get_service_ip(self):
        return self._service_ip

    def get_service_version(self):
        return self._service_version

    def get_service_info(self):
        return {
            'serviceName': self._service_name,
            'servicePort': self._service_port,
            'serviceIP': self._service_ip,
            'instanceID': self._instance_id,
            'serviceVersion': self._service_version,
        }

    def get_health(self):
        pid = os.getpid()
        p = psutil.Process(pid)
        return {
            'serviceName': self._service_name,
            'instanceID': self._instance_id,
            'hostName': socket.gethostname(),
            'sampledOn': UMFMessage.get_time_stamp(),
            'processID': pid,
            'architecture': f'{platform.machine()}',
            'platform': f'{platform.system()}',
            'nodeVersion': f'{platform.python_implementation()} {platform.python_version()}',
            'memory': {
                'rss': p.memory_info()[0],
                'heapTotal': p.memory_info()[1],
                'heapUsed': '',
                'external': ''
            },
            'uptimeSeconds': time.time() - psutil.boot_time()
        }

    async def _flush_routes(self):
        await self._redis.delete(f'{self._redis_pre_key}:{self._service_name}:service:routes')

    async def register_routes(self):
        await self._flush_routes()
        key = f'{self._redis_pre_key}:{self._service_name}:service:routes'
        self._hydra_routes = [
            f'[get]/{self._service_name}',
            f'[get]/{self._service_name}/',
            f'[get]/{self._service_name}/:rest'
        ]
        for route in _routes:
            for method in route[1]:
                self._hydra_routes.append(f'[{method.lower()}]{route[0]}')
        tr = self._redis.multi_exec()
        for route in self._hydra_routes:
            tr.sadd(key, route)
        await tr.execute()

    async def register_message_handler(self, message_handler):
        self._message_handler = message_handler

    async def _register_service(self):
        service_entry = {
            'serviceName': self._service_name,
            'type': self._service_type,
            'registeredOn': UMFMessage.get_time_stamp()
        }
        tr = self._redis.multi_exec()
        f1 = tr.set(f'{self._redis_pre_key}:{self._service_name}:service',
                    json.dumps(service_entry))
        await tr.execute()
        await asyncio.gather(f1)

        async def _message_reader(channel):
            while (await channel.wait_message()):
                if self._message_handler:
                    msg = await channel.get_json()
                    msg = (UMFMessage()).createMessage(msg)
                    asyncio.ensure_future(self._message_handler(msg))

        ch1 = await self._redis.subscribe(f'{self._mc_message_key}:{self._service_name}')
        ch2 = await self._redis.subscribe(f'{self._mc_message_key}:{self._service_name}:{self._instance_id}')
        asyncio.ensure_future(_message_reader(ch1[0]))
        asyncio.ensure_future(_message_reader(ch2[0]))

        return {
            'serviceName': self._service_name,
            'serviceIP': self._service_ip,
            'servicePort': self._service_port
        }

    async def _presence_event(self):
        entry = {
            'serviceName': self._service_name,
            'serviceDescription': self._service_description,
            'version': self._service_version,
            'instanceID': self._instance_id,
            'processID': os.getpid(),
            'ip': self._service_ip,
            'port': self._service_port,
            'hostName': socket.gethostname()
        }
        entry['updatedOn'] = UMFMessage.get_time_stamp()
        tr = self._redis.multi_exec()
        f1 = tr.setex(f'{self._redis_pre_key}:{self._service_name}:{self._instance_id}:presence',
                      self._KEY_EXPIRATION_TTL,
                      self._instance_id)
        f2 = tr.hset(f'{self._redis_pre_key}:nodes',
                     self._instance_id, json.dumps(entry))
        await tr.execute()
        await asyncio.gather(f1, f2)

    async def _health_check_event(self):
        tr = self._redis.multi_exec()
        f1 = tr.setex(f'{self._redis_pre_key}:{self._service_name}:{self._instance_id}:health',
                      self._KEY_EXPIRATION_TTL,
                      json.dumps(self.get_health()))
        f2 = tr.expire(f'{self._redis_pre_key}:{self._service_name}:{self._instance_id}:health:log',
                       self._ONE_WEEK_IN_SECONDS)
        await tr.execute()
        await asyncio.gather(f1, f2)

    async def _hydra_events(self):
        await self._presence_event()
        self._hydra_event_count = self._hydra_event_count + 1
        if self._hydra_event_count % self._HEALTH_UPDATE_INTERVAL == 0:
            self._hydra_event_count = 0
            await self._health_check_event()

    async def init(self):
        self._instance_id = uuid.uuid4().hex
        await self._register_service()
        p = Periodic(self._PRESENCE_UPDATE_INTERVAL, self._hydra_events)
        await p.start()