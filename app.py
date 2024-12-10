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

def load_existing_titles_from_minio():
    """Load all existing movie titles from MinIO files"""
    existing_titles = set()
    try:
        objects = minio_client.list_objects('movies')
        for obj in objects:
            try:
                data = minio_client.get_object('movies', obj.object_name)
                df = pd.read_csv(io.BytesIO(data.read()))
                existing_titles.update(df['title'].unique())
            except Exception as e:
                continue
        return existing_titles
    except Exception as e:
        return set()

# Initialize session state
if 'movies' not in st.session_state:
    st.session_state.movies = []
    st.session_state.last_save_time = time.time()
    st.session_state.processed_titles = load_existing_titles_from_minio()

def save_to_minio(data_list):
    df = pd.DataFrame(data_list).drop_duplicates(subset=['title'])
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    filename = f"streamed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
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
try:
    for message in consumer:
        movie = message.value
        movie_title = movie.get('title', '')
        
        if movie_title not in st.session_state.processed_titles:
            st.session_state.movies.append(movie)
            st.session_state.processed_titles.add(movie_title)
            
            current_time = time.time()
            if current_time - st.session_state.last_save_time >= 60:
                if st.session_state.movies:
                    save_to_minio(st.session_state.movies)
                    st.session_state.last_save_time = current_time
                    st.session_state.movies = []
            
            # Update metrics
            with metrics_row.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Unique Movies", len(st.session_state.processed_titles))
                with col2:
                    if st.session_state.movies:
                        avg_rating = sum(float(m['vote_average']) for m in st.session_state.movies) / len(st.session_state.movies)
                        st.metric("Average Rating (Current Batch)", f"{avg_rating:.2f}")
                with col3:
                    if st.session_state.movies:
                        avg_votes = sum(int(m['vote_count']) for m in st.session_state.movies) / len(st.session_state.movies)
                        st.metric("Average Votes (Current Batch)", f"{avg_votes:.0f}")
            
            # Update chart for current batch
            if st.session_state.movies:
                df = pd.DataFrame(st.session_state.movies)
                chart_placeholder.line_chart(df['vote_average'])

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    
finally:
    if st.session_state.movies:
        save_to_minio(st.session_state.movies)