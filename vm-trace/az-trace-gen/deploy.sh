mvn clean install
scp ./target/az-trace-gen-1.0-SNAPSHOT-jar-with-dependencies.jar $USER@$HOST:$WORKPLACE/trace-gen.jar
scp ./src/main/resources/configs.properties $USER@$HOST:$WORKPLACE/configs.properties
scp ./openrc.sh $USER@$HOST:$WORKPLACE/openrc.sh
scp ./remote-exec-debug.sh $USER@$HOST:$WORKPLACE/remote-exec-debug.sh

scp ./src/main/resources/os-client/image-list.sh $USER@$HOST:$WORKPLACE/image-list.sh
