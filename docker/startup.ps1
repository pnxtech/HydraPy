$STACK_NAME='hydrapy-cluster'
$HOSTIP=ipconfig | Select-String -Pattern "IPv4"
$HOSTIP=($HOSTIP[0] -Split ":")[1].trim()
echo "Host IP: $HOSTIP"
docker stack deploy --compose-file cluster-compose.yml $STACK_NAME
docker run -d -v redisinsight:/db -p 8001:8001 --rm --name redisinsight redislabs/redisinsight:latest
