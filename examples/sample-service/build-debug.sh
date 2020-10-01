# Syntax: ./build-debug.sh
# Use --no-cache=true  when necessary
cp -R ../../hydrapy .
VERSION_TAG=$(<VERSION)
docker build -f Dockerfile.debug -t hydrapy-sample-service:$VERSION_TAG .
