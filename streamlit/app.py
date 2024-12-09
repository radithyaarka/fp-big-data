import streamlit as st
import pandas as pd
from kafka import KafkaConsumer
import json
from minio import Minio
from datetime import datetime
import io
import time

# Initialize MinIO client
minio_client = Minio(
    "minio:9000",
    access_key="minio_access_key",
    secret_key="minio_secret_key",
    secure=False
)

# Initialize Kafka consumer
consumer = KafkaConsumer(
    'movies-topic',
    bootstrap_servers=['kafka:29092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Initialize session state
if 'movies' not in st.session_state:
    st.session_state.movies = []
    st.session_state.last_save_time = time.time()

def save_to_minio(data_list):
    df = pd.DataFrame(data_list)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    # Create a unique filename with timestamp
    filename = f"streamed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Save to MinIO
    minio_client.put_object(
        "movies",
        filename,
        io.BytesIO(csv_buffer.getvalue().encode()),
        len(csv_buffer.getvalue())
    )
    st.success(f"Saved batch to MinIO: {filename}")

# Streamlit app
st.title('Movie Stream Analysis')

# Create columns for metrics
col1, col2, col3 = st.columns(3)

# Initialize placeholder for the chart
chart_placeholder = st.empty()

# Initialize row for metrics
metrics_row = st.empty()

# Main loop
for message in consumer:
    movie = message.value
    
    # Add movie to session state
    st.session_state.movies.append(movie)
    
    # Check if 2 minutes have passed since last save
    current_time = time.time()
    if current_time - st.session_state.last_save_time >= 120:  # 120 seconds = 2 minutes
        if st.session_state.movies:  # Only save if there's data
            save_to_minio(st.session_state.movies)
            st.session_state.last_save_time = current_time
    
    # Update metrics
    with metrics_row.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Movies Streamed", len(st.session_state.movies))
        with col2:
            avg_rating = sum(float(m['vote_average']) for m in st.session_state.movies) / len(st.session_state.movies)
            st.metric("Average Rating", f"{avg_rating:.2f}")
        with col3:
            avg_votes = sum(int(m['vote_count']) for m in st.session_state.movies) / len(st.session_state.movies)
            st.metric("Average Votes", f"{avg_votes:.0f}")
    
    # Update chart
    df = pd.DataFrame(st.session_state.movies)
    chart_placeholder.line_chart(df['vote_average'])