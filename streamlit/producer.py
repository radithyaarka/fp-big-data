from kafka import KafkaProducer
import json
import time
import pandas as pd
from datetime import datetime
import os

def json_serializer(data):
    return json.dumps(data).encode('utf-8')

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=json_serializer
)

# Get the current script's directory and read the CSV file with correct path
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, 'dataset.csv')

# Print the path being used
print(f"Attempting to read CSV from: {csv_path}")

# Read the CSV file
df = pd.read_csv(csv_path)

# Keep track of processed records in memory
processed_records = set()
total_processed = 0
total_skipped = 0

# Stream each row with duplicate prevention and counting
def stream_data():
    global total_processed, total_skipped
    
    # Print available columns
    print("Available columns in CSV:", df.columns.tolist())
    print(f"Total records in CSV: {len(df)}")
    
    for index, row in df.iterrows():
        data = row.to_dict()
        
        # Create a unique identifier using just the title
        record_id = str(data.get('title', ''))
        
        if record_id not in processed_records:
            producer.send('movies-topic', data)
            processed_records.add(record_id)
            total_processed += 1
            print(f"Sent ({total_processed}): {data['title']}")
            time.sleep(0.5)
        else:
            total_skipped += 1
            print(f"Skipped duplicate ({total_skipped}): {data['title']}")
    
    print("\nFinal Statistics:")
    print(f"Total records processed: {total_processed}")
    print(f"Total duplicates skipped: {total_skipped}")
    print(f"Total records handled: {total_processed + total_skipped}")

if __name__ == "__main__":
    try:
        stream_data()
    except FileNotFoundError:
        print(f"Error: Could not find dataset.csv at {csv_path}")
        print(f"Current working directory: {os.getcwd()}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")