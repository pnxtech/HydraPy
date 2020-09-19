# Syntax: ./build.sh 0.1.1
docker build --no-cache=true -t hydrapy-sample-service:$1 .

