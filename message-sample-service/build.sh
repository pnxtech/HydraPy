# Syntax: ./build.sh 0.1.1
# Use --no-cache=true  when necessary
cp ../hydrapy/hydra.py .
docker build -t message-sample-service:$1 .
