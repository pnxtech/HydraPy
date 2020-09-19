# Syntax: ./build.sh 0.1.1
# Use --no-cache=true  when necessary
cp ../src/hydra.py .
docker build -t hydrapy-sample-service:$1 .
