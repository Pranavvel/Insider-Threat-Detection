@echo off
cd /d C:\kafka_2.13-2.8.1

echo Starting Zookeeper...
start "Zookeeper" cmd /k bin\windows\zookeeper-server-start.bat config\zookeeper.properties

timeout /t 5

echo Starting Kafka Broker...
start "Kafka Broker" cmd /k bin\windows\kafka-server-start.bat config\server.properties

timeout /t 10

echo Checking if 'vm-logs' exists...
bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092 | findstr vm-logs > nul

if %errorlevel% neq 0 (
    echo Creating Kafka Topic: vm-logs
    bin\windows\kafka-topics.bat --create --topic vm-logs --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
) else (
    echo Topic 'vm-logs' already exists. Skipping creation.
)

