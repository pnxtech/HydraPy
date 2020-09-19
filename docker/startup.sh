export STACK_NAME='hydrapy-cluster'
export HOSTIP=`echo "show State:/Network/Global/IPv4" | scutil | grep PrimaryInterface | awk '{print $3}' | xargs ifconfig | grep inet | grep -v inet6 | awk '{print $2}'`
echo "Binding ${STACK_NAME} to ${HOSTIP}"
docker stack deploy --compose-file cluster-compose.yml ${STACK_NAME}
