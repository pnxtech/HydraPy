# HydraPy
Hydra for Python

![](./assets/hydrapy-logo.png)

```diff
- NOTE THIS PROJECT IS IN VERY EARLY DEVELOPMENT
* HydraPy requires Python 3.7+ and aioredis==1.3.1 or greater
```

```diff
- If using this version with HydraRouter it's important to refresh hydra router after your test container is loaded.
- $ curl localhost:5353/v1/router/refresh
```

Hydra is an approach to building light-weight microservices by leveraging the awesome power of the Redis database platform.

HydraPy is a nextgen port of the NodeJS implementation of Hydra with a goal of offering the same level of ease of use to the Python community.  We hope this will empower data scientists to build containerized microservices for their AI/ML applications.

The Hydra approach was first presented at the [2006 EmpireNode conference](https://www.youtube.com/watch?v=j_yVf9Blcjo) in New York City where Hydra for NodeJS was open sourced.

The following describes the approach:

* [Building light-weight microservices using Redis](https://medium.com/hydramicroservices/building-light-weight-microservices-using-redis-dc5b3bca741
)
* [RedisConf 2018 presentation](https://www.youtube.com/watch?v=z25CPqJMFUk)

[![Building light-weight microservices using Redis](http://img.youtube.com/vi/z25CPqJMFUk/0.jpg)](https://www.youtube.com/watch?v=z25CPqJMFUk "Building light-weight microservices using Redis")

---

## Usage

#### Import

```python
from hydrapy import HydraPy, hydra_route, UMF_Message
```

#### Route registration

Routes which do not require HydraPy functions can be defined as:

```python
hydra_route('/', ['GET'])
@app.route('/', methods=['GET'])
async def home():
    return 'Sample Service'
```

Note we still call the hydra_route function so that HydraPy will know about this function even if the function itself does not call HydraPy functions. This is required for routing.

Routes that do depend on HydraPy must be declared after HydraPy has been initialized.

```python
hydra = HydraPy(config_path='./config.json', version=service_version, message_handler=hydra_message_handler)
si = await hydra.init()

hydra_route('/v1/sample/health', ['GET'])
@app.route('/v1/sample/health', methods=['GET'])
async def health():
    return {
        'result': hydra.get_health()
    }

await hydra.register_routes()
```


---
## Development

### Build the sample-service
The service can be built as a debug and non-debug container.

#### Debug

```shell
$ cd sample-service
$ ./build-debug.sh
```

#### Non-debug
```shell
$ cd sample-service
$ ./build.sh
```

### Start the support cluster
```shell
$ cd docker
$ ./startup.sh
```

### Web interfaces
HydraRouter: http://localhost:5353
RedisInsight: http://localhost:8001

