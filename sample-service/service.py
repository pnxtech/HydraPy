import asyncio
import aioredis
import json

from pprint import pp
from flask import Flask, request, jsonify, make_response
from hydra import Hydra

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

    redis = await aioredis.create_redis(config['hydra']['redis']['url'], encoding='utf-8')

    hydra = Hydra(redis, config, service_version)

    app.run(debug=True,
            host=config['hydra']['serviceIP'] != '' or '0.0.0.0',
            port=config['hydra']['servicePort'])

    redis.close()
    await redis.wait_closed()

asyncio.run(main())
