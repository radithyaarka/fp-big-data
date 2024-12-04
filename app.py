from flask import Flask, render_template, request, jsonify
import pickle
import requests

app = Flask(__name__, template_folder='frontend')

# Function to fetch movie poster
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US"
    try:
        data = requests.get(url).json()
        poster_path = data.get('poster_path', None)
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/500x750.png?text=No+Image"
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750.png?text=Error+Fetching+Image"

# Function to fetch movie ratings
def fetch_rating(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US"
    try:
        data = requests.get(url).json()
        rating = data.get('vote_average', 'N/A')
        return rating
    except requests.exceptions.RequestException:
        return 'N/A'

# Load movie data and similarity matrix
try:
    movies = pickle.load(open("movies_list.pkl", 'rb'))
    similarity = pickle.load(open("similarity.pkl", 'rb'))
except FileNotFoundError:
    print("Files not found. Please check the files.")
    exit()

movies_list = movies['title'].values

@app.route('/')
def home():
    return render_template('index.html', movies=movies_list)

@app.route('/recommend', methods=['GET'])  # Ganti menjadi GET jika menggunakan JS
def recommend():
    movie = request.args.get('movie')  # Gunakan request.args.get() jika menggunakan GET
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return jsonify({"error": "Movie not found!"})

    # Fetch details for the searched movie
    searched_movie_id = movies.iloc[index].id
    searched_movie_poster = fetch_poster(searched_movie_id)

    # Fetch recommendations
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    recommend_movie = []
    recommend_poster = []
    recommend_rating = []

    for i in distance[1:11]:  # Get top 10 recommendations
        movie_id = movies.iloc[i[0]].id
        recommend_movie.append(movies.iloc[i[0]].title)
        recommend_poster.append(fetch_poster(movie_id))
        recommend_rating.append(fetch_rating(movie_id))

    return jsonify({
        "movie": movie,  # Title of the searched movie
        "poster": searched_movie_poster,  # Poster URL of the searched movie
        "movies": recommend_movie,
        "posters": recommend_poster,
        "ratings": recommend_rating
    })

if __name__ == "__main__":
    app.run(debug=True)
