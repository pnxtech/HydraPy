import uuid
import shortuuid
from datetime import datetime
from pprint import pp

class UMFMessage:
    UMF_VERSION = 'UMF/1.4.6'
    message = None

    def __init__(self):
        message = {}

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
        return message

    def toShort(self):
        '''convert a long message to a short one'''
        let message = {}
        if self.message['to']:
            message['to'] = self.message['to']
        if self.message['from']:
            message['frm'] = self.message['from']
        if self.message['headers']:
            message['hdr'] = self.message['headers']
        if self.message['mid']:
            message['mid'] = self.message['mid']
        if self.message['rmid']:
            message['rmid'] = self.message['rmid']
        if self.message['signature']:
            message['sig'] = self.message['signature']
        if self.message['timeout']:
            message['tmo'] = self.message['timeout']
        if self.message['timestamp']:
            message['ts'] = self.message['timestamp']
        if self.message['type']:
            message['typ'] = self.message['type']
        if self.message['version']:
            message['ver'] = self.message['version']
        if self.message['via']:
            message['via'] = self.message['via']
        if self.message['forward']:
            message['fwd'] = self.message['forward']
        if self.message['body']:
            message['bdy'] = self.message['body']
        if self.message['authorization']:
            message['aut'] = self.message['authorization']
        return message

    def createMessage(self, message):
        '''Create a UMF message'''
        if message['to']:
            self.message['to'] = message['to']
        if message['from'] or message['frm']:
            self.message['from'] = message['from'] or message['frm']
        if message['headers'] or message['hdr']:
            self.message['headers'] = message['headers'] or message['hdr']
        self.message['mid'] = message.mid or self.createMessageID()
        if message['rmid']:
            self.message['rmid'] = message['rmid']
        if message['signature'] or message['sig']:
            self.message['signature'] = message['signature'] or message['sig']
        if message['timout'] or message['tmo']:
            self.message['timeout'] = message['timeout'] or message['tmo']
        self.message['timestamp'] = message['timestamp'] or message['ts'] or self.getTimeStamp()
        if message['type'] or message['typ']:
            self.message['type'] = message['type'] or message['typ']
        self.message['version'] = message['version'] or message['ver'] or self.UMF_VERSION
        if message['via']:
            self.message['via'] = message['via]
        if message['forward'] or message['fwd']:
            self.message['forward'] = message['forward'] or message['fwd']
        if message['body'] or self.message['bdy']:
            self.message['body'] = message['body'] or self.message['bdy']
        if message['authorization'] or self.message['aut']:
            self.message['authorization'] = message['authorization'] or self.message['aut']
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
        message = umf.createMessage({})
        pp(message)
