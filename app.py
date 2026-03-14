import streamlit as st
import pickle
import pandas as pd
import requests

# 1. DEFINE FUNCTIONS FIRST
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=98d38df69b8f66e1b16e9f207c51a8a6"
    data = requests.get(url).json()
    return "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', '')

@st.dialog("Movie Information")
def show_details(tmdb_id):
    # (Your existing show_details code here)
    st.write("Fetching details...")

# 2. LOAD DATA (This must happen before the UI uses 'movies')
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# 3. SETUP UI
st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movies['title'].values
)

# 4. BUTTON LOGIC (Now all variables exist!)
if st.button('Get Recommendations'):
    with st.spinner('Searching for similar movies...'):
        # Match the movie index
        movie_index = movies[movies['title'] == selected_movie_name].index[0]
        distances = similarity[movie_index]
        movie_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    cols = st.columns(5)
    for i, m_info in enumerate(movie_indices):
        idx = m_info[0]
        tmdb_id = movies.iloc[idx].movie_id
        name = movies.iloc[idx].title
        poster = fetch_poster(tmdb_id)

        with cols[i]:
            st.image(poster)
            st.caption(name)
            if st.button("Details", key=f"btn_{tmdb_id}"):
                show_details(tmdb_id)