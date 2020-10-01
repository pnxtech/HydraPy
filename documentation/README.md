# Documentation

## About this repo
This repo has the following features and goals:

* Official project repo for ongoing work on Hydra-Py
* Example of how to launch a containerized docker cluster of microservices
* An environment where Hydra-Py can be debugged and tested

So outside the hosting of Hydra-Py development, this repo offers practical examples of how Hydra-Py can be used to created containerized Python-based microservices.

## Backstory
The Hydra approach was first presented at the [2006 EmpireNode conference](https://www.youtube.com/watch?v=j_yVf9Blcjo) in New York City where Hydra for NodeJS was open sourced.

The following describes the approach:

* [Building light-weight microservices using Redis](https://medium.com/hydramicroservices/building-light-weight-microservices-using-redis-dc5b3bca741
)
* [RedisConf 2018 presentation](https://www.youtube.com/watch?v=z25CPqJMFUk)

[![Building light-weight microservices using Redis](http://img.youtube.com/vi/z25CPqJMFUk/0.jpg)](https://www.youtube.com/watch?v=z25CPqJMFUk "Building light-weight microservices using Redis")

## Installation
Hydra-Py is available via pypi:
https://pypi.org/project/hydra-py/

#### Import

```python
from Hydra-Py import Hydra-Py, hydra_route, UMF_Message
```

#### Initialization
Hydra-Py has a pre-initilization phase via its constructor and then when ready, an application can invoke the actual init via the `init` call.

```python
hydra = HydraPy(
    config_path='./config.json',
    version=service_version,
    message_handler=hydra_message_handler)
si = await hydra.init()
```

The first parameter to the constructor is a path to a configuration file in JSON format.

The `init()` call returns a dictionary containing useful information such as the instance ID of the current microservice, as well as the IP address and network port.

Sample config.json file:

```js
{
    "hydra": {
        "serviceName": "sample",
        "serviceIP": "",
        "servicePort": 15000,
        "serviceType": "example",
        "serviceDescription": "A HydraPy sample service",
        "redis": {
            "host": "redis",
            "port": 6379,
            "database": 15
        }
    }
}
```


#### Async ready
Like Hydra for NodeJS, Hydra-Py is built using async I/O.   As such, it works best with other asyncio compatible libraries.  In the case of application servers, Hydra-Py currently favors the use of [Quart](https://pgjones.gitlab.io/quart/) as shown in the demo projects found in the [examples](./examples) folder in this repo.

#### Use with Quart

**Route registration**

Routes which do not require Hydra-Py functions can be defined as:

```python
hydra_route('/', ['GET'])
@app.route('/', methods=['GET'])
async def home():
    return 'Sample Service'
```

Note we still call the hydra_route function so that Hydra-Py will know about this function even if the function itself does not call Hydra-Py functions. This is required for routing.

Routes that do depend on Hydra-Py must be declared after Hydra-Py has been initialized.

```python
hydra = Hydra-Py(config_path='./config.json', version=service_version, message_handler=hydra_message_handler)
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

