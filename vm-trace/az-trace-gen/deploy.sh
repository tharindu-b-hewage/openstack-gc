mvn clean install
scp ./target/az-trace-gen-1.0-SNAPSHOT-jar-with-dependencies.jar $USER@$HOST:$WORKPLACE/trace-gen.jar
scp ./src/main/resources/configs.properties $USER@$HOST:$WORKPLACE/configs.properties