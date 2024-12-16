import os
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Get absolute paths
VENV_PATH = os.path.abspath("venv_kafka/Scripts/python.exe")
STREAMLIT_PATH = os.path.abspath("venv_kafka/Scripts/streamlit.exe")

class ModelFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.pkl'):
            print(f"New model detected: {event.src_path}")
            restart_streamlit_app()

def run_producer():
    print("Starting Kafka producer...")
    command = f'"{VENV_PATH}" streamlit/producer.py'
    os.system(command)

def run_streamlit():
    print("Starting Streamlit dashboard...")
    command = f'"{STREAMLIT_PATH}" run streamlit/app.py'
    os.system(command)

def run_spark():
    print("Running Spark processing...")
    command = f'"{VENV_PATH}" spark.py'
    os.system(command)

def restart_streamlit_app():
    print("Restarting web application...")
    command = f'"{STREAMLIT_PATH}" run app.py'
    os.system(command)

def monitor_pkl_files():
    event_handler = ModelFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path='./', recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def schedule_spark():
    while True:
        run_spark()
        time.sleep(300)  # Wait 5 minutes

if __name__ == "__main__":
    # Verify paths exist
    if not os.path.exists(VENV_PATH):
        raise Exception(f"Python interpreter not found at {VENV_PATH}")
    if not os.path.exists(STREAMLIT_PATH):
        raise Exception(f"Streamlit not found at {STREAMLIT_PATH}")

    print("Starting all services...")
    print(f"Using Python from: {VENV_PATH}")
    print(f"Using Streamlit from: {STREAMLIT_PATH}")
    
    # Start threads
    producer_thread = threading.Thread(target=run_producer)
    streamlit_thread = threading.Thread(target=run_streamlit)
    spark_thread = threading.Thread(target=schedule_spark)
    pkl_monitor_thread = threading.Thread(target=monitor_pkl_files)

    producer_thread.start()
    streamlit_thread.start()
    spark_thread.start()
    pkl_monitor_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down all services...")