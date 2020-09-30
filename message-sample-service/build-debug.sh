# Syntax: ./build-debug.sh
# Use --no-cache=true  when necessary
cp ../hydrapy/hydra.py .
VERSION_TAG=$(<VERSION)
docker build -f Dockerfile.debug -t message-sample-service:$VERSION_TAG .