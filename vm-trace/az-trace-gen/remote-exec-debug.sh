source ./openrc.sh
echo $OS_AUTH_URL
echo $OS_USERNAME
echo $OS_PASSWORD
sudo chmod +x ./*.sh
java -agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=127.0.0.1:8000 -jar trace-gen.jar ./configs.properties