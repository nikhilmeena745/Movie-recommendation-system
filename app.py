import streamlit as st
import pickle
import pandas as pd
import requests

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🍿",
    layout="wide"
)


# 1. FIX: The function must wrap the logic and use quotes for the URL
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=98d38df69b8f66e1b16e9f207c51a8a6".format(movie_id)
    response = requests.get(url)
    data = response.json()
    # Adding a leading slash if missing is handled by TMDB, but this is the standard path:
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        # 2. FIX: Get the ACTUAL TMDB ID from your dataframe, not the loop index
        # Double check if your column is named 'movie_id' or 'id'
        tmdb_id = movies.iloc[i[0]].movie_id

        recommended_movies.append(movies.iloc[i[0]].title)
        # 3. FIX: Removed the space in the function call
        recommended_movies_posters.append(fetch_poster(tmdb_id))
    return recommended_movies, recommended_movies_posters


# Load data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movies['title'].values
)




if st.sidebar.button('Recommend'):
    # This creates the loading animation
    with st.spinner('Searching for similar movies...'):
        names, posters = recommend(selected_movie_name)

    # Once the logic finishes, the spinner disappears and columns appear
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            # Use caption for titles to keep them neat, or stick with text
            st.caption(names[i])
            st.image(posters[i])
            st.write(f"🔥 {90 - i * 2}% Match")


