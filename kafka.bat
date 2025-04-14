@echo off
cd /d C:\kafka_2.13-2.8.1

echo Starting Zookeeper...
start "Zookeeper" cmd /k bin\windows\zookeeper-server-start.bat config\zookeeper.properties

timeout /t 10

echo Starting Kafka Broker...
start "Kafka Broker" cmd /k bin\windows\kafka-server-start.bat config\server.properties

timeout /t 15

echo Verifying Kafka Broker is running...
bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092

echo Deleting existing Kafka Topic: vm-logs (if it exists)...
bin\windows\kafka-topics.bat --delete --topic vm-logs --bootstrap-server localhost:9092

timeout /t 10

echo Creating Kafka Topic: vm-logs
bin\windows\kafka-topics.bat --create --topic vm-logs --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

echo Verifying Kafka Topic: vm-logs was created...
bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092 | find "vm-logs"
if %errorlevel% neq 0 (
    echo Failed to create Kafka Topic: vm-logs
    exit /b 1
) else (
    echo Kafka Topic: vm-logs created successfully
)

