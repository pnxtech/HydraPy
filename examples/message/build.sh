# Syntax: ./build.sh
# Use --no-cache=true  when necessary
cp -R ../../hydrapy .
VERSION_TAG=$(<VERSION)
docker build -t message:$VERSION_TAG .
