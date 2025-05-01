# from flask import Flask, request, render_template
# import pandas as pd
# import numpy as np
# import requests
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# app = Flask(__name__)

# # Load and prepare your movie dataset
# df = pd.read_csv("movie_dataset.csv")
# features = ['keywords','cast','genres','director']
# for feature in features:
#     df[feature] = df[feature].fillna('')
# df["combined_features"] = df.apply(lambda row: row['keywords']+" "+row['cast']+" "+row['genres']+" "+row['director'], axis=1)
# cv = CountVectorizer()
# count_matrix = cv.fit_transform(df["combined_features"])
# cosine_sim = cosine_similarity(count_matrix)

# # Helper Functions
# def get_title_from_index(index):
#     return df[df.index == index]["title"].values[0]

# def get_index_from_title(title):
#     return df[df.title == title]["index"].values[0]

# def search_movie_api(search):
#     url = f"http://www.omdbapi.com/?s={search}&apikey=24b81528"
#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return {"error": "Failed to fetch"}

# @app.route('/', methods=['GET'])
# def home():
#     return render_template('index.html')  # Your HTML file should be named index.html

# @app.route('/recommend', methods=['POST'])
# def recommend():
#     movie_name = request.form['movie_name']
#     try:
#         movie_index = get_index_from_title(movie_name)
#         similar_movies = list(enumerate(cosine_sim[movie_index]))
#         sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)[1:6]

#         movies = []
#         for element in sorted_similar_movies:
#             movie_title = get_title_from_index(element[0])
#             movie_data = search_movie_api(movie_title)
#             movies.append(movie_data)

#         return {"recommendations": movies}
#     except Exception as e:
#         return {"error": str(e)}

# if __name__ == "__main__":
#     app.run(debug=True)
""" This is the Whole Working Code

Just Upload the Dataset and the adjust the path of the Dataset and then run the code  """





from flask import Flask, render_template_string, request
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
from pyngrok import ngrok

# Step 1: Set up Flask app
app = Flask(__name__)

# Step 2: Set Ngrok auth token and start tunnel
public_url = ngrok.connect(5000)
print(" * Ngrok Tunnel URL:", public_url)

# Step 3: Load dataset
df = pd.read_csv("/content/sample_data/movie_dataset.csv")
features = ['keywords', 'cast', 'genres', 'director']
for feature in features:
    df[feature] = df[feature].fillna('')
df["combined_features"] = df.apply(lambda row: row['keywords']+" "+row['cast']+" "+row['genres']+" "+row['director'], axis=1)

# Step 4: Create similarity matrix
cv = CountVectorizer()
count_matrix = cv.fit_transform(df["combined_features"])
cosine_sim = cosine_similarity(count_matrix)

# Step 5: Helper functions
def get_title_from_index(index):
    """Return the movie title based on the given index"""
    return df.loc[index]["title"]

def get_index_from_title(title):
    """Return the index of the movie based on the title (case-insensitive)"""
    title = title.strip().lower()  # Strip and lower-case the input title
    matching_rows = df[df.title.str.lower() == title]  # Case-insensitive match
    if not matching_rows.empty:
        return matching_rows.index[0]
    return None

def search_movie_from_omdb(search):
    """Fetch movie details from OMDB API"""
    url = f"http://www.omdbapi.com/?t={search}&apikey=24b81528" 
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('Response') == 'True':
            return {
                'title': data.get('Title'),
                'year': data.get('Year'),
                'genre': data.get('Genre'),
                'plot': data.get('Plot'),
                'poster': data.get('Poster')
            }
    return None

# Step 6: HTML Template
html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Movie Recommender</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Inter', sans-serif;
      margin: 0;
      padding: 2rem;
      background: #f4f4f9;
      color: #333;
    }

    h2, h3 {
      color: #222;
    }

    form {
      margin-bottom: 2rem;
      display: flex;
      gap: 1rem;
      align-items: center;
    }

    input[type="text"] {
      padding: 0.75rem;
      font-size: 1rem;
      width: 300px;
      border: 1px solid #ccc;
      border-radius: 8px;
    }

    input[type="submit"] {
      padding: 0.75rem 1.5rem;
      background-color: #4f46e5;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
      transition: background-color 0.3s;
    }

    input[type="submit"]:hover {
      background-color: #3730a3;
    }

    ul {
      list-style: none;
      padding: 0;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 2rem;
    }

    li {
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      padding: 1rem;
      transition: transform 0.2s ease;
    }

    li:hover {
      transform: translateY(-5px);
    }

    img {
      width: 100%;
      border-radius: 8px;
      margin-top: 0.5rem;
    }

    p {
      font-size: 0.95rem;
      margin-top: 0.5rem;
      color: #555;
    }

    @media (max-width: 600px) {
      input[type="text"] {
        width: 100%;
      }
      form {
        flex-direction: column;
        align-items: stretch;
      }
    }
  </style>
</head>
<body>
  <h2>🎬 Movie Recommender</h2>
  <form method="post">
    <input name="movie_name" type="text" placeholder="Enter movie name..." required>
    <input type="submit" value="Recommend">
  </form>

  {% if movies %}
    <h3>Recommended Movies</h3>
    <ul>
      {% for movie in movies %}
        <li>
          <h4>{{ movie.title }} ({{ movie.year }})</h4>
          <p>{{ movie.plot }}</p>
          <img src="{{ movie.poster }}" alt="Poster of {{ movie.title }}">
        </li>
      {% endfor %}
    </ul>
  {% endif %}
</body>
</html>

"""

# Step 7: Flask route
@app.route('/', methods=['GET', 'POST'])
def home():
    movies = []
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        try:
            # Step 1: Get index from title (find the index of the given movie)
            movie_index = get_index_from_title(movie_name)
            if movie_index is not None:
                # Step 2: Get similar movies based on the cosine similarity
                similar_movies = list(enumerate(cosine_sim[movie_index]))
                sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)[1:6]

                # Step 3: Fetch movie details from OMDB API for each similar movie
                for element in sorted_similar_movies:
                    movie_title = get_title_from_index(element[0])
                    movie_details = search_movie_from_omdb(movie_title)
                    if movie_details:
                        movies.append(movie_details)
            else:
                # If movie is not found in the dataset, fetch from OMDB directly
                movie_details = search_movie_from_omdb(movie_name)
                if movie_details:
                    movies.append(movie_details)
                else:
                    movies.append({'title': f"Error: Movie '{movie_name}' not found in OMDB API."})

        except Exception as e:
            movies.append({'title': f"Error: {str(e)}"})
    return render_template_string(html, movies=movies)

# Step 8: Run the app
if __name__ == '__main__':
    app.run()
