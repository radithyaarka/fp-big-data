from flask import Flask, render_template, request, jsonify
import pickle
import requests

app = Flask(__name__, template_folder='frontend')

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US"
    try:
        data = requests.get(url).json()
        poster_path = data.get('poster_path', None)
        poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750.png?text=No+Image"
        rating = data.get('vote_average', 'N/A')
        
        # Fetch IMDB ID
        imdb_id = data.get('imdb_id', '')
        return poster_url, rating, imdb_id
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750.png?text=Error+Fetching+Image", 'N/A', ''

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

@app.route('/recommend', methods=['GET'])
def recommend():
    movie = request.args.get('movie')
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return jsonify({"error": "Movie not found!"})

    # Fetch details for the searched movie
    searched_movie_id = movies.iloc[index].id
    searched_movie_poster, _, searched_movie_imdb = fetch_movie_details(searched_movie_id)

    # Fetch recommendations
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    recommend_movie = []
    recommend_poster = []
    recommend_rating = []
    recommend_imdb = []

    for i in distance[1:11]:
        movie_id = movies.iloc[i[0]].id
        poster_url, rating, imdb_id = fetch_movie_details(movie_id)
        
        recommend_movie.append(movies.iloc[i[0]].title)
        recommend_poster.append(poster_url)
        recommend_rating.append(rating)
        recommend_imdb.append(imdb_id)

    return jsonify({
        "movie": movie,
        "poster": searched_movie_poster,
        "imdb_id": searched_movie_imdb,
        "movies": recommend_movie,
        "posters": recommend_poster,
        "ratings": recommend_rating,
        "imdb_ids": recommend_imdb
    })

if __name__ == "__main__":
    app.run(debug=True)