import streamlit as st
import pickle
import pandas as pd
import requests


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

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    # 4. FIX: Create 5 columns to match your 5 recommendations
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])