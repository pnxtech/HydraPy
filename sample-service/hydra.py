"""
HydraPy: Hydra for Python
"""
class Hydra:
    service_version = '0.0.0'
    redis = None
    config = None

    def __init__(self, redis, config, service_version):
        self.redis = redis
        self.config = config
        self.service_version = service_version

    def version(self):
        print(self.service_version)
