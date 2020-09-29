# Syntax: ./build.sh
# Use --no-cache=true  when necessary
cp ../hydrapy/hydra.py .
VERSION_TAG=$(<VERSION)
docker build -t hydrapy-sample-service:$VERSION_TAG .
