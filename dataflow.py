import time
from datetime import datetime
import pandas as pd
from app.dataflow import timescore, webscore, user, devicescore, pcscore
from kafka import KafkaConsumer
import json

def process_line(line):
    # Initial parsing
    parts = line.strip().split(",")
    if len(parts) != 5:
        return None
        
    json_msg = {
        "id": parts[0],
        "time": parts[1],
        "user_id": parts[2][5:],  # Remove 'user_' prefix
        "pc": parts[3],
        "activity": parts[4].strip(),
    }

    # Processing pipeline
    try:
        json_msg = get_role(json_msg)
        json_msg = score_time(json_msg)
        json_msg = score_activity(json_msg)
        json_msg = score_pc(json_msg)
        json_msg = sum_score(json_msg)
    except Exception as e:
        print(f"Error processing line: {e}")
        return None

    return json_msg

def get_role(json_msg):
    json_msg["role"] = user.get_role_from_uid(json_msg["user_id"])
    return json_msg

def score_time(json_msg):
    json_msg["time_score"] = timescore.score(json_msg["time"])
    return json_msg

def score_activity(json_msg):
    activity = json_msg["activity"]
    if activity.startswith("http"):
        json_msg["activity_score"] = webscore.score(activity)
    elif activity == "Connect":
        json_msg["activity_score"] = devicescore.score(json_msg["role"])
    else:
        json_msg["activity_score"] = 0
    return json_msg

def score_pc(json_msg):
    json_msg["pc_score"] = pcscore.score(
        json_msg["user_id"], 
        json_msg["pc"], 
        json_msg["role"]
    )
    return json_msg

def sum_score(json_msg):
    json_msg["score"] = (
        json_msg["time_score"] + 
        json_msg["activity_score"] + 
        json_msg["pc_score"]
    )
    return json_msg

if __name__ == "__main__":
    results = []
    with open("sample.csv", "r") as f:
        # Skip header if exists
        next(f)
        
        for line in f:
            result = process_line(line)
            if result and result.get("score", 0) > 2.5:
                results.append(result)

    output_file = "output.json"
    with open(output_file, "w") as out_f:
        json.dump(results, out_f, indent=4)
    
    # Kafka consumer setup
    topic_name = "insider-threat-topic"
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="insider-threat-group",
        value_deserializer=lambda x: x.decode("utf-8"),
    )

    print("Listening for Kafka messages...")
    for message in consumer:
        line = message.value
        result = process_line(line)
        if result and result.get("score", 0) > 2.5:
            results.append(result)
            print(f"Processed Kafka message: {result}")
    
    with open(output_file, "w") as out_f:
        json.dump(results, out_f, indent=4)
