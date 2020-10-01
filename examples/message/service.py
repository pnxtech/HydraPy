import asyncio

from quart import Quart
from quart.logging import create_serving_logger
from hypercorn.config import Config
from hypercorn.asyncio import serve

from hydrapy import HydraPy, hydra_route, UMF_Message

app = Quart(__name__)
service_version = open('VERSION').read().rstrip()

async def startQuart(si):
    print(f"{si['serviceName']}({si['instanceID']})(v{si['serviceVersion']}) running at {si['serviceIP']}:{si['servicePort']}")
    config = Config()
    config.bind = [f"{si['serviceIP']}:{si['servicePort']}"]
    config.access_log_format = '%(h)s %(r)s %(s)s %(b)s %(D)s'
    config.accesslog = create_serving_logger()
    config.errorlog = config.accesslog
    loop = asyncio.get_event_loop()
    await loop.create_task(serve(app, config))

async def main():
    async def hydra_message_handler(message):
        print(message)

    hydra = HydraPy(config_path='./config.json', version=service_version, message_handler=hydra_message_handler)
    si = await hydra.init()

    hydra_route('/v1/message/health', ['GET'])
    @app.route('/v1/message/health', methods=['GET'])
    async def health():
        return {
            'result': hydra.get_health()
        }

    hydra_route('/v1/message/send', ['GET'])
    @app.route('/v1/message/send', methods=['GET'])
    async def send():
        msg = (UMF_Message()).create_message({
            'to': 'sample:/',
            'from': f"{si['serviceName']}:/",
            'body': {
                'action': 'do-something',
                'data': 'data'
            }
        })
        await hydra.send_message(msg)
        return {
            'result': {}
        }
    await hydra.register_routes()
    await startQuart(si)


asyncio.run(main())
