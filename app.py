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


def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=98d38df69b8f66e1b16e9f207c51a8a6"
    data = requests.get(url).json()

    # Standardizing the data we want to show
    details = {
        "poster": "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', ''),
        "title": data.get('original_title', 'N/A'),
        "overview": data.get('overview', 'No description available.'),
        "release_date": data.get('release_date', 'Unknown'),
        "rating": data.get('vote_average', 'N/A'),
        "genres": [g['name'] for g in data.get('genres', [])]
    }
    return details


@st.dialog("Movie Information")
def show_details(tmdb_id):
    info = fetch_movie_details(tmdb_id)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(info['poster'])
    with col2:
        st.subheader(info['title'])
        st.write(f"**Release Date:** {info['release_date']}")
        st.write(f"**Rating:** ⭐ {info['rating']}/10")
        st.write(f"**Genres:** {', '.join(info['genres'])}")
        st.write("---")
        st.write(info['overview'])

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


if st.button('Recommend'):
    with st.spinner('Searching for similar movies...'):
        # We need the IDs to fetch details later
        movie_indices = sorted(list(enumerate(similarity[movies[movies['title'] == selected_movie_name].index[0]])),
                               reverse=True, key=lambda x: x[1])[1:6]

    cols = st.columns(5)
    for i, m_info in enumerate(movie_indices):
        tmdb_id = movies.iloc[m_info[0]].movie_id
        name = movies.iloc[m_info[0]].title
        poster = fetch_poster(tmdb_id)

        with cols[i]:
            st.image(poster)
            st.caption(name)
            # This button triggers the popup
            if st.button("Details", key=f"btn_{tmdb_id}"):
                show_details(tmdb_id)
# Load data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movies['title'].values
)




if st.button('Recommend'):
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


