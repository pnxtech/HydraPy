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

import aioredis
import asyncio
import json
import os
import time
import platform
import psutil
import random
import re
import shortuuid
import socket
import uuid

from datetime import datetime
from pprint import pp
from periodic import Periodic


class UMF_Message:
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

    def create_message(self, message):
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
            self._message['mid'] = UMF_Message.create_message_id()

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
            self._message['timestamp'] = UMF_Message.get_time_stamp()

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

    def parse_route(to_value):
        service_name = ''
        http_method = ''
        api_route = ''
        error = ''
        instance = ''
        sub_id = ''
        segments = to_value.split(':')
        if len(segments) < 2:
            error = 'route field has invalid number of routable segments'
        else:
            sub_segments = segments[0].split('@')
            if len(sub_segments) == 1:
                service_name = segments[0]
            else:
                sub_id = sub_segments[0].split('-')
                l = len(sub_id)
                if l < 0:
                    sub_id = sub_id[0]
                elif l > 1:
                    instance = sub_id[0]
                    sub_id = sub_id[1]
                else:
                    instance = sub_id[0]
                    sub_id = ''
        x = re.search(r'\[(.*?)\]', segments[1])
        if x and x.group(1):
            http_method = x.group(1)
            segments[1] = segments[1].replace(f'[{http_method}]', '')
        api_route = segments[1]
        return {
            'instance': instance,
            'sub_id': sub_id,
            'service_name': service_name,
            'http_method': http_method,
            'api_route': api_route,
            'error': error
        }

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

    INFO = 'info'
    DEBUG = 'debug'
    WARN = 'warn'
    ERROR = 'error'
    FATAL = 'fatal'
    TRACE = 'trace'

    def __init__(self, config_path, version, message_handler):
        if message_handler:
            self._message_handler = message_handler

        with open(config_path, 'r', encoding='utf-8-sig') as json_file:
            self._config = json.load(json_file)

        if version:
            self._config['hydra']['serviceVersion'] = version

        entry = self._config['hydra']
        if 'serviceVersion' in entry:
            self._service_version = entry['serviceVersion']
        else:
            self._service_version = '0.0.0'
        self._service_name = entry['serviceName']

        if 'serviceDNS' in entry and entry['serviceDNS'] != '':
            entry['serviceIP'] = entry['serviceDNS']
            self._service_ip = entry['serviceDNS']
        else:
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
            'sampledOn': UMF_Message.get_time_stamp(),
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

    async def send_message(self, umf_message):
        parsed_route = UMF_Message.parse_route(umf_message['to'])
        instances_list = await self.get_presence(parsed_route['service_name'])
        instance = None
        if len(instances_list):
            if parsed_route['instance'] != '':
                instance = parsed_route['instance']
                #TODO: loop through instances_list to confirm instance ID is present
            else:
                instance = instances_list[0]['instanceID']
            await self._redis.publish(f"{self._mc_message_key}:{parsed_route['service_name']}:{instance}", json.dumps(umf_message))

    async def send_broadcast_message(self, umf_message):
        parsed_route = UMF_Message.parse_route(umf_message['to'])
        key = f"{self._mc_message_key}:{parsed_route['service_name']}"
        await self._redis.publish(key, json.dumps(umf_message))

    async def get_presence(self, service_name):
        instance_list = []
        ids = []
        cur = b'0'
        while cur:
            cur, keys = await self._redis.scan(cur, match=f'*:{service_name}:*:presence')
            ids.append(keys)
        trans=[]
        tr = self._redis.multi_exec()
        pp(ids)
        for entries in ids:
            for entry in entries:
                if len(entry) != 0:
                    pp(entry)
                    instance_id = entry.split(':')[3]
                    trans.append(tr.hget(f'{self._redis_pre_key}:nodes', instance_id))
        await tr.execute()
        results = []
        raw_results = await asyncio.gather(*trans)
        for item in raw_results:
            obj = json.loads(item)
            timestamp = obj['updatedOn'].replace('z', '+0000')
            obj['updatedOnTS'] = int(time.mktime(time.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')))
            results.append(obj)
        return random.sample(results, len(results))

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

        msg = (UMF_Message()).create_message({
            'to': 'hydra-router:/refresh',
            'from': f'{self._service_name}:/',
            'body': {
                'action': 'refresh',
                'serviceName': self._service_name
            }
        })
        await self._redis.publish(f'{self._mc_message_key}:hydra-router', json.dumps(msg))

    async def register_message_handler(self, message_handler):
        self._message_handler = message_handler

    async def _register_service(self):
        service_entry = {
            'serviceName': self._service_name,
            'type': self._service_type,
            'registeredOn': UMF_Message.get_time_stamp()
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
                    msg = (UMF_Message()).create_message(msg)
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
        entry['updatedOn'] = UMF_Message.get_time_stamp()
        tr = self._redis.multi_exec()
        f1 = tr.setex(f'{self._redis_pre_key}:{self._service_name}:{self._instance_id}:presence',
                      self._KEY_EXPIRATION_TTL,
                      self._instance_id)
        f2 = tr.hset(f'{self._redis_pre_key}:nodes',
                     self._instance_id, json.dumps(entry))
        await tr.execute()
        await asyncio.gather(f1, f2)

    async def log(self, severity, entry, text=None):
        new_entry = {
            'serviceName': self._service_name,
            'version': self._service_version,
            'instanceID': self._instance_id,
            'severity': severity,
            'bdy': {}
        }
        if text:
            new_entry['message'] = text
        if entry:
            new_entry['bdy'] = entry
        await self.send_broadcast_message((UMF_Message()).create_message({
            'to': 'hydra-logging-svcs:/',
            'from': f'{self._service_name}:/',
            'body': new_entry
        }))

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

        redis_entry = self._config['hydra']['redis']
        redis_url = f"redis://{redis_entry['host']}:{redis_entry['port']}/{redis_entry['database']}"
        self._redis = await aioredis.create_redis_pool(redis_url, encoding='utf-8')

        await self._register_service()
        p = Periodic(self._PRESENCE_UPDATE_INTERVAL, self._hydra_events)
        await p.start()

        # TODO: determine best way to close
        # self._redis.close()
        # await self._redis.wait_closed()

        return self.get_service_info()
