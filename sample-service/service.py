import asyncio
import aioredis
import json
import os
import socket
from quart import Quart
from quart.logging import create_serving_logger
from hypercorn.config import Config
from hypercorn.asyncio import serve
from pprint import pp
from hydra import HydraPy

app = Quart(__name__)
service_version = '1.0.0'
routes = []

routes.append(('/', ['GET']))
@app.route('/', methods=['GET'])
async def home():
    return 'HydraPy Sample Service version ' + service_version

routes.append(('/v1/hydrapy/version', ['GET']))
@app.route('/v1/hydrapy/version', methods=['GET'])
async def version():
    return {'version': service_version}


async def main():
    with open('./config.json', 'r', encoding='utf-8-sig') as json_file:
        hydra_config = json.load(json_file)

    if hydra_config['hydra']['serviceIP'] != '':
        ip_addr = hydra_config['hydra']['serviceIP']
    else:
        ip_addr = socket.gethostbyname(socket.gethostname())

    config = Config()
    config.bind = [f"{ip_addr}:{hydra_config['hydra']['servicePort']}"]
    config.access_log_format = '%(h)s %(r)s %(s)s %(b)s %(D)s'
    config.accesslog = create_serving_logger()
    config.errorlog = config.accesslog

    redis_entry = hydra_config['hydra']['redis']
    redis_url = f"redis://{redis_entry['host']}:{redis_entry['port']}/{redis_entry['database']}"
    redis = await aioredis.create_redis(redis_url, encoding='utf-8')

    hydra = HydraPy(redis, hydra_config, service_version)
    await hydra.init()
    await hydra.register_routes(routes)

    routes.append(('/v1/hydrapy/health', ['GET']))
    @app.route('/v1/hydrapy/health', methods=['GET'])
    async def health():
        return hydra.get_health()

    loop = asyncio.get_event_loop()
    await loop.create_task(serve(app, config))

    redis.close()
    await redis.wait_closed()

asyncio.run(main())
