import asyncio
import aioredis
import json

from quart import Quart
from quart.logging import create_serving_logger
from hypercorn.config import Config
from hypercorn.asyncio import serve

from hydra import HydraPy
from hydra import hydra_route

from pprint import pp

app = Quart(__name__)

hydra_route('/', ['GET'])
@app.route('/', methods=['GET'])
async def home():
    return 'HydraPy Sample Service'

async def startQuart(si):
    config = Config()
    config.bind = [f"{si['serviceIP']}:{si['servicePort']}"]
    config.access_log_format = '%(h)s %(r)s %(s)s %(b)s %(D)s'
    config.accesslog = create_serving_logger()
    config.errorlog = config.accesslog
    loop = asyncio.get_event_loop()
    await loop.create_task(serve(app, config))

async def main():
    with open('./config.json', 'r', encoding='utf-8-sig') as json_file:
        hydra_config = json.load(json_file)

    redis_entry = hydra_config['hydra']['redis']
    redis_url = f"redis://{redis_entry['host']}:{redis_entry['port']}/{redis_entry['database']}"
    redis = await aioredis.create_redis_pool(redis_url, encoding='utf-8')

    hydra = HydraPy(redis, hydra_config)
    await hydra.init()

    si = hydra.get_service_info()

    hydra_route('/v1/sample/health', ['GET'])
    @app.route('/v1/sample/health', methods=['GET'])
    async def health():
        return {
            'result': hydra.get_health()
        }

    hydra_route('/v1/sample/version', ['GET'])
    @app.route('/v1/sample/version', methods=['GET'])
    async def version():
        return {
            'result': {
                'version': si['serviceVersion']
            }
        }

    await hydra.register_routes()

    async def message_handler(message):
        pp(message)

    await hydra.register_message_handler(message_handler)

    print(f"{si['serviceName']}({si['instanceID']})(v{si['serviceVersion']}) running at {si['serviceIP']}:{si['servicePort']}")
    await startQuart(si)

    redis.close()
    await redis.wait_closed()

asyncio.run(main())
