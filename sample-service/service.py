import asyncio
import nest_asyncio
import aioredis
import json

from pprint import pp
from flask import Flask, request, jsonify, make_response
from hydra import Hydra

'''
patch asyncio to allow for nested asyncio.run and run_until_complete calls
'''
nest_asyncio.apply()

app = Flask(__name__)
service_version = '1.0.0'


@app.route('/', methods=['GET'])
def home():
    return 'HydraPy Sample Service version ' + service_version


@app.route('/v1/hydrapy/version', methods=['GET'])
def version():
    return make_response(jsonify({"version": service_version}), 200)


async def main():
    with open('./config.json', 'r', encoding='utf-8-sig') as json_file:
        config = json.load(json_file)

    redis_entry = config['hydra']['redis']
    redis_url = f"redis://{redis_entry['host']}:{redis_entry['port']}/{redis_entry['database']}"
    redis = await aioredis.create_redis(redis_url, encoding='utf-8')

    hydra = Hydra(redis, config, service_version)
    await hydra.init()

    app.run(debug=True,
            host=config['hydra']['serviceIP'] != '' or '0.0.0.0',
            port=config['hydra']['servicePort'])

    redis.close()
    await redis.wait_closed()

asyncio.run(main())
