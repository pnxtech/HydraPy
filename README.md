![](./assets/hydrapy-logo.png)
# HydraPy
Hydra for Python

```diff
- NOTE THIS PROJECT IS IN VERY EARLY DEVELOPMENT
* HydraPy requires Python 3.7+ and aioredis==1.3.1 or greater
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

## Development

### Build the sample-service
The service can be built as a debug and non-debug container.

#### Debug

```shell
$ cd sample-service
$ ./build-debug.sh 1.0.0
```

#### Non-debug
```shell
$ cd sample-service
$ ./build.sh 1.0.0
```

### Start the support cluster
```shell
$ cd docker
$ ./startup.sh
```

### Web interfaces
HydraRouter: http://localhost:5353
RedisInsight: http://localhost:8001

