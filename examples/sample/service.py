import asyncio
from datetime import datetime
import json

from quart import Quart
from quart.logging import create_serving_logger
from hypercorn.config import Config
from hypercorn.asyncio import serve

from hydrapy import HydraPy, hydra_route, UMF_Message

app = Quart(__name__)
service_version = open('VERSION').read().rstrip()

hydra_route('/', ['GET'])
@app.route('/', methods=['GET'])
async def home():
    return 'HydraPy Sample Service'

hydra_route('/v1/sample/test/:param1/:param2', ['GET'])
@app.route('/v1/sample/test/<param1>/<param2>', methods=['GET'])
async def test(param1, param2):
    return {
        'result': {
            'param1': param1,
            'param2': param2
        }
    }

async def startQuart(si):
    print(f"{si['serviceName']}({si['instanceID']})(v{si['serviceVersion']}) running at {si['serviceIP']}:{si['servicePort']}")
    config = Config()
    config.bind = [f"{si['serviceIP']}:{si['servicePort']}"]
    # config.bind = [f"0.0.0.0:{si['servicePort']}"]
    config.access_log_format = '%(h)s %(r)s %(s)s %(b)s %(D)s'
    config.accesslog = create_serving_logger()
    config.errorlog = config.accesslog
    loop = asyncio.get_event_loop()
    await loop.create_task(serve(app, config))

async def main():
    async def hydra_message_handler(message):
        print(f'{json.dumps(message)}', flush=True)

    hydra = HydraPy(config_path='./config.json', version=service_version, message_handler=hydra_message_handler)
    si = await hydra.init()

    hydra_route('/v1/sample/health', ['GET'])
    @app.route('/v1/sample/health', methods=['GET'])
    async def health():
        return {
            'result': hydra.get_health()
        }

    hydra_route('/v1/sample/send', ['GET'])
    @app.route('/v1/sample/send', methods=['GET'])
    async def send_message():
        msg = (UMF_Message()).create_message({
            'to': 'message:/',
            'from': f"{si['serviceName']}:/",
            'body': {
            }
        })
        await hydra.send_message(msg)
        return {
            'result': {}
        }

    hydra_route('/v1/sample/send-bc', ['GET'])
    @app.route('/v1/sample/send-bc', methods=['GET'])
    async def send_broadcast_message():
        msg = (UMF_Message()).create_message({
            'to': 'message:/',
            'from': f"{si['serviceName']}:/",
            'body': {
            }
        })
        await hydra.send_broadcast_message(msg)
        return {
            'result': {}
        }

    await hydra.register_routes()
    await startQuart(si)


asyncio.run(main())
