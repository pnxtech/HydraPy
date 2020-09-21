![](./assets/hydrapy-logo.png)
# HydraPy
Hydra for Python

Note: HydraPy requires Python 3.7+ and aioredis==1.3.1 or greater

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

