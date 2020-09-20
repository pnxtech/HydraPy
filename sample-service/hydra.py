import asyncio
import nest_asyncio
import uuid
import shortuuid
from datetime import datetime
from pprint import pp

class UMFMessage:
    UMF_VERSION = 'UMF/1.4.6'
    message = None

    def __init__(self):
        self.message = {}

    def getTimeStamp(self):
        '''retrieve an ISO 8601 timestamp'''
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def createMessageID(self):
        '''Returns a UUID for use with messages'''
        return uuid.uuid4()

    def createShortMessageID(self):
        '''Returns a short form UUID for use with messages'''
        return shortuuid.uuid()

    def toJSON(self):
        '''A JSON stringifiable version of message'''
        return self.message

    def toShort(self):
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
            self.message['mid'] = self.createMessageID()

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
            self.message['timestamp'] = self.getTimeStamp()

        if 'type' in message:
            self.message['type'] = message['type']
        if 'typ' in message:
            self.message['type'] = message['typ']

        if 'version' in message:
            self.message['version'] = message['version']
        elif 'ver' in message:
            self.message['version']  = message['ver']
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
    redis = None
    config = None
    service_version = ''

    def __init__(self, redis, config, service_version):
        self.redis = redis
        self.config = config
        self.service_version = service_version

        umf = UMFMessage()
        message = umf.createMessage({
            'body': {
                'msg': 'hello there',
                'val': 12
            }
        })
        pp(message)

        shortMessage = umf.toShort()
        pp(shortMessage)

    async def hydra_event_loop(self):
        while True:
            print('periodic')
            await asyncio.sleep(2)

    async def init(self):
        loop = asyncio.get_event_loop()
        nest_asyncio.apply(loop)
        task = loop.create_task(self.hydra_event_loop())
        try:
            loop.run_until_complete(task)
        except asyncio.CancelledError:
            pass
