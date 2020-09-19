# Syntax: ./build-debug.sh 0.1.1
# Use --no-cache=true  when necessary
cp ../src/hydra.py .
docker build -f Dockerfile.debug -t hydrapy-sample-service:$1 .
