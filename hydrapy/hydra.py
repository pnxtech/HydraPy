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
            self._message['mid'] = message.mid
        else:
            self._message['mid'] = self.create_message_id()

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
            self._message['timestamp'] = self.get_time_stamp()

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
    _service_ip = '0.0.0.0'
    _service_description = ''
    _instance_id = None
    _hydra_event_count = 0

    def __init__(self, redis, config, service_version):
        self._redis = redis
        self._config = config
        entry = self._config['hydra']
        self._service_version = service_version
        self._service_name = entry['serviceName']
        self._service_port = entry['servicePort']
        self._service_description = entry['serviceDescription']
        self._service_type = entry['serviceType']
        self._redis_database = entry['redis']['database']

    async def _presence_event(self):
        umf = UMFMessage()
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
        pp(f'{self._redis_pre_key}:{self._service_name}:service')
        entry['updatedOn'] = umf.get_time_stamp()
        tr = self._redis.multi_exec()
        f1 = tr.setex(f'{self._redis_pre_key}:{self._service_name}:{self._instance_id}:presence',
                      self._KEY_EXPIRATION_TTL,
                      self._instance_id)
        f2 = tr.hset(f'{self._redis_pre_key}:nodes',
                     self._instance_id, json.dumps(entry))
        await tr.execute()
        await asyncio.gather(f1, f2)

    async def _health_check_event(self):
        pp(f'{self._redis_pre_key}:{self._service_name}:{self._instance_id}:health')

    async def _hydra_events(self):
        await self._presence_event()
        self._hydra_event_count = self._hydra_event_count + 1
        if self._hydra_event_count % self._HEALTH_UPDATE_INTERVAL == 0:
            self._hydra_event_count = 0
            await self._health_check_event()

    async def init(self):
        self._instance_id = uuid.uuid4().hex
        p = Periodic(self._PRESENCE_UPDATE_INTERVAL, self._hydra_events)
        await p.start()
