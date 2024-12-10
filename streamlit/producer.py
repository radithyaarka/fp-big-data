from kafka import KafkaProducer
import json
import time
import pandas as pd
from datetime import datetime

def json_serializer(data):
    return json.dumps(data).encode('utf-8')

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=json_serializer
)

# Read the CSV file
df = pd.read_csv('dataset.csv')

# Stream each row with an interval
def stream_data():
    for index, row in df.iterrows():
        data = row.to_dict()
        producer.send('movies-topic', data)
        print(f"Sent: {data['title']}")
        time.sleep(2)  # Stream every 2 seconds

if __name__ == "__main__":
    stream_data()