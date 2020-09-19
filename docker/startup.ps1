$STACK_NAME='hydrapy-cluster'
$HOSTIP=ipconfig | Select-String -Pattern "IPv4"
$HOSTIP=($HOSTIP[0] -Split ":")[1].trim()
echo "Host IP: $HOSTIP"
docker stack deploy --compose-file cluster-compose.yml $STACK_NAME
