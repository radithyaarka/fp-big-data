#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.ml.feature import CountVectorizer, RegexTokenizer, StopWordsRemover
from pyspark.sql.functions import concat_ws
from sklearn.metrics.pairwise import cosine_similarity
from pyspark.sql.functions import split
import numpy as np
import pickle
import os

# Create a SparkSession
spark = SparkSession.builder.getOrCreate()
# Get the SparkContext from the SparkSession
sc = spark.sparkContext
# Set the MinIO access key, secret key, endpoint, and other configurations
sc._jsc.hadoopConfiguration().set("fs.s3a.access.key", "minio_access_key")
sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key", "minio_secret_key")
sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint", "http://localhost:9000")
sc._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
sc._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "false")
sc._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
sc._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "false")

# Read batched data from S3 bucket
movies_df = spark.read.csv("s3a://movies/*.csv", header=True, inferSchema=True)

# Explore the data
movies_df.show(10)
movies_df.describe().show()
movies_df.printSchema()
print(movies_df.columns)

# Handle missing values
movies_df = movies_df.dropna()

# Feature engineering
movies_df = movies_df.select("id", "title", "overview", "genre")

# Tokenize the text data
tokenizer = RegexTokenizer(inputCol="overview", outputCol="words", pattern="\\W")
movies_df = tokenizer.transform(movies_df)

# Remove stop words
remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
movies_df = remover.transform(movies_df)

# Concatenate overview and genres
movies_df = movies_df.withColumn("tags", concat_ws(" ", movies_df["filtered_words"], movies_df["genre"]))
# Convert the "tags" column to an array of strings
movies_df = movies_df.withColumn("tags", split(movies_df["tags"], " "))
movies_df = movies_df.drop("overview", "genre", "words", "filtered_words")

# Create feature vectors using CountVectorizer
cv = CountVectorizer(inputCol="tags", outputCol="features", vocabSize=10000, minDF=2)
model = cv.fit(movies_df)
movies_df = model.transform(movies_df)

# Convert Spark DataFrame to Pandas DataFrame for sklearn compatibility
pandas_df = movies_df.select("id", "title", "features").toPandas()

# Convert the features column to a NumPy array
features_array = np.array(pandas_df['features'].tolist())

# Compute cosine similarity
cosine_sim = cosine_similarity(features_array)

# Create a function to get movie recommendations based on cosine similarity
def get_recommendations(title, cosine_sim=cosine_sim):
    # Get the index of the movie that matches the title
    idx = pandas_df[pandas_df['title'] == title].index[0]

    # Get the pairwise similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores[1:11]  # Exclude the first one as it is the movie itself

    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]

    # Return the top 10 most similar movies
    return pandas_df.iloc[movie_indices]

# Example usage
recommended_movies = get_recommendations("Iron Man")  # Replace with an actual movie title
print(recommended_movies)

# Save the model and other artifacts
pickle.dump(pandas_df, open("movies_list.pkl", "wb"))
pickle.dump(cosine_sim, open("similarity.pkl", "wb"))